import re

from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
def clean_job_title(job_title: str):
    if not job_title:
        raise ValueError("Job title is required")

    # Convert to string and strip whitespace
    job_title = str(job_title).strip()

    # 1. Remove content in parentheses
    # .*? is a non-greedy match, meaning it will match the shortest possible string
    # Ex1-1: QA Automation Engineer (SDET) -> QA Automation Engineer
    # Ex1-2: SDET (SDET in Test) -> SDET
    # Ex1-3: QA Automation Engineer (434831) -> QA Automation Engineer
    job_title = re.sub(r"\(.*?\)", "", job_title)

    # 2. Remove content in square brackets
    # Ex2-1: QA Automation Engineer [SDET] -> QA Automation Engineer
    job_title = re.sub(r"\[.*?\]", "", job_title)

    # 3. Handle vertical bars (| or ||) - remove everything after
    # Ex3-1: Test & Reliability Engineer | Software Testing -> Test & Reliability Engineer
    # Ex3-2: Mobile Test Automation Engineer || W2 role -> Mobile Test Automation Engineer
    job_title = re.sub(r"\s*\|+.*", "", job_title)

    # 4. Handle hyphens - only remove if surrounded by spaces
    # Ex4-1: Senior SDET - Javascript -> Senior SDET
    # Ex4-2: Software Test Engineer - Mid-Level - TGC -> Software Test Engineer
    # Ex4-3: Vehicle-to-Cloud Integration and Automation Engineer -> Vehicle-to-Cloud Integration and Automation Engineer
    # Ex4-4: Software Test Engineer-Top Secret Cleared -> Software Test Engineer-Top Secret Cleared
    job_title = re.sub(r"\s+-\s+.*", "", job_title)

    # 5. Handle commas followed by experience requirements
    # Ex5-1: Quality Engineer, 2+ Years of Experience -> Quality Engineer
    job_title = re.sub(r",\s*\d+\+?\s*[Yy]ears?.*", "", job_title)
    job_title = re.sub(r",\s*[Ee]xperienced?.*", "", job_title)

    # Clean up any remaining multiple spaces
    job_title = re.sub(r"\s+", " ", job_title).strip()

    return job_title
