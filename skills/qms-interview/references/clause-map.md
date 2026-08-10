# Answer-to-clause-to-document map

How interview answers drive the QM-04 applicability table and the affected
documents. Only Clause 7 requirements may be *excluded* under ISO 13485:2016
section 1.2; clause 6.4 and 7.6 rows are recorded as "not applicable with
justification" when they genuinely do not apply. Never mark a row N/A
without a user-approved justification.

| Config key (scope.*) | QM-04 row | If false | Affected documents |
|---|---|---|---|
| contamination_control | 6.4 | N/A with justification | SOP-05 (work-environment sections stay minimal) |
| design | 7.3 | N/A with justification | SOP-07 carries an applicability callout; QM-01 process table row remains |
| process_validation | 7.5.6 | N/A with justification | SOP-09 validation sections minimal |
| sterilisation | 7.5.7 | N/A with justification | SOP-09; also revisit 7.5.6 (sterilisation always needs validation) |
| customer_property | 7.5.10 | N/A with justification | SOP-09 |
| special_preservation | 7.5.11 | N/A with justification | SOP-09 |
| measuring_equipment | 7.6 | N/A with justification | SOP-11 carries an applicability callout |

Always-applicable rows (4, 5, 6.1-6.3, 7.1, 7.2, 7.4, 7.5.1-7.5.5,
7.5.8-7.5.9, 8, 8.2.3) are never edited to N/A.

Cross-checks to apply before writing the table:

- `sterilisation: true` forces `process_validation: true`.
- `design: false` but the company develops its own device: challenge the
  answer before accepting the exclusion.
- `software_in_product: true`: reference IEC 62304 in SOP-07 drafting and
  keep 7.3 applicable unless design is genuinely external; note software
  validation records live in `05-records/software-validation/` (script-
  written - never write there).

Other answer-to-document routing:

| Answers | Documents to tailor in Phase C |
|---|---|
| Markets, vigilance channels | SOP-16 (per-market reporting), SOP-15 |
| Markets, UDI/traceability | SOP-10 scope note (EU MDR vs US FDA wording) |
| Outsourced processes | SOP-08 (supplier controls, 4.1.5) |
| Installation/servicing | SOP-09 sections; QM-04 scope statement |
| Sites, headcount, roles | QM-01 sections 2 and 8, SOP-04 |
| Device types, intended use | QM-01 section 2, QM-04 section 1, SOP-06 drafting context |
| Standards held | QM-04 section 3 regulatory context |
| ISMS in scope | standard field `both`; 06-isms content is out of scope for this skill version |
