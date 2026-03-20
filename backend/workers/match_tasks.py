from workers.celery_app import app
from services.match_service import MatchService
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from bson import ObjectId
from datetime import datetime
import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

@app.task
def match_new_jobs_for_user(
    user_id: str,
    job_ids: list
):
    """
    Automatically triggered by scrape_company_for_user
    when new jobs are found.

    For each new job:
      1. Check user is still active + not paused
      2. Check not already applied
      3. Score resume vs job description
      4. Store application record with score + reasons
      5. If score >= threshold → queue apply_to_job

    Rate limit: asyncio.sleep(2) after each Groq call.
    """
    async def _run():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db     = client[settings.MONGO_DB]
        svc    = MatchService()

        # Load user
        user = await db.users.find_one(
            {"_id": ObjectId(user_id)}
        )
        if not user:
            print(f"[Match] User {user_id} not found")
            client.close()
            return

        # Respect pause state
        if (not user.get("autopilot_enabled") or
            user.get("is_paused")):
            print(f"[Match] User {user_id} paused/disabled")
            client.close()
            return

        # Load resume
        resume = await db.resumes.find_one(
            {"user_id": ObjectId(user_id)}
        )
        if not resume:
            print(f"[Match] No resume for user {user_id}")
            client.close()
            return

        threshold   = user.get(
            "preferences", {}
        ).get("match_threshold", 65)
        resume_text = resume.get("parsed_text", "")

        if not resume_text:
            print(f"[Match] Empty resume text for {user_id}")
            client.close()
            return

        matched  = 0
        queued   = 0

        for job_id in job_ids:
            job = await db.jobs.find_one(
                {"_id": ObjectId(job_id)}
            )
            if not job:
                continue

            # Skip if already applied or in progress
            existing = await db.applications.find_one({
                "user_id": ObjectId(user_id),
                "job_id":  ObjectId(job_id)
            })
            if existing:
                continue

            # Score the job
            try:
                result = await svc.score(resume_text, job)
            except Exception as e:
                print(f"[Match] Score failed {job_id}: {e}")
                continue

            score   = result["score"]
            reasons = result["reasons"]
            matched += 1

            print(
                f"[Match] {job['title']} @ "
                f"{job['company']} → {score}/100"
            )

            # Always create an application record
            status = (
                "pending"
                if score >= threshold
                else "below_threshold"
            )

            app_doc = {
                "user_id":     ObjectId(user_id),
                "job_id":      ObjectId(job_id),
                "match_score": score,
                "status":      status,
                "reasons":     reasons,
                "applied_at":  None,
                "error":       "",
                "created_at":  datetime.utcnow(),
            }

            try:
                inserted = await db.applications.insert_one(
                    app_doc
                )
            except Exception as e:
                # Duplicate key — already applied
                print(f"[Match] Duplicate skip: {e}")
                continue

            # Auto-trigger apply if score clears threshold
            if score >= threshold:
                from workers.apply_tasks import apply_to_job
                apply_to_job.delay(
                    str(inserted.inserted_id)
                )
                queued += 1
                print(
                    f"[Match] Queued apply for "
                    f"{job['title']} (score: {score})"
                )

        print(
            f"[Match] User {user_id}: "
            f"{matched} scored, {queued} apply tasks queued"
        )
        client.close()

    asyncio.run(_run())
