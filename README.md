# Costing-Analyzer-NTC: raw-material costing analyzer

Status: **Phase 0 (design only)**. No application code yet.

The analyzer is a **separate, new artifact**. The existing Causal Identifier artifact is read only and is never updated by this project.

- `docs/phase0/questionnaire/` holds the PO questionnaire for the commercial specialist (DOCX to fill in, PDF to read).
- `docs/phase0/sources.md` lists every source and the reserved slots for company-licensed platforms.
- `docs/phase0/` holds the Gate 0 design: six JSON Schemas, PO mapping, decisions and v1 method, storage adapter, Causal Identifier mapping, source coverage, and the gate report.
- `scripts/` holds the read-only Phase 0 check scripts used to verify the PO export and the Causal Identifier data.

Credentials for login sources go in a git-ignored `.env` (never committed).
