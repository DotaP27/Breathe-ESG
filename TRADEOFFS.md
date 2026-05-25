TRADEOFFS — prototype choices

- No real-time SAP API integration: we accept flat files to avoid credential and mapping complexity.
- No external emission-factor APIs: use a curated, local set to avoid dependency and licensing risk.
- No enterprise SSO/OAuth: SimpleJWT + Django auth suffice for the demo.

Future: optional ML anomaly detection, PDF parsing, currency normalization, and richer factor sources.
