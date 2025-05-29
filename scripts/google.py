# type: ignore
import os
import pickle
from typing import Any

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_google_sheets_service():
    """Initialize Google Sheets API client using OAuth"""
    creds: Credentials | None = None
    # Read token if it exists
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If token does not exist or is invalid, get new one
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "google-oauth.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        # Save token
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service: Any = build("sheets", "v4", credentials=creds)
    return service


def read_from_sheets(service: Any, spreadsheet_id: str):
    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range="QA Engineer!A:I")
            .execute()
        )

        values = result.get("values", [])
        if not values or len(values) <= 1:  # Empty or only headers
            return []

        headers = values[0]
        existing_jobs = []

        for row in values[1:]:
            # Ensure row has all columns
            row_data = row + [""] * (len(headers) - len(row))
            job = dict(zip(headers, row_data))
            existing_jobs.append(job)

        return existing_jobs
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


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

    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="QA Engineer!A:I",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        ).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise
