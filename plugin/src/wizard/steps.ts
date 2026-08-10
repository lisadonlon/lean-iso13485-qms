/*
Wizard step metadata: the scope questions and their mapping to config keys
and QM-04 clauses. Kept as data so the modal, the preview, and the skill
documentation stay in agreement.
*/
import { QmsConfig } from "../config";
import { CONDITIONAL_CLAUSES } from "../scaffold";

export interface ScopeQuestion {
  key: keyof Omit<QmsConfig["scope"], "outsourced_processes">;
  question: string;
  detail: string;
  /* QM-04 clause driven by this answer, when there is one. */
  clause?: string;
}

export const SCOPE_QUESTIONS: ScopeQuestion[] = [
  {
    key: "design",
    question: "Do you design and develop devices?",
    detail: "Clause 7.3. Answer no only if design and development is genuinely not performed.",
    clause: "7.3",
  },
  {
    key: "sterilisation",
    question: "Do you supply sterile devices or perform sterilisation?",
    detail: "Clause 7.5.7, validation of sterilisation processes.",
    clause: "7.5.7",
  },
  {
    key: "process_validation",
    question: "Do any processes need validation because their output cannot be fully verified?",
    detail: "Clause 7.5.6. Sterilisation, welding, and sealing are typical examples.",
    clause: "7.5.6",
  },
  {
    key: "contamination_control",
    question: "Do your devices need a controlled work environment or contamination control?",
    detail: "Clause 6.4, work environment and contamination control.",
    clause: "6.4",
  },
  {
    key: "customer_property",
    question: "Do you hold or use customer property?",
    detail: "Clause 7.5.10. Includes customer-supplied materials, equipment, or confidential information.",
    clause: "7.5.10",
  },
  {
    key: "special_preservation",
    question: "Do your devices need special preservation or storage conditions?",
    detail: "Clause 7.5.11. Cold chain, humidity limits, shelf life, protective packaging.",
    clause: "7.5.11",
  },
  {
    key: "measuring_equipment",
    question: "Does measuring equipment affect product conformity?",
    detail: "Clause 7.6, control of monitoring and measuring equipment (calibration).",
    clause: "7.6",
  },
  {
    key: "installation",
    question: "Do you perform installation activities?",
    detail: "Feeds the QM-04 scope statement and SOP-09.",
  },
  {
    key: "servicing",
    question: "Do you perform servicing activities?",
    detail: "Feeds the QM-04 scope statement and SOP-09.",
  },
  {
    key: "software_in_product",
    question: "Does the device contain software, or is it software?",
    detail: "If yes, IEC 62304 applies alongside ISO 13485; see SOP-07.",
  },
  {
    key: "isms_in_scope",
    question: "Is ISO 27001 (information security) in scope?",
    detail: "Enables the 06-isms area; content is not generated in this version.",
  },
];

export function defaultJustificationFor(clause: string): string {
  return CONDITIONAL_CLAUSES.find((c) => c.clause === clause)?.defaultJustification ?? "";
}

/* Textarea helpers: one entry per line. Sites use "address | activities". */
export function parseLines(value: string): string[] {
  return value
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
}

export function parseSites(value: string): { address: string; activities: string }[] {
  return parseLines(value).map((line) => {
    const [address, ...rest] = line.split("|");
    return { address: address.trim(), activities: rest.join("|").trim() };
  });
}

export function formatSites(sites: { address: string; activities: string }[]): string {
  return sites.map((s) => (s.activities ? `${s.address} | ${s.activities}` : s.address)).join("\n");
}
