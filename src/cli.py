"""
Simple CLI wrapper for common operations.

Examples:
    python -m src.cli run-model --project-id 1
    python -m src.cli summarize --project-id 1
    python -m src.cli sensitivity --project-id 1
    python -m src.cli all --project-id 1
"""

import argparse

from .model import run_project_model
from .report import write_markdown_summary
from .sensitivity import run_sensitivity


def main():
    parser = argparse.ArgumentParser(description="Project Finance CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: run-model
    run_model_p = subparsers.add_parser(
        "run-model",
        help="Run the project finance model for a single project",
    )
    run_model_p.add_argument(
        "--project-id",
        type=int,
        required=True,
        help="ID of the project to run the model for",
    )

    # Subcommand: summarize
    summarize_p = subparsers.add_parser(
        "summarize",
        help="Generate a Markdown summary for the latest run of a project",
    )
    summarize_p.add_argument(
        "--project-id",
        type=int,
        required=True,
        help="ID of the project to summarize",
    )

    # Subcommand: sensitivity
    sens_p = subparsers.add_parser(
        "sensitivity",
        help="Run sensitivity analysis for a single project",
    )
    sens_p.add_argument(
        "--project-id",
        type=int,
        required=True,
        help="ID of the project to run sensitivity on",
    )

    # Subcommand: all (run model + summary + sensitivity)
    all_p = subparsers.add_parser(
        "all",
        help="Run model, generate summary, and run sensitivity for a single project",
    )
    all_p.add_argument(
        "--project-id",
        type=int,
        required=True,
        help="ID of the project to run the full pipeline for",
    )

    args = parser.parse_args()

    if args.command == "run-model":
        run_project_model(args.project_id)

    elif args.command == "summarize":
        write_markdown_summary(args.project_id)

    elif args.command == "sensitivity":
        run_sensitivity(args.project_id)

    elif args.command == "all":
        # 1) run model
        print(f"[all] Running model for project {args.project_id}...")
        run_project_model(args.project_id)

        # 2) generate summary
        print(f"[all] Generating summary for project {args.project_id}...")
        write_markdown_summary(args.project_id)

        # 3) run sensitivity
        print(f"[all] Running sensitivity for project {args.project_id}...")
        run_sensitivity(args.project_id)

        print(f"[all] Completed full pipeline for project {args.project_id}.")


if __name__ == "__main__":
    main()
