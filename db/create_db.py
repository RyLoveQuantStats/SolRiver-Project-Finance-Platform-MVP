#!/usr/bin/env python3
"""
Create and seed a SQLite database for the project finance MVP.
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "solriver_mvp.db"


def create_schema(conn):
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS proforma_results;
        DROP TABLE IF EXISTS financing;
        DROP TABLE IF EXISTS projects;

        CREATE TABLE projects (
            project_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            location        TEXT,
            capacity_mw     REAL NOT NULL,
            capex           REAL NOT NULL,
            opex_annual     REAL NOT NULL,
            ppa_price       REAL NOT NULL,   -- USD/kWh
            degradation_pct REAL NOT NULL,   -- decimal, e.g. 0.005 = 0.5%
            cf_year1        REAL NOT NULL,   -- capacity factor, decimal
            cod_year        INTEGER
        );

        CREATE TABLE financing (
            financing_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      INTEGER NOT NULL,
            tax_credit_pct  REAL NOT NULL,
            debt_pct        REAL NOT NULL,
            interest_rate   REAL NOT NULL,
            term_years      INTEGER NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        );

        CREATE TABLE proforma_results (
            result_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      INTEGER NOT NULL,
            run_date        TEXT NOT NULL,
            npv_real        REAL NOT NULL,
            irr_real        REAL NOT NULL,
            payback_year    REAL,
            max_dscr        REAL,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        );
        """
    )
    conn.commit()


def seed_data(conn):
    cur = conn.cursor()

    projects = [
        # name, location, capacity_mw, capex, opex_annual, ppa_price, degradation_pct, cf_year1, cod_year
        ("Sunny Ridge 5MW", "AZ", 5.0, 4_500_000, 25_000, 0.030, 0.005, 0.20, 2026),
        ("Windy Plains 3MW", "CO", 3.0, 3_600_000, 30_000, 0.040, 0.008, 0.35, 2025),
        ("Desert Bloom 10MW", "TX", 10.0, 8_000_000, 80_000, 0.028, 0.004, 0.22, 2027),
    ]
    cur.executemany(
        """
        INSERT INTO projects (
            name, location, capacity_mw, capex, opex_annual,
            ppa_price, degradation_pct, cf_year1, cod_year
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        projects,
    )

    financings = [
        # project_id, tax_credit_pct, debt_pct, interest_rate, term_years
        (1, 0.30, 0.70, 0.045, 12),
        (2, 0.30, 0.65, 0.050, 10),
        (3, 0.30, 0.65, 0.0475, 12),
    ]
    cur.executemany(
        """
        INSERT INTO financing (
            project_id, tax_credit_pct, debt_pct, interest_rate, term_years
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        financings,
    )

    conn.commit()


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        seed_data(conn)
        print(f"Database created and seeded at {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
