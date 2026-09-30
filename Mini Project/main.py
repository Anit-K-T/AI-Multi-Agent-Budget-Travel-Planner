"""Run the multi-agent travel planner from a normal Python file."""

import argparse

from agents.manager import run_pipeline
from utils import pretty_json


DEFAULT_REQUEST = (
    "Plan a 3-day weekend trip from Mumbai to Singapore for a college student on a "
    "strict backpacker budget. Prioritize free or cheap activities, affordable stays, "
    "food, city views, and cultural sites. Avoid red-eye flights."
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-agent travel planner")
    parser.add_argument("--request", default=DEFAULT_REQUEST)
    parser.add_argument("--show-trace", action="store_true")
    args = parser.parse_args()

    print("Running manager, workers, critic, and revision...\n")
    result = run_pipeline(args.request)

    print("FINAL TRAVEL PLAN\n")
    print(pretty_json(result["final_output"]))

    if args.show_trace:
        print("\nFULL PIPELINE TRACE\n")
        print(pretty_json(result))


if __name__ == "__main__":
    main()
