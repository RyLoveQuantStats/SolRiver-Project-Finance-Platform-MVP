# Project Finance MVP – Solar Asset Evaluation

This repository contains a minimal but extensible project finance platform for evaluating utility-scale solar projects.

It demonstrates:

- A relational database schema for projects, financing, and pro forma results  
- Python modules to:
  - create and seed a SQLite database  
  - query projects and financing assumptions  
  - run a levered project finance model (IRR, NPV, payback, DSCR)  
  - run basic sensitivity analysis around key assumptions  
  - generate concise, text-based project summaries  

The structure is intentionally designed so it can be migrated to a managed Postgres instance (e.g., AWS RDS) with minimal code changes.

---

## Tech stack

- **Python 3.9+**
- **SQLite** (easily swappable to Postgres/RDS)
- **SQLAlchemy** for database access
- **NumPy / pandas** for numerical and tabular handling

---

## Quick start

From the repository root:

### 1. (Optional) virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
