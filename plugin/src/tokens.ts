/*
{{TOKEN}} substitution. Mirrors scripts/init_qms.py: tokens with no usable
value are omitted from the map and therefore left untouched in documents, so
substitution is safe to re-run as the config grows.
*/
import { DEFAULT_ORG, QmsConfig, REGULATORY_ROLE_LABELS } from "./config";

export type TokenMap = Record<string, string>;

export function buildTokenMap(config: QmsConfig): TokenMap {
  const tokens: TokenMap = {};
  const put = (name: string, value: string | undefined | null) => {
    const v = (value ?? "").trim();
    if (v) tokens[name] = v;
  };

  if (config.organisation && config.organisation !== DEFAULT_ORG) {
    put("ORGANISATION_NAME", config.organisation);
  }
  put("QUALITY_MANAGER", config.quality_manager);
  put("COMPANY_REGISTRATION", config.company.registration_number);
  put("REGISTERED_OFFICE", config.company.registered_office);
  put("REGULATORY_ROLE", REGULATORY_ROLE_LABELS[config.company.regulatory_role]);

  const siteParts = config.company.operating_sites
    .filter((s) => s.address.trim())
    .map((s) => (s.activities.trim() ? `${s.address.trim()} (${s.activities.trim()})` : s.address.trim()));
  put("OPERATING_SITES", siteParts.join("; "));
  put("DEVICE_TYPES", config.company.device_types.join(", "));
  put("MARKETS", config.company.markets.join(", "));
  put("QMS_ACTIVITIES", config.company.activities.join(", "));
  return tokens;
}

export function substituteTokens(text: string, tokens: TokenMap): string {
  let out = text;
  for (const [name, value] of Object.entries(tokens)) {
    out = out.split(`{{${name}}}`).join(value);
  }
  return out;
}

/* Derive the QMS activities list from the config for the scope statement.
   Only states activities the user has actually confirmed. */
export function deriveActivities(config: QmsConfig): string[] {
  const activities: string[] = [];
  if (config.scope.design) activities.push("design and development");
  switch (config.company.regulatory_role) {
    case "legal_manufacturer":
    case "own_brand_labeller":
    case "contract_manufacturer":
      activities.push("manufacture");
      break;
    case "distributor":
      activities.push("distribution");
      break;
    case "importer":
      activities.push("import and distribution");
      break;
  }
  if (config.scope.installation) activities.push("installation");
  if (config.scope.servicing) activities.push("servicing");
  return activities;
}
