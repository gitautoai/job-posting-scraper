#!/usr/bin/env python3
import json
import os
import sys
import datetime


def select_keyword(event_name: str | None = None):
    """
    Select a keyword based on various criteria:
    - For manual runs (workflow_dispatch): Use the first keyword
    - For scheduled runs: Select based on current hour
    """
    # Load keywords from JSON file
    try:
        with open("keywords.json", "r", encoding="utf-8") as keyword_file:
            keywords = json.load(keyword_file)
    except FileNotFoundError:
        # Fallback keywords if file doesn't exist
        keywords = [
            "Test Automation Engineer",
            "QA Engineer",
            "Software QA",
            "Quality Assurance Engineer",
            "SDET",
            "Test Engineer",
        ]
        # Create the file for future use
        with open("keywords.json", "w", encoding="utf-8") as keyword_file:
            json.dump(keywords, keyword_file, indent=2)

    # For manual runs use the first keyword
    if event_name == "workflow_dispatch":
        return keywords[0]

    # For scheduled runs, calculate based on time
    hour = datetime.datetime.now(datetime.UTC).hour
    run_interval = 8  # Run every 8 hours

    # Select keyword based on current time
    index = (hour // run_interval) % len(keywords)
    selected_keyword = keywords[index]

    print(
        f"Selected keyword '{selected_keyword}' (index {index}) based on current hour {hour}"
    )
    return selected_keyword


if __name__ == "__main__":
    # Optional argument for event type
    cli_event_type = sys.argv[1] if len(sys.argv) > 1 else None
    result = select_keyword(cli_event_type)
    print(result)  # Output for direct usage

    # For GitHub Actions, set output variable
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"keyword={result}\n")
