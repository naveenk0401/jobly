from workers.celery_app import app

@app.task(bind=True, max_retries=2, default_retry_delay=30)
def apply_to_job(self, application_id: str):
    """
    STUB — full implementation Day 5.
    Receives an application_id, fetches job + user +
    resume from MongoDB, runs Playwright bot,
    updates status, sends Gmail notification.
    """
    print(
        f"[Apply STUB] application {application_id} "
        f"queued — bot wired Day 5"
    )
