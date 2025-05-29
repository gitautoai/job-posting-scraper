# pylint: disable=broad-exception-caught
from datetime import datetime
from playwright.async_api import Page
from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
async def search_linkedin_jobs(page: Page, keyword: str = "QA Engineer"):
    results: list[dict[str, str | None]] = []
    processed_ids: set[str] = set()
    no_new_jobs_count = 0

    # Scroll and collect jobs until we have at least 25 unique jobs
    while len(results) < 25:
        # Get current job cards: https://www.linkedin.com/jobs/search/?currentJobId=4220568275&f_T=11227%2C13936%2C4729%2C264%2C661%2C20648%2C1510&geoId=103644278&keywords=Test%20Automation%20Engineer&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE
        job_cards = await page.locator(".job-card-container").all()
        initial_count = len(job_cards)
        print(f"# of job cards: {len(job_cards)}")

        # Process new job cards
        for card in job_cards:
            try:
                job_post_id = await card.get_attribute("data-job-id")

                # Skip if we've already processed this job
                if job_post_id is None or job_post_id in processed_ids:
                    continue
                processed_ids.add(job_post_id)

                title = await card.locator(
                    ".job-card-list__title--link strong"
                ).inner_text()
                company_name = await card.locator(
                    ".artdeco-entity-lockup__subtitle span"
                ).inner_text()
                location = await card.locator(
                    ".job-card-container__metadata-wrapper span[dir='ltr']"
                ).first.inner_text()

                # Click the card to load job details
                await page.wait_for_timeout(1000)
                await card.click()
                await page.wait_for_selector(
                    ".job-details-jobs-unified-top-card__company-name a"
                )

                company_linkedin_url = await page.locator(
                    ".job-details-jobs-unified-top-card__company-name a"
                ).get_attribute("href")
                if company_linkedin_url:
                    company_linkedin_url = company_linkedin_url.split("/life")[0] + "/"

                results.append(
                    {
                        "job_post_id": job_post_id,
                        "job_post_title": title.strip(),
                        "job_post_url": f"https://www.linkedin.com/jobs/view/{job_post_id}",
                        "job_post_location": location.strip(),
                        "company_name": company_name.strip(),
                        "company_linkedin_url": company_linkedin_url,
                        "job_search_keyword": keyword,
                        "job_post_source": "LinkedIn",
                        "created_at": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                print(f"Error processing job card: {e}")
                continue

        print(f"Found {len(job_cards)} job cards")
        print(f"Currently found {len(results)} jobs")

        if len(results) >= 25:
            break

        # Check if we found any new jobs in this iteration
        if len(processed_ids) == initial_count:
            no_new_jobs_count += 1
            if no_new_jobs_count >= 3:  # If no new jobs found after 3 attempts, break
                print("No new jobs found after multiple scroll attempts. Stopping.")
                break
        else:
            no_new_jobs_count = 0

        try:
            # Smooth scroll to load more content
            await page.mouse.wheel(0, 400)  # Increased scroll amount for efficiency
            await page.wait_for_timeout(2000)  # Wait for new content to load

        except Exception as e:
            print(f"Error during scroll: {e}")
            break

    return results[:25]  # Return only first 25 jobs even if we found more
