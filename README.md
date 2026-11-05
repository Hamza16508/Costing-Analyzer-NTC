# Costing-Analyzer-NTC: raw-material costing analyzer

Status: **Phase 1 (databank built, Gate 1)**. See `docs/phase1/gate1-report.md`.

The analyzer is a **separate, new artifact**. The existing Causal Identifier artifact is read only and is never updated by this project.

- `docs/phase0/po-knowledge.md` and `config/po_knowledge.json` hold the company PO knowledge from the commercial specialist.
- `docs/phase0/questionnaire/` holds the PO questionnaire for the commercial specialist (DOCX to fill in, PDF to read).
- `docs/phase0/sources.md` lists every source and the reserved slots for company-licensed platforms.
- `docs/phase0/` holds the Gate 0 design: six JSON Schemas, PO mapping, decisions and v1 method, storage adapter, Causal Identifier mapping, source coverage, and the gate report.
- `scripts/` holds the Phase 0 check scripts and the Phase 1 fetch and build scripts (`build_db.py` builds the artifact database docs into `out/db/`).
- `analyzer/` holds the PO loader, factor source fetchers and the coverage and base-month logic; `artifact/index.html` is the analyzer page.

Credentials for login sources go in a git-ignored `.env` (never committed).
