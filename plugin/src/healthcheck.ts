/*
QMS health check: a TypeScript port of the filesystem subset of the 24-check
IQ/OQ/PQ validation in scripts/validate_qms.py. It exists so shared-drive
users get fast feedback inside Obsidian. It does not write VAL records and it
does not perform the git, tag, or Dataview-query checks - the Python
validator remains the authoritative, record-producing validation.
*/
import { App, Modal, normalizePath, TFile } from "obsidian";
import { getField, isIsoDate, parseFrontmatterBlock, parseInlineArray, todayIso, unquote } from "./frontmatter";
import { RECORD_SUBDIRS, VAULT_FOLDERS } from "./generated/templates";

export const FRONTMATTER_FIELDS = [
  "doc_id",
  "title",
  "doc_type",
  "standard",
  "clauses",
  "revision",
  "status",
  "effective_date",
  "review_due",
  "review_interval",
  "author",
  "reviewer",
  "approver",
  "approved_date",
  "change_summary",
  "tags",
  "supersedes",
  "related",
];

const VALID_STATUSES = new Set(["draft", "review", "approved", "obsolete"]);
const CONTROLLED_DOC_FOLDERS = [
  "01-quality-manual",
  "02-procedures",
  "03-work-instructions",
  "04-forms-templates",
  "06-isms",
  "08-references",
];
const DATE_FIELDS = ["effective_date", "review_due", "approved_date"];
const SOFT_DEPENDENCIES = ["dataview", "templater-obsidian"];

export type CheckLevel = "PASS" | "WARN" | "FAIL";

export interface CheckResult {
  id: string;
  name: string;
  level: CheckLevel;
  details: string[];
}

function result(id: string, name: string, failures: string[], warn = false): CheckResult {
  return {
    id,
    name,
    level: failures.length === 0 ? "PASS" : warn ? "WARN" : "FAIL",
    details: failures,
  };
}

async function controlledDocs(app: App): Promise<TFile[]> {
  const files: TFile[] = [];
  for (const f of app.vault.getMarkdownFiles()) {
    if (CONTROLLED_DOC_FOLDERS.some((folder) => f.path.startsWith(folder + "/"))) {
      files.push(f);
    }
  }
  return files.sort((a, b) => a.path.localeCompare(b.path));
}

