import re

from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
def clean_company_name(company_name: str):
    if not company_name:
        raise ValueError("Company name is required")

    # Convert to string and strip whitespace
    company_name = str(company_name).strip()

    # Define patterns to remove
    # ,? means , or nothing
    # \s* means 0 or more spaces
    # .* means anything after the pattern
    patterns = [
        r",?\s*Inc\.?.*",  # Matches "Inc", "Inc.", ", Inc" and anything after
        r",?\s*LLC\.?.*",  # Matches "LLC", "LLC.", ", LLC" and anything after
        r"\.com.*",  # Matches ".com" and anything after
        r"™.*",  # Matches trademark symbol and anything after
        r"®.*",  # Matches registered symbol and anything after
        r"\(.*\).*",  # Matches "(*)" and anything after
    ]

    # Apply all patterns
    for pattern in patterns:
        company_name = re.sub(pattern, "", company_name, flags=re.IGNORECASE)

    # Clean up any remaining multiple spaces and trim
    company_name = re.sub(r"\s+", " ", company_name).strip()

    return company_name
