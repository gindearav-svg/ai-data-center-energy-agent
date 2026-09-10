import argparse
import json
from pathlib import Path

from src.energy_agent.queries import (
    compare_all_regions,
    get_region_metrics,
    list_regions,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "energy_intelligence.db"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query the regional energy database."
    )

    query_group = parser.add_mutually_exclusive_group(
        required=True
    )

    query_group.add_argument(
        "--list-regions",
        action="store_true",
        help="List available regions.",
    )

    query_group.add_argument(
        "--region",
        type=str,
        help="Return metrics for one region.",
    )

    query_group.add_argument(
        "--compare-all",
        action="store_true",
        help="Compare every available region.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    if arguments.list_regions:
        regions = list_regions(DATABASE_PATH)

        print("\nAvailable regions")
        print("-----------------")

        for region in regions:
            print(f"- {region}")

    elif arguments.region:
        result = get_region_metrics(
            DATABASE_PATH,
            arguments.region,
        )

        print("\nRegional metrics")
        print("----------------")
        print(json.dumps(result, indent=2))

    elif arguments.compare_all:
        results = compare_all_regions(DATABASE_PATH)

        print("\nRegional SQL comparison")
        print("-----------------------")

        print(
            results.to_string(
                index=False,
                float_format=lambda value: f"{value:,.3f}",
            )
        )


if __name__ == "__main__":
    main()