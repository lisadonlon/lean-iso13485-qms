/*
Line-preserving frontmatter editing.

The Python validator and the Dataview dashboards depend on the exact 18-line
frontmatter layout, including blank-capable fields (`effective_date:`) and the
quoted revision string (`revision: "1.0"`). Obsidian's processFrontMatter
re-serialises the YAML block and does not preserve that layout, so this module
edits the raw lines instead: each field keeps its own line, order is never
changed, and only the value portion after `key:` is rewritten.
*/

export interface FrontmatterBlock {
  /* Index of the opening fence line (always 0 when present). */
  start: number;
  /* Index of the closing fence line. */
  end: number;
  lines: string[];
}

export function parseFrontmatterBlock(text: string): FrontmatterBlock | null {
  const lines = text.split("\n");
  if (lines[0] !== "---") return null;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i] === "---") {
      return { start: 0, end: i, lines };
    }
  }
  return null;
}

/* Return the raw value of a field (text after `key:`, trimmed), or null when
   the field line is absent. A present-but-blank field returns "". */
export function getField(text: string, key: string): string | null {
  const block = parseFrontmatterBlock(text);
  if (!block) return null;
  const prefix = `${key}:`;
  for (let i = block.start + 1; i < block.end; i++) {
    const line = block.lines[i];
    if (line.startsWith(prefix)) {
      return line.slice(prefix.length).trim();
    }
  }
  return null;
}

/* Strip surrounding quotes from a raw scalar value. */
export function unquote(raw: string): string {
  const t = raw.trim();
  if (t.length >= 2 && ((t.startsWith('"') && t.endsWith('"')) || (t.startsWith("'") && t.endsWith("'")))) {
    return t.slice(1, -1);
  }
  return t;
}

/* Set fields in place. Values are written verbatim after `key: ` (caller is
   responsible for quoting, e.g. revision: '"1.1"'). An empty-string value
   produces a blank field (`key:`). Fields not present in the block are left
   alone and reported back so callers can refuse to operate on malformed docs. */
export function setFields(text: string, fields: Record<string, string>): { text: string; missing: string[] } {
  const block = parseFrontmatterBlock(text);
  if (!block) return { text, missing: Object.keys(fields) };
  const remaining = new Set(Object.keys(fields));
  for (let i = block.start + 1; i < block.end; i++) {
    const line = block.lines[i];
    const colon = line.indexOf(":");
    if (colon <= 0) continue;
    const key = line.slice(0, colon);
    if (remaining.has(key)) {
      const value = fields[key];
      block.lines[i] = value === "" ? `${key}:` : `${key}: ${value}`;
      remaining.delete(key);
    }
  }
  return { text: block.lines.join("\n"), missing: [...remaining] };
}

/* Parse an inline YAML array (["a", "b"]) leniently; returns null when the
   raw value is not an inline array. */
export function parseInlineArray(raw: string): string[] | null {
  const t = raw.trim();
  if (!t.startsWith("[") || !t.endsWith("]")) return null;
  const inner = t.slice(1, -1).trim();
  if (!inner) return [];
  return inner.split(",").map((part) => unquote(part.trim()));
}

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

export function isIsoDate(value: string): boolean {
  return DATE_RE.test(value);
}

export function todayIso(): string {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mm}-${dd}`;
}

export function isoToBodyDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

/* effective_date + review_interval months, clamped to the last day of the
   target month (e.g. 31 Jan + 1 month = 28/29 Feb). */
export function addMonthsIso(iso: string, months: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const targetMonthIndex = m - 1 + months;
  const targetYear = y + Math.floor(targetMonthIndex / 12);
  const targetMonth = ((targetMonthIndex % 12) + 12) % 12;
  const lastDay = new Date(targetYear, targetMonth + 1, 0).getDate();
  const day = Math.min(d, lastDay);
  return `${targetYear}-${String(targetMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}
