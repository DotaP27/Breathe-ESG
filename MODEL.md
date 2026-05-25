## Data model — short summary

Core entities:
- `Tenant`: client isolation and configs.
- `IngestionBatch`: one uploaded file / import run (filename, uploader, timestamps, parsing metadata).
- `EmissionRecord`: one normalized row derived from a source row. Keeps `raw_data` (original JSON) and normalized fields.

Important fields on `EmissionRecord`:
- `tenant`, `source_type` (SAP/UTILITY/TRAVEL), `source_file` (IngestionBatch)
- `raw_data` (JSON) — original row kept for audits
- `quantity_kwh` (Decimal) — normalized energy quantity when applicable
- `co2e_kg` (Decimal) — calculated emissions
- `scope`, `fuel_type`, `measurement_unit`
- `status` (PENDING / APPROVED / FLAGGED / LOCKED), `reviewed_by`, `reviewed_at`, `edit_history`

Design notes:
- Keep `raw_data` to preserve provenance and handle varying source schemas.
- Normalize to kWh-equivalent to enable cross-source comparisons; store `co2e_kg` as the primary emissions metric.
- `IngestionBatch` simplifies traceability, batch rollback, and storing parsing warnings.

Common reviewer operations:
- List pending records: filter by `tenant` + `status=PENDING`.
- Approve/flag records and record `reviewed_by` + `reviewed_at`.

Indexes: add `(tenant, status)` and `source_type` for efficient queries.
