from celery import Celery
from celery.schedules import crontab
from config import settings
import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

app = Celery(
    "jobly",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

app.conf.task_serializer     = "json"
app.conf.result_serializer   = "json"
app.conf.accept_content      = ["json"]
app.conf.task_track_started  = True
app.conf.timezone            = "UTC"
app.conf.enable_utc          = True

app.conf.beat_schedule = {
    # Core autopilot loop — fires every 6 hours
    "scrape-all-autopilot-users": {
        "task": "workers.scrape_tasks.scrape_for_all_autopilot_users",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    # Reset applied_today counter at midnight UTC
    "reset-daily-stats": {
        "task": "workers.scrape_tasks.reset_daily_stats",
        "schedule": crontab(minute=0, hour=0),
    },
}
