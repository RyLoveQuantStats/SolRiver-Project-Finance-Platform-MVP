# 90-Day Plan (High-Level)

## Days 1–30
- Finalize schema and normalize project/financing tables.
- Implement import scripts for project data from real sources (CSVs, Excel).
- Validate model outputs against sample deals.

## Days 31–60
- Migrate from SQLite to a dev Postgres/RDS instance.
- Introduce environment-based configuration (dev/stage/prod).
- Add automated tests for core model functions (IRR, NPV, DSCR).

## Days 61–90
- Schedule recurring model runs (e.g., nightly).
- Implement basic monitoring/logging for model runs.
- Prototype a simple reporting dashboard connected directly to the database.
