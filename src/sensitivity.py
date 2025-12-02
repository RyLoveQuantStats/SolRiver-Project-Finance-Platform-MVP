"""
Sensitivity analysis around PPA price, capex, and leverage.

Writes results to reports/sensitivity_project_<id>.csv
"""

import argparse
import csv
from pathlib import Path

from sqlalchemy import text

from .database import get_engine
from .model import compute_project_finance, load_config


def run_sensitivity(project_id: int):
    cfg = load_config() or {}
    model_cfg = cfg.get("model", {})
    discount_rate = model_cfg.get("discount_rate", 0.08)
    tax_rate = model_cfg.get("tax_rate", 0.21)
    years = model_cfg.get("project_life_years", 25)
    opex_escalation = model_cfg.get("opex_escalation", 0.02)

    engine = get_engine()
    with engine.connect() as conn:
        proj = conn.execute(
            text("SELECT * FROM projects WHERE project_id = :pid"),
            {"pid": project_id},
        ).mappings().first()
        fin = conn.execute(
            text("SELECT * FROM financing WHERE project_id = :pid"),
            {"pid": project_id},
        ).mappings().first()

        if proj is None or fin is None:
            raise ValueError(f"Missing project or financing for project_id={project_id}")

        base_ppa = proj["ppa_price"]
        base_capex = proj["capex"]
        base_debt = fin["debt_pct"]

        ppa_mults = [0.90, 0.95, 1.00, 1.05, 1.10]
        capex_mults = [0.90, 1.00, 1.10]
        debt_levels = [max(0.0, base_debt - 0.10), base_debt, min(0.95, base_debt + 0.10)]

        results = []
        for ppa_m in ppa_mults:
            for capex_m in capex_mults:
                for debt_pct in debt_levels:
                    temp_proj = dict(proj)
                    temp_fin = dict(fin)

                    temp_proj["ppa_price"] = base_ppa * ppa_m
                    temp_proj["capex"] = base_capex * capex_m
                    temp_fin["debt_pct"] = debt_pct

                    out = compute_project_finance(
                        temp_proj,
                        temp_fin,
                        discount_rate=discount_rate,
                        tax_rate=tax_rate,
                        years=years,
                        opex_escalation=opex_escalation,
                    )

                    results.append(
                        {
                            "ppa_mult": ppa_m,
                            "capex_mult": capex_m,
                            "debt_pct": debt_pct,
                            "irr": out["irr"],
                            "npv": out["npv"],
                            "payback_year": out["payback_year"],
                            "min_dscr": out["min_dscr"],
                        }
                    )

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"sensitivity_project_{project_id}.csv"

    if results:
        keys = list(results[0].keys())
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in results:
                writer.writerow(r)

    print(f"Sensitivity results written to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Run sensitivity analysis for a project.")
    parser.add_argument("--project-id", type=int, required=True)
    args = parser.parse_args()
    run_sensitivity(args.project_id)


if __name__ == "__main__":
    main()
