/*
Vault scaffolding: folder tree, bundled documents, token substitution, the
QM-04 applicability table, and per-SOP applicability callouts.

The pipeline is idempotent: missing files are written from the bundle,
existing files are only token-substituted and (for QM-04 and affected SOPs)
have their applicability rows/callouts re-derived from the config. Existing
content is never overwritten wholesale, so running the wizard on a clone of
the template repository, or re-running it with changed answers, is safe.
*/
import { App, normalizePath } from "obsidian";
import { ClauseExclusion, QmsConfig } from "./config";
import { buildTokenMap, deriveActivities, substituteTokens } from "./tokens";
import {
  BUNDLED_CONFIG_FILES,
  BUNDLED_DOCS,
  RECORD_SUBDIRS,
  VAULT_FOLDERS,
} from "./generated/templates";

/* The seven conditional rows of QM-04's applicability table, keyed by the
   clause cell, with the scope flag that drives each and a factual default
   justification offered when the clause is excluded. */
export interface ConditionalClause {
  clause: string;
  scopeKey: keyof Pick<
    QmsConfig["scope"],
    | "contamination_control"
    | "design"
    | "process_validation"
    | "sterilisation"
    | "customer_property"
    | "special_preservation"
    | "measuring_equipment"
  >;
  defaultJustification: string;
}

export const CONDITIONAL_CLAUSES: ConditionalClause[] = [
  {
    clause: "6.4",
    scopeKey: "contamination_control",
    defaultJustification:
      "No special work environment or contamination control conditions are required for the devices.",
  },
  {
    clause: "7.3",
    scopeKey: "design",
    defaultJustification: "The organisation does not perform design and development of medical devices.",
  },
  {
    clause: "7.5.6",
    scopeKey: "process_validation",
    defaultJustification:
      "No production processes require validation; all process outputs are verified by subsequent monitoring or measurement.",
  },
  {
    clause: "7.5.7",
    scopeKey: "sterilisation",
    defaultJustification: "No sterile devices are manufactured or supplied; sterilisation is not performed.",
  },
  {
    clause: "7.5.10",
    scopeKey: "customer_property",
    defaultJustification: "The organisation does not hold or use customer property.",
  },
  {
    clause: "7.5.11",
    scopeKey: "special_preservation",
    defaultJustification:
      "The devices require no special preservation conditions beyond standard storage and packaging.",
  },
  {
    clause: "7.6",
    scopeKey: "measuring_equipment",
    defaultJustification: "No monitoring or measuring equipment is used that affects product conformity.",
  },
];

/* SOPs that are wholly driven by an excludable clause. When the clause is
   excluded, the SOP is still created (ISO 13485 section 1.2 exclusions are
   documented, not hidden) but carries an applicability callout. */
const SOP_APPLICABILITY: { pathContains: string; clause: string }[] = [
  { pathContains: "SOP-07", clause: "7.3" },
  { pathContains: "SOP-11", clause: "7.6" },
];

const QM04_PATH = "01-quality-manual/QM-04 Scope and Exclusions.md";
const APPLICABILITY_MARKER = "> **Applicability.**";

export function deriveExclusions(config: QmsConfig): Record<string, ClauseExclusion> {
  const out: Record<string, ClauseExclusion> = {};
  for (const row of CONDITIONAL_CLAUSES) {
    const applicable = config.scope[row.scopeKey];
    const stored = config.clause_exclusions[row.clause];
    out[row.clause] = {
      applicable,
      justification: applicable
        ? ""
        : (stored && !stored.applicable && stored.justification.trim()) || row.defaultJustification,
    };
  }
  return out;
}

/* Rewrite the Applicable?/Justification cells of QM-04's conditional rows.
   Rows are located by their first cell; the fixed "Yes" rows are never
   touched. Returns null when the table cannot be recognised. */
export function rewriteQm04Table(text: string, exclusions: Record<string, ClauseExclusion>): string | null {
  const lines = text.split("\n");
  let rowsFound = 0;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.startsWith("|")) continue;
    const cells = line.split("|");
    if (cells.length < 6) continue;
    const clause = cells[1].trim();
    const exclusion = exclusions[clause];
    if (!exclusion) continue;
    rowsFound++;
    cells[3] = exclusion.applicable ? " Yes " : " N/A ";
    cells[4] = exclusion.applicable ? " " : ` ${exclusion.justification} `;
    lines[i] = cells.join("|");
  }
  if (rowsFound !== Object.keys(exclusions).length) return null;
  return lines.join("\n");
}

