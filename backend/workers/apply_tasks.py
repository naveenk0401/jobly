from workers.celery_app import app
from bots.greenhouse_bot import GreenhouseBot
from bots.lever_bot import LeverBot
from bots.generic_bot import GenericBot
from services.email_service import send_application_email
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from bson import ObjectId
from datetime import datetime
import asyncio, os, tempfile, httpx
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

BOT_MAP = {
    "greenhouse": GreenhouseBot,
    "lever":      LeverBot,
    "workday":    GenericBot,
}

@app.task(bind=True, max_retries=2, default_retry_delay=30)
def apply_to_job(self, application_id: str):
    """
    Full apply bot implementation.

    Steps:
      1. Load application, job, user, resume from MongoDB
      2. Check pause state (user may have paused after queue)
      3. Download resume PDF from Supabase signed URL
         to a temp file
      4. Select correct bot by job source
      5. Run bot → fill form → submit
      6. Update application status in MongoDB
      7. Increment user stats counters
      8. Send Gmail notification email
      9. Clean up temp file

    Retries: max 2 times with 30s delay on failure.
    """
    async def _run():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db     = client[settings.MONGO_DB]

        # Load all required documents
        app_doc = await db.applications.find_one(
            {"_id": ObjectId(application_id)}
        )
        if not app_doc:
            print(f"[Apply] Application {application_id} not found")
            client.close()
            return

        job    = await db.jobs.find_one(
            {"_id": app_doc["job_id"]}
        )
        user   = await db.users.find_one(
            {"_id": app_doc["user_id"]}
        )
        resume = await db.resumes.find_one(
            {"user_id": app_doc["user_id"]}
        )

        if not all([job, user, resume]):
            await db.applications.update_one(
                {"_id": ObjectId(application_id)},
                {"$set": {
                    "status": "failed",
                    "error":  "Missing job, user, or resume"
                }}
            )
            client.close()
            return

        # Final pause check — user may have paused
        # between when task was queued and now
        if (not user.get("autopilot_enabled") or
            user.get("is_paused")):
            await db.applications.update_one(
                {"_id": ObjectId(application_id)},
                {"$set": {"status": "paused"}}
            )
            print(
                f"[Apply] Skipped — user paused: "
                f"{job['title']} @ {job['company']}"
            )
            client.close()
            return

        # Download resume from Supabase to temp file
        resume_path = await _download_resume(
            resume.get("file_url", ""),
            resume.get("filename", "resume.pdf")
        )

        if not resume_path:
            await db.applications.update_one(
                {"_id": ObjectId(application_id)},
                {"$set": {
                    "status": "failed",
                    "error":  "Could not download resume "
                              "from Supabase"
                  }}
            )
            client.close()
            return

        # Select bot by platform
        bot_cls = BOT_MAP.get(
            job.get("source", ""), GenericBot
        )
        bot     = bot_cls()

        try:
            print(
                f"[Apply] Starting: {job['title']} "
                f"@ {job['company']} "
                f"(source: {job['source']})"
            )

            result = await bot.apply(
                job, user, resume_path
            )

            if result["status"] == "applied":
                now = datetime.utcnow()

                # Update application to applied
                await db.applications.update_one(
                    {"_id": ObjectId(application_id)},
                    {"$set": {
                        "status":     "applied",
                        "applied_at": now,
                        "error":      ""
                    }}
                )

                # Increment stats counters
                await db.users.update_one(
                    {"_id": app_doc["user_id"]},
                    {"$inc": {
                        "stats.total_applied":     1,
                        "stats.applied_today":     1,
                        "stats.applied_this_week": 1,
                    }}
                )

                # Send Gmail notification
                email_sent = await send_application_email(
                    to_email  = user["email"],
                    user_name = user["name"],
                    job_title = job["title"],
                    company   = job["company"],
                    job_url   = job["apply_url"],
                    score     = app_doc.get(
                        "match_score", 0
                    ),
                )

                print(
                    f"[Apply] ✅ Applied: {job['title']} "
                    f"@ {job['company']} | "
                    f"Email sent: {email_sent}"
                )

            else:
                error_msg = result.get(
                    "error", "Unknown error"
                )
                await db.applications.update_one(
                    {"_id": ObjectId(application_id)},
                    {"$set": {
                        "status": "failed",
                        "error":  error_msg
                    }}
                )
                print(
                    f"[Apply] ❌ Failed: {job['title']} "
                    f"| {error_msg}"
                )

        except Exception as e:
            await db.applications.update_one(
                {"_id": ObjectId(application_id)},
                {"$set": {
                    "status": "failed",
                    "error":  str(e)
                }}
            )
            client.close()
            # Clean up temp file
            if resume_path and os.path.exists(resume_path):
                os.unlink(resume_path)
            raise self.retry(exc=e)

        finally:
            # Always clean up temp resume file
            if resume_path and os.path.exists(resume_path):
                os.unlink(resume_path)

        client.close()

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc)


async def _download_resume(
    file_url: str, filename: str
) -> str:
    """
    Downloads resume PDF from Supabase signed URL
    to a temporary file. Returns the temp file path.
    Returns empty string on failure.
    """
    if not file_url:
        return ""
    try:
        async with httpx.AsyncClient(
            timeout=30
        ) as client:
            response = await client.get(file_url)
            response.raise_for_status()

        # Write to temp file
        suffix = ".pdf"
        tmp = tempfile.NamedTemporaryFile(
            suffix=suffix, delete=False
        )
        tmp.write(response.content)
        tmp.close()
        return tmp.name

    except Exception as e:
        print(f"[Apply] Resume download failed: {e}")
        return ""
