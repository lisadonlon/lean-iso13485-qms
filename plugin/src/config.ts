/*
qms.config.json handling (schema v2, additive over the Python scripts' four
legacy keys). The file is the durable record of the wizard's answers; documents
are derived from it, never the other way round.
*/
import { App, normalizePath } from "obsidian";

export const CONFIG_PATH = "qms.config.json";
export const DEFAULT_ORG = "Your Organisation Ltd";

export type RegulatoryRole =
  | "legal_manufacturer"
  | "own_brand_labeller"
  | "contract_manufacturer"
  | "distributor"
  | "importer";

export const REGULATORY_ROLE_LABELS: Record<RegulatoryRole, string> = {
  legal_manufacturer: "legal manufacturer",
  own_brand_labeller: "own-brand labeller",
  contract_manufacturer: "contract manufacturer",
  distributor: "distributor",
  importer: "importer",
};

export interface OperatingSite {
  address: string;
  activities: string;
}

export interface CompanyDetails {
  registration_number: string;
  registered_office: string;
  operating_sites: OperatingSite[];
  device_types: string[];
  regulatory_role: RegulatoryRole;
  markets: string[];
  activities: string[];
}

export interface ScopeAnswers {
  design: boolean;
  sterilisation: boolean;
  process_validation: boolean;
  installation: boolean;
  servicing: boolean;
  software_in_product: boolean;
  customer_property: boolean;
  special_preservation: boolean;
  measuring_equipment: boolean;
  contamination_control: boolean;
  outsourced_processes: string[];
  isms_in_scope: boolean;
}

export interface ClauseExclusion {
  applicable: boolean;
  justification: string;
}

export type DocControlMode = "shared-drive" | "git";

export interface QmsConfig {
  organisation: string;
  quality_manager: string;
  standard: string;
  github_repo: string;
  config_version: number;
  doc_control_mode: DocControlMode;
  company: CompanyDetails;
  scope: ScopeAnswers;
  clause_exclusions: Record<string, ClauseExclusion>;
  wizard_completed_at: string;
  wizard_version: number;
}

export function defaultConfig(): QmsConfig {
  return {
    organisation: DEFAULT_ORG,
    quality_manager: "",
    standard: "ISO 13485:2016",
    github_repo: "",
    config_version: 2,
    doc_control_mode: "shared-drive",
    company: {
      registration_number: "",
      registered_office: "",
      operating_sites: [],
      device_types: [],
      regulatory_role: "legal_manufacturer",
      markets: [],
      activities: [],
    },
    scope: {
      design: true,
      sterilisation: false,
      process_validation: true,
      installation: false,
      servicing: false,
      software_in_product: false,
      customer_property: false,
      special_preservation: true,
      measuring_equipment: true,
      contamination_control: false,
      outsourced_processes: [],
      isms_in_scope: false,
    },
    clause_exclusions: {},
    wizard_completed_at: "",
    wizard_version: 1,
  };
}

function isPlainObject(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

/* Deep-merge stored values over defaults; unknown keys from the stored file
   are preserved so this plugin never drops fields other tools have added. */
function deepMerge<T>(base: T, override: unknown): T {
  if (!isPlainObject(override)) return base;
  if (!isPlainObject(base)) return override as T;
  const out: Record<string, unknown> = { ...(base as Record<string, unknown>) };
  for (const [key, value] of Object.entries(override)) {
    const baseValue = out[key];
    if (isPlainObject(baseValue) && isPlainObject(value)) {
      out[key] = deepMerge(baseValue, value);
    } else {
      out[key] = value;
    }
  }
  return out as T;
}

export async function loadConfig(app: App): Promise<QmsConfig> {
  const path = normalizePath(CONFIG_PATH);
  let stored: unknown = {};
  if (await app.vault.adapter.exists(path)) {
    try {
      stored = JSON.parse(await app.vault.adapter.read(path));
    } catch {
      stored = {};
    }
  }
  return deepMerge(defaultConfig(), stored);
}

/* Write with 2-space indent and trailing newline, matching init_qms.py, and
   merging over whatever is currently on disk (never clobbering foreign keys). */
export async function saveConfig(app: App, config: QmsConfig): Promise<void> {
  const path = normalizePath(CONFIG_PATH);
  let onDisk: unknown = {};
  if (await app.vault.adapter.exists(path)) {
    try {
      onDisk = JSON.parse(await app.vault.adapter.read(path));
    } catch {
      onDisk = {};
    }
  }
  const merged = deepMerge(isPlainObject(onDisk) ? (onDisk as object) : {}, config);
  await app.vault.adapter.write(path, JSON.stringify(merged, null, 2) + "\n");
}