/* Insert, update, or remove the applicability callout below a SOP's scope
   note (or below the Effective Date line when no scope note exists). */
export function applyApplicabilityCallout(text: string, excluded: boolean, justification: string): string {
  const lines = text.split("\n");
  const calloutLine =
    `${APPLICABILITY_MARKER} This clause is recorded as not applicable in ` +
    `[[QM-04 Scope and Exclusions]] with justification: ${justification} ` +
    `This document is retained as a controlled placeholder; review the exclusion if the activity begins.`;

  const existing = lines.findIndex((l) => l.startsWith(APPLICABILITY_MARKER));
  if (!excluded) {
    if (existing >= 0) {
      // Remove the callout and one adjacent blank line.
      lines.splice(existing, 1);
      if (existing < lines.length && lines[existing] === "" && existing > 0 && lines[existing - 1] === "") {
        lines.splice(existing, 1);
      }
    }
    return lines.join("\n");
  }
  if (existing >= 0) {
    lines[existing] = calloutLine;
    return lines.join("\n");
  }
  let anchor = lines.findIndex((l) => l.startsWith("> **Scope note.**"));
  if (anchor < 0) anchor = lines.findIndex((l) => l.startsWith("**Effective Date:**"));
  if (anchor < 0) return text;
  lines.splice(anchor + 1, 0, "", calloutLine);
  return lines.join("\n");
}

export interface ScaffoldReport {
  foldersCreated: string[];
  docsCreated: string[];
  docsUpdated: string[];
  configFilesWritten: string[];
  warnings: string[];
}

async function ensureFolder(app: App, path: string, report: ScaffoldReport): Promise<void> {
  const p = normalizePath(path);
  if (!(await app.vault.adapter.exists(p))) {
    await app.vault.adapter.mkdir(p);
    report.foldersCreated.push(p);
  }
}

export async function scaffoldVault(app: App, config: QmsConfig): Promise<ScaffoldReport> {
  const report: ScaffoldReport = {
    foldersCreated: [],
    docsCreated: [],
    docsUpdated: [],
    configFilesWritten: [],
    warnings: [],
  };

  const derivedConfig: QmsConfig = {
    ...config,
    company: { ...config.company, activities: deriveActivities(config) },
  };
  const tokens = buildTokenMap(derivedConfig);
  const exclusions = deriveExclusions(derivedConfig);

  for (const folder of VAULT_FOLDERS) {
    await ensureFolder(app, folder, report);
  }
  for (const sub of RECORD_SUBDIRS) {
    await ensureFolder(app, `05-records/${sub}`, report);
  }

  await ensureFolder(app, ".obsidian", report);
  for (const file of BUNDLED_CONFIG_FILES) {
    const p = normalizePath(file.path);
    if (!(await app.vault.adapter.exists(p))) {
      await app.vault.adapter.write(p, file.content);
      report.configFilesWritten.push(p);
    }
  }

  for (const doc of BUNDLED_DOCS) {
    const p = normalizePath(doc.path);
    const exists = await app.vault.adapter.exists(p);
    let text = exists ? await app.vault.adapter.read(p) : doc.content;
    const original = exists ? text : null;

    text = substituteTokens(text, tokens);

    if (doc.path === QM04_PATH) {
      const rewritten = rewriteQm04Table(text, exclusions);
      if (rewritten === null) {
        report.warnings.push(
          "QM-04 applicability table was not recognised and has not been modified; update it manually.",
        );
      } else {
        text = rewritten;
      }
    }

    for (const sop of SOP_APPLICABILITY) {
      if (doc.path.includes(sop.pathContains)) {
        const exclusion = exclusions[sop.clause];
        text = applyApplicabilityCallout(text, !exclusion.applicable, exclusion.justification);
      }
    }

    if (!exists) {
      await app.vault.adapter.write(p, text);
      report.docsCreated.push(p);
    } else if (text !== original) {
      await app.vault.adapter.write(p, text);
      report.docsUpdated.push(p);
    }
  }

  return report;
}