export async function runHealthCheck(app: App): Promise<CheckResult[]> {
  const results: CheckResult[] = [];

  const missingFolders: string[] = [];
  for (const folder of VAULT_FOLDERS) {
    if (!(await app.vault.adapter.exists(normalizePath(folder)))) missingFolders.push(folder);
  }
  results.push(result("HC-01", "Vault folder structure", missingFolders));

  const missingSubdirs: string[] = [];
  for (const sub of RECORD_SUBDIRS) {
    if (!(await app.vault.adapter.exists(normalizePath(`05-records/${sub}`)))) missingSubdirs.push(sub);
  }
  results.push(result("HC-02", "Record subfolders", missingSubdirs));

  const docs = await controlledDocs(app);
  const texts = new Map<string, string>();
  for (const f of docs) texts.set(f.path, await app.vault.read(f));

  const incomplete: string[] = [];
  for (const f of docs) {
    const text = texts.get(f.path)!;
    if (!parseFrontmatterBlock(text)) {
      incomplete.push(`${f.path}: no frontmatter block`);
      continue;
    }
    const missing = FRONTMATTER_FIELDS.filter((field) => getField(text, field) === null);
    if (missing.length) incomplete.push(`${f.path}: missing ${missing.join(", ")}`);
  }
  results.push(result("HC-03", "Complete 18-field frontmatter", incomplete));

  const idMismatch: string[] = [];
  for (const f of docs) {
    const docId = getField(texts.get(f.path)!, "doc_id");
    if (docId && !f.name.startsWith(docId)) idMismatch.push(`${f.path}: doc_id '${docId}'`);
  }
  results.push(result("HC-04", "doc_id matches filename prefix", idMismatch));

  const badStatus: string[] = [];
  for (const f of docs) {
    const status = getField(texts.get(f.path)!, "status");
    if (status !== null && !VALID_STATUSES.has(status)) badStatus.push(`${f.path}: '${status}'`);
  }
  results.push(result("HC-05", "Status is a valid value", badStatus));

  const badArrays: string[] = [];
  for (const f of docs) {
    const text = texts.get(f.path)!;
    for (const field of ["clauses", "related"]) {
      const raw = getField(text, field);
      if (raw !== null && raw !== "" && parseInlineArray(raw) === null) {
        badArrays.push(`${f.path}: ${field} is not an inline array`);
      }
    }
  }
  results.push(result("HC-06", "clauses/related are arrays", badArrays));

  const badDates: string[] = [];
  for (const f of docs) {
    const text = texts.get(f.path)!;
    for (const field of DATE_FIELDS) {
      const raw = getField(text, field);
      if (raw && !isIsoDate(unquote(raw))) badDates.push(`${f.path}: ${field} '${raw}'`);
    }
  }
  results.push(result("HC-07", "Dates are YYYY-MM-DD", badDates));

  const approvedIncomplete: string[] = [];
  for (const f of docs) {
    const text = texts.get(f.path)!;
    if (getField(text, "status") !== "approved") continue;
    const blank = [...DATE_FIELDS, "approver"].filter((field) => !(getField(text, field) ?? "").trim());
    if (blank.length) approvedIncomplete.push(`${f.path}: blank ${blank.join(", ")}`);
  }
  results.push(result("HC-08", "Approved docs fully populated", approvedIncomplete));

  const overdue: string[] = [];
  const today = todayIso();
  for (const f of docs) {
    const text = texts.get(f.path)!;
    if (getField(text, "status") !== "approved") continue;
    const due = unquote(getField(text, "review_due") ?? "");
    if (due && isIsoDate(due) && due < today) overdue.push(`${f.path}: review was due ${due}`);
  }
  results.push(result("HC-09", "Periodic reviews up to date", overdue, true));

  const unresolved: string[] = [];
  for (const f of docs) {
    const matches = texts.get(f.path)!.match(/\{\{[A-Z_]+\}\}/g);
    if (matches) unresolved.push(`${f.path}: ${[...new Set(matches)].join(", ")}`);
  }
  results.push(result("HC-10", "Personalisation tokens resolved", unresolved, true));

  const enabled: Set<string> =
    ((app as unknown as { plugins?: { enabledPlugins?: Set<string> } }).plugins?.enabledPlugins) ?? new Set();
  const missingDeps = SOFT_DEPENDENCIES.filter((p) => !enabled.has(p));
  results.push(result("HC-11", "Dashboard dependencies enabled (Dataview, Templater)", missingDeps, true));

  return results;
}

export class HealthCheckModal extends Modal {
  private results: CheckResult[];

  constructor(app: App, results: CheckResult[]) {
    super(app);
    this.results = results;
  }

  onOpen(): void {
    const { contentEl } = this;
    const passed = this.results.filter((r) => r.level === "PASS").length;
    contentEl.createEl("h3", { text: `QMS health check - ${passed}/${this.results.length} passed` });
    const box = contentEl.createDiv({ cls: "microqms-healthcheck-result" });
    for (const r of this.results) {
      const line = box.createDiv({ cls: `microqms-check-${r.level.toLowerCase()}` });
      line.setText(`[${r.level}] ${r.id}: ${r.name}`);
      for (const d of r.details.slice(0, 10)) {
        box.createDiv({ text: `    -> ${d}` });
      }
      if (r.details.length > 10) box.createDiv({ text: `    -> and ${r.details.length - 10} more` });
    }
    contentEl.createEl("p", {
      text:
        "This is a quick in-vault check. The full 24-check validation (including git and tag evidence) is " +
        "scripts/validate_qms.py, which also writes the VAL record.",
    });
  }

  onClose(): void {
    this.contentEl.empty();
  }
}
