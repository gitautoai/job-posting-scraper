from typing import Any

from scripts.google.read_from_sheets import read_from_sheets
from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
def write_to_sheets(service: Any, spreadsheet_id: str, jobs: list[dict[str, Any]]):
    # Get existing jobs
    existing_jobs = read_from_sheets(service, spreadsheet_id)

    # Exclude duplicates based on job_post_id
    existing_ids = {job["job_post_id"] for job in existing_jobs}
    new_jobs = [job for job in jobs if job["job_post_id"] not in existing_ids]

    if not new_jobs:
        return  # No new data, exit

    headers = [
        "job_post_id",
        "job_post_title",
        "job_post_url",
        "job_post_location",
        "company_name",
        "company_linkedin_url",
        "job_search_keyword",
        "job_post_source",
        "created_at",
    ]

    # Add headers only if sheet is empty
    values = ([headers] if not existing_jobs else []) + [
        [
            job["job_post_id"],
            job["job_post_title"],
            job["job_post_url"],
            job["job_post_location"],
            job["company_name"],
            job["company_linkedin_url"],
            job["job_search_keyword"],
            job["job_post_source"],
            job["created_at"],
        ]
        for job in new_jobs
    ]

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="QA Engineer!A:I",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()
