/*
Document lifecycle: draft -> review -> approved -> obsolete, plus revision
bumps. In shared-drive mode the plugin is the document-control mechanism:
approval populates the three date fields, and superseded or withdrawn
revisions move to _archive/ (this module is the only writer to _archive/).
In git mode approval is a git ceremony; see gitmode.ts.
*/
import { App, Modal, Notice, Setting, TFile, normalizePath } from "obsidian";
import { addMonthsIso, getField, isIsoDate, isoToBodyDate, setFields, todayIso, unquote } from "./frontmatter";

export interface DocInfo {
  docId: string;
  revision: string;
  status: string;
  reviewInterval: number;
}

export async function readDocInfo(app: App, file: TFile): Promise<DocInfo | null> {
  const text = await app.vault.read(file);
  const docId = getField(text, "doc_id");
  const revision = getField(text, "revision");
  const status = getField(text, "status");
  if (!docId || !revision || !status) return null;
  const interval = parseInt(getField(text, "review_interval") ?? "12", 10);
  return {
    docId,
    revision: unquote(revision),
    status,
    reviewInterval: Number.isFinite(interval) && interval > 0 ? interval : 12,
  };
}

function bumpMinor(revision: string): string | null {
  const m = revision.match(/^(\d+)\.(\d+)$/);
  if (!m) return null;
  return `${m[1]}.${parseInt(m[2], 10) + 1}`;
}

function archivePath(file: TFile, docInfo: DocInfo): string {
  const base = file.basename;
  return normalizePath(`_archive/${base} - Rev ${docInfo.revision} (superseded ${todayIso()}).md`);
}

async function updateFile(app: App, file: TFile, fields: Record<string, string>): Promise<boolean> {
  const text = await app.vault.read(file);
  const { text: updated, missing } = setFields(text, fields);
  if (missing.length > 0) {
    new Notice(`Cannot update ${file.name}: missing frontmatter field(s) ${missing.join(", ")}.`);
    return false;
  }
  await app.vault.modify(file, updated);
  return true;
}

export async function submitForReview(app: App, file: TFile, reviewer: string): Promise<void> {
  const info = await readDocInfo(app, file);
  if (!info) {
    new Notice("Not a controlled document (missing doc_id/revision/status frontmatter).");
    return;
  }
  if (info.status !== "draft") {
    new Notice(`${info.docId} is '${info.status}', not 'draft'.`);
    return;
  }
  const ok = await updateFile(app, file, { status: "review", reviewer });
  if (ok) new Notice(`${info.docId} submitted for review.`);
}

export async function approveDocument(app: App, file: TFile, approver: string, effectiveDate: string): Promise<void> {
  const info = await readDocInfo(app, file);
  if (!info) {
    new Notice("Not a controlled document (missing doc_id/revision/status frontmatter).");
    return;
  }
  if (info.status === "approved") {
    new Notice(`${info.docId} is already approved.`);
    return;
  }
  if (info.status === "obsolete") {
    new Notice(`${info.docId} is obsolete and cannot be approved.`);
    return;
  }
  if (!approver.trim()) {
    new Notice("An approver name is required.");
    return;
  }
  if (!isIsoDate(effectiveDate)) {
    new Notice("Effective date must be YYYY-MM-DD.");
    return;
  }
  const reviewDue = addMonthsIso(effectiveDate, info.reviewInterval);
  const ok = await updateFile(app, file, {
    status: "approved",
    approver: approver.trim(),
    approved_date: effectiveDate,
    effective_date: effectiveDate,
    review_due: reviewDue,
  });
  if (ok) new Notice(`${info.docId} approved. Review due ${reviewDue}.`);
}

/* Copy the approved document into _archive/ as an obsolete record, then bump
   the live file to the next draft revision. */
