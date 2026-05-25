DECISIONS — short list

- SAP input: accept flat-file exports (IDoc-like). Easier for prototype clients.
- Utility data: accept CSV exports (not PDFs). CSVs are common and reliable.
- Travel data: accept Concur-style CSV; derive distances via airport lookup or haversine when missing.
- Normalization: store `quantity_kwh` (kWh-equivalent) and `co2e_kg`. kWh-eq helps cross-source comparisons.
- Auth: Django users + SimpleJWT for API access.
- Storage: Postgres in production; SQLite allowed for local dev.
- Uploads: keep original file per `IngestionBatch` for audit and re-parsing.
