"""
Generate a concise project summary from the latest pro forma results.
"""

import argparse
from pathlib import Path

from sqlalchemy import text

from .database import get_engine


def get_latest_result(project_id: int):
    engine = get_engine()
    with engine.connect() as conn:
        proj = conn.execute(
            text("SELECT * FROM projects WHERE project_id = :pid"),
            {"pid": project_id},
        ).mappings().first()

        if proj is None:
            raise ValueError(f"No project found with project_id={project_id}")

        res = conn.execute(
            text(
                """
                SELECT *
                FROM proforma_results
                WHERE project_id = :pid
                ORDER BY run_date DESC
                LIMIT 1
                """
            ),
            {"pid": project_id},
        ).mappings().first()

        if res is None:
            raise ValueError(f"No pro forma results found for project_id={project_id}")

    return proj, res


def write_markdown_summary(project_id: int, output_dir: Path = Path("reports")) -> Path:
    proj, res = get_latest_result(project_id)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"project_{project_id}_summary.md"

    lines: list[str] = []
    lines.append(f"# {proj['name']} – Investment Summary\n\n")
    lines.append(f"**Run date:** {res['run_date']}\n\n")

    lines.append("## Key Assumptions\n")
    lines.append(f"- Location: {proj['location']}\n")
    lines.append(f"- COD Year: {proj['cod_year']}\n")
    lines.append(f"- Capacity: {proj['capacity_mw']} MW\n")
    lines.append(f"- Capacity Factor (Year 1): {proj['cf_year1']:.2%}\n")
    lines.append(f"- Capex: ${proj['capex']:,.0f}\n")
    lines.append(f"- Opex (Year 1): ${proj['opex_annual']:,.0f} / year\n")
    lines.append(f"- PPA Price: ${proj['ppa_price']:.4f} / kWh\n")
    lines.append(f"- Degradation: {proj['degradation_pct']*100:.2f}% per year\n\n")

    lines.append("## Financial Results\n")
    lines.append(f"- Levered IRR: {res['irr_real']:.2%}\n")
    lines.append(f"- NPV (8% discount): ${res['npv_real']:,.0f}\n")
    if res["payback_year"] is not None:
        lines.append(f"- Simple Payback: Year {int(res['payback_year'])}\n")
    else:
        lines.append("- Simple Payback: N/A\n")
    if res["max_dscr"] is not None:
        lines.append(f"- Min DSCR (loan term): {res['max_dscr']:.2f}\n")

    out_path.write_text("".join(lines), encoding="utf-8")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate latest project finance summary.")
    parser.add_argument("--project-id", type=int, required=True)
    args = parser.parse_args()

    out_path = write_markdown_summary(args.project_id)
    print(f"Summary written to: {out_path}")


if __name__ == "__main__":
    main()