export async function startNewRevision(app: App, file: TFile): Promise<void> {
  const info = await readDocInfo(app, file);
  if (!info) {
    new Notice("Not a controlled document (missing doc_id/revision/status frontmatter).");
    return;
  }
  if (info.status !== "approved") {
    new Notice(`${info.docId} is '${info.status}'; only approved documents are revised this way.`);
    return;
  }
  const newRev = bumpMinor(info.revision);
  if (!newRev) {
    new Notice(`Revision '${info.revision}' is not in x.y form; bump it manually.`);
    return;
  }

  const text = await app.vault.read(file);
  const dest = archivePath(file, info);
  if (await app.vault.adapter.exists(dest)) {
    new Notice(`Archive copy already exists: ${dest}`);
    return;
  }
  const archived = setFields(text, {
    status: "obsolete",
    change_summary: `"Superseded by Rev ${newRev}"`,
  });
  await app.vault.adapter.write(dest, archived.text);

  let updated = setFields(text, {
    revision: `"${newRev}"`,
    status: "draft",
    effective_date: "",
    review_due: "",
    approved_date: "",
    reviewer: "",
    approver: "",
    change_summary: `"Rev ${newRev} draft"`,
    supersedes: `${info.docId}-v${info.revision}`,
  }).text;
  updated = appendRevisionHistoryRow(updated, newRev);
  await app.vault.modify(file, updated);
  new Notice(`${info.docId} bumped to Rev ${newRev} (draft). Previous revision archived.`);
}

export async function markObsolete(app: App, file: TFile): Promise<void> {
  const info = await readDocInfo(app, file);
  if (!info) {
    new Notice("Not a controlled document (missing doc_id/revision/status frontmatter).");
    return;
  }
  const text = await app.vault.read(file);
  const updated = setFields(text, { status: "obsolete" });
  const dest = normalizePath(`_archive/${file.basename} - Rev ${info.revision} (withdrawn ${todayIso()}).md`);
  if (await app.vault.adapter.exists(dest)) {
    new Notice(`Archive copy already exists: ${dest}`);
    return;
  }
  await app.vault.adapter.write(dest, updated.text);
  await app.vault.delete(file);
  new Notice(`${info.docId} marked obsolete and moved to _archive/.`);
}

function appendRevisionHistoryRow(text: string, newRev: string): string {
  const lines = text.split("\n");
  const headerIdx = lines.findIndex((l) => /^\|\s*Rev\s*\|/i.test(l));
  if (headerIdx < 0) return text;
  let last = headerIdx;
  for (let i = headerIdx + 1; i < lines.length && lines[i].startsWith("|"); i++) last = i;
  lines.splice(last + 1, 0, `| ${newRev} | ${isoToBodyDate(todayIso())} |  | [describe the changes] |`);
  return lines.join("\n");
}

/* Small prompt modal used by the approve / submit commands. */
export class FieldPromptModal extends Modal {
  private fields: { name: string; desc?: string; initial: string }[];
  private values: string[];
  private onSubmit: (values: string[]) => void;
  private title: string;

  constructor(
    app: App,
    title: string,
    fields: { name: string; desc?: string; initial: string }[],
    onSubmit: (values: string[]) => void,
  ) {
    super(app);
    this.title = title;
    this.fields = fields;
    this.values = fields.map((f) => f.initial);
    this.onSubmit = onSubmit;
  }

  onOpen(): void {
    const { contentEl } = this;
    contentEl.createEl("h3", { text: this.title });
    this.fields.forEach((f, i) => {
      const s = new Setting(contentEl).setName(f.name);
      if (f.desc) s.setDesc(f.desc);
      s.addText((t) => t.setValue(f.initial).onChange((v) => (this.values[i] = v)));
    });
    new Setting(contentEl).addButton((b) =>
      b
        .setButtonText("Confirm")
        .setCta()
        .onClick(() => {
          this.close();
          this.onSubmit(this.values);
        }),
    );
  }

  onClose(): void {
    this.contentEl.empty();
  }
}

export { todayIso };
