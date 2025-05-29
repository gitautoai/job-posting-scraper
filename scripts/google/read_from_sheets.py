from typing import Any

from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
def read_from_sheets(service: Any, spreadsheet_id: str):

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range="QA Engineer!A:I")
        .execute()
    )

    values = result.get("values", [])
    existing_jobs: list[dict[str, Any]] = []

    if not values or len(values) <= 1:
        return existing_jobs

    headers = values[0]

    for row in values[1:]:
        # Ensure row has all columns
        row_data = row + [""] * (len(headers) - len(row))
        job = dict(zip(headers, row_data))
        existing_jobs.append(job)

    return existing_jobs
