"""
Project finance model.

Reads project and financing data from the database, runs a levered project
finance model, and stores results in the proforma_results table.
"""

import argparse
from datetime import datetime
from math import isclose
from typing import Dict, Any

from sqlalchemy import text

from .database import get_engine, load_config


def npv(rate: float, cashflows: list[float]) -> float:
    return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))


def irr(cashflows: list[float], guess: float = 0.08, tol: float = 1e-6, maxiter: int = 200) -> float:
    """
    Simple Newton-Raphson IRR solver.
    """
    r = guess
    for _ in range(maxiter):
        npv_val = sum(cf / ((1 + r) ** t) for t, cf in enumerate(cashflows))
        d_npv = sum(-t * cf / ((1 + r) ** (t + 1)) for t, cf in enumerate(cashflows))
        if isclose(d_npv, 0.0, abs_tol=1e-12):
            break
        new_r = r - npv_val / d_npv
        if abs(new_r - r) < tol:
            return new_r
        r = new_r
    return r


def loan_schedule(principal: float, rate: float, term_years: int):
    """
    Simple annual amortizing loan schedule.
    """
    term_years = int(term_years)
    balance = principal

    if rate != 0:
        annuity_factor = (rate * (1 + rate) ** term_years) / ((1 + rate) ** term_years - 1)
        payment = principal * annuity_factor
    else:
        payment = principal / term_years

    schedule = []
    for year in range(1, term_years + 1):
        interest = balance * rate
        principal_paid = payment - interest
        balance = max(balance - principal_paid, 0.0)
        schedule.append(
            {
                "year": year,
                "payment": payment,
                "interest": interest,
                "principal": principal_paid,
                "balance": balance,
            }
        )
    return schedule


def compute_project_finance(
    proj: Dict[str, Any],
    fin: Dict[str, Any],
    discount_rate: float,
    tax_rate: float,
    years: int,
    opex_escalation: float,
) -> Dict[str, Any]:
    """
    Core financial logic separated from I/O so it can be reused (sensitivity, APIs, etc.).
    """
    capacity_mw = proj["capacity_mw"]
    cf_year1 = proj["cf_year1"]
    degradation = float(proj["degradation_pct"])
    ppa_price = proj["ppa_price"]  # USD/kWh
    capex = proj["capex"]
    opex_annual = proj["opex_annual"]

    # Base-year production (MWh)
    energy_mwh_year1 = capacity_mw * cf_year1 * 8760.0

    # Capital structure
    debt_pct = fin["debt_pct"]
    debt_principal = capex * debt_pct
    equity = capex - debt_principal

    loan = loan_schedule(debt_principal, fin["interest_rate"], fin["term_years"])

    cashflows = []
    revenues = []
    opex_list = []
    debt_service = []

    for year in range(1, years + 1):
        production_mwh = energy_mwh_year1 * ((1 - degradation) ** (year - 1))
        revenue = production_mwh * 1000.0 * ppa_price

        opex_y = opex_annual * ((1 + opex_escalation) ** (year - 1))

        ds = loan[year - 1]["payment"] if year <= len(loan) else 0.0

        depreciation = capex / years

        taxable_income = revenue - opex_y - depreciation - ds
        tax = max(taxable_income * tax_rate, 0.0)

        after_tax_cf = revenue - opex_y - ds - tax + depreciation

        cashflows.append(after_tax_cf)
        revenues.append(revenue)
        opex_list.append(opex_y)
        debt_service.append(ds)

    series = [-equity] + cashflows

    irr_val = irr(series, guess=0.08)
    npv_val = npv(discount_rate, series)

    # Payback
    cumulative = 0.0
    payback_year = None
    for idx, cf in enumerate(series[1:], start=1):
        cumulative += cf
        if cumulative > 0:
            payback_year = idx
            break

    dscr_values = []
    for i, ds in enumerate(debt_service):
        if ds <= 0:
            continue
        ebitda = revenues[i] - opex_list[i]
        dscr_values.append(ebitda / ds)

    min_dscr = min(dscr_values) if dscr_values else None

    return {
        "irr": irr_val,
        "npv": npv_val,
        "payback_year": payback_year,
        "min_dscr": min_dscr,
    }


def run_project_model(project_id: int) -> Dict[str, Any]:
    """
    Fetch project & financing from DB, run the model, and persist results.
    """
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
        if proj is None:
            raise ValueError(f"No project found with project_id={project_id}")

        fin = conn.execute(
            text("SELECT * FROM financing WHERE project_id = :pid"),
            {"pid": project_id},
        ).mappings().first()
        if fin is None:
            raise ValueError(f"No financing found for project_id={project_id}")

        results = compute_project_finance(
            proj,
            fin,
            discount_rate=discount_rate,
            tax_rate=tax_rate,
            years=years,
            opex_escalation=opex_escalation,
        )

        conn.execute(
            text(
                """
                INSERT INTO proforma_results (
                    project_id, run_date, npv_real, irr_real, payback_year, max_dscr
                )
                VALUES (:pid, :run_date, :npv, :irr, :payback, :dscr)
                """
            ),
            {
                "pid": project_id,
                "run_date": datetime.utcnow().isoformat(),
                "npv": float(results["npv"]),
                "irr": float(results["irr"]),
                "payback": float(results["payback_year"]) if results["payback_year"] is not None else None,
                "dscr": float(results["min_dscr"]) if results["min_dscr"] is not None else None,
            },
        )
        conn.commit()

    return {"project_id": project_id, **results}


def main():
    parser = argparse.ArgumentParser(description="Run project finance model for a project.")
    parser.add_argument("--project-id", type=int, required=True)
    args = parser.parse_args()

    results = run_project_model(args.project_id)
    print("=== Project Finance Results ===")
    print(f"Project ID     : {results['project_id']}")
    print(f"IRR            : {results['irr']:.2%}")
    print(f"NPV @ 8%       : ${results['npv']:,.0f}")
    print(f"Payback (year) : {results['payback_year']}")
    if results["min_dscr"] is not None:
        print(f"Min DSCR       : {results['min_dscr']:.2f}")


if __name__ == "__main__":
    main()
