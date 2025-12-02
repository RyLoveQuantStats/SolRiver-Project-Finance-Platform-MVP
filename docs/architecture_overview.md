# Architecture Overview

## Current MVP

- **Database**: SQLite (`db/solriver_mvp.db`)
- **Access layer**: `src/database.py` using SQLAlchemy
- **Core model**: `src/model.py`
- **Reporting**: `src/report.py`
- **Sensitivity**: `src/sensitivity.py`
- **Config**: `config/settings.yaml`

## Migration to managed Postgres (e.g. AWS RDS)

1. Provision a Postgres instance (RDS).  
2. Create the same tables (`projects`, `financing`, `proforma_results`).  
3. Update the DB URL (e.g. `postgresql+psycopg2://user:pass@host:5432/dbname`) in:
   - `config/settings.yaml`, or  
   - environment variable `DB_URL`  

4. Reuse the same Python modules without code changes to the model logic.

## Future extensions

- Scheduled ETL/model runs (Cron/Lambda/Batch)  
- S3 for raw data, reports, dashboards  
- BI/dashboard layer (Power BI)

The code is organized specifically so the database and compute layers are cleanly separated.
