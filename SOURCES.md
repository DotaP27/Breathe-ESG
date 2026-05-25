SOURCES — quick notes

SAP flat files (IDoc-like)
- Fields: `MENGE`, `MEINS`, `WERKS`, German headers, `YYYYMMDD` dates.
- Map plant codes to locations via tenant-provided lookup for factor selection.
- Parse segments or fallback to delimiter-based parsing.

Utility CSVs
- Fields: account, billing period, meter, reading (kWh/MWh), tariff, amount.
- Normalize units to `kWh`; allocate multi-day bills to calendar months when needed.

Travel (Concur-style CSV)
- Fields: trip, employee, date, origin/dest IATA codes, transport mode, hotel nights, distance.
- If `Distance_km` missing, compute via airport-pair lookup or haversine from lat/lon.
- Keep emission factors configurable (flights, trains, hotels).

References: vendor docs, Concur export guides, SAP community examples.

