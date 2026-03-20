from workers.celery_app import app

@app.task
def match_new_jobs_for_user(user_id: str, job_ids: list):
    """
    STUB — full implementation on Day 4.
    Called automatically by scrape_company_for_user
    when new jobs are found.
    """
    print(
        f"[Match STUB] {len(job_ids)} jobs "
        f"queued for user {user_id} — wired Day 4"
    )
