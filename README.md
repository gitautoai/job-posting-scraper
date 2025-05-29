# Job Posting Scraper

Extract job posting data from LinkedIn and write it to Google Sheets.

## What to do

1. Run `python3.12 -m venv venv` to create a virtual environment.
2. Run `source venv/bin/activate` to activate the virtual environment.
3. Run `pip install -r requirements.txt` to install the dependencies.
4. Run `python -m playwright install chromium` to install the playwright browser.
5. (Optional) Run `pip freeze > requirements.txt` to update the requirements.txt file when you add or remove a dependency.

## How to run the LinkedIn scraper

1. Run `python scripts/linkedin.py` to run the LinkedIn scraper.
2. Run `python scripts/google.py` to write the job data to Google Sheets.
