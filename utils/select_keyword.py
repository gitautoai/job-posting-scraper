#!/usr/bin/env python3
import json
import os
import sys
import datetime

from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
def select_keyword(event_name: str | None = None):
    """
    Select a keyword based on various criteria:
    - For manual runs (workflow_dispatch): Use the first keyword
    - For scheduled runs: Select based on current hour
    """
    # Load keywords from JSON file
    with open("keywords.json", "r", encoding="utf-8") as keyword_file:
        keywords: list[str] = json.load(keyword_file)

    # For manual runs use the first keyword
    selected_keyword = keywords[0]
    if event_name == "workflow_dispatch":
        return selected_keyword

    # For scheduled runs, calculate based on time
    hour = datetime.datetime.now(datetime.UTC).hour
    run_interval = 24 // len(keywords)

    # Select keyword based on current time
    index = hour // run_interval
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
