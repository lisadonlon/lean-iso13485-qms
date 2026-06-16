# Records

Completed record instances live here, one subfolder per category. Create new
records from the matching template in `_templates/`. Records are evidence —
once created they are retained per the master retention schedule in your
Control of Records procedure (SOP-02).

| Subfolder | Contents | Written by |
|---|---|---|
| `audits/` | Internal/supplier/external audit records | Hand (from template) |
| `capa/` | Corrective and preventive action records | Hand (from template) |
| `management-reviews/` | Management review minutes and outputs | Hand (from template) |
| `training/` | Training and competence records | Hand (from template) |
| `complaints/` | Complaint and feedback records | Hand (from template) |
| `changes/` | Change control records | Hand (from template) |
| `software-validation/` | `VAL-YYYY-NN` validation evidence | `scripts/validate_qms.py` only |
| `distribution/` | `DIST-YYYY-NN` distribution manifests | `scripts/export_for_audit.py` only |

Do not hand-edit `software-validation/` or `distribution/` — they are written
by the tooling and form part of the automated audit trail.
