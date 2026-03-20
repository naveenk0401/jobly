from fastapi import APIRouter, Depends, Query, HTTPException
from database import get_db
from models.application import ApplyRequest
from services.apply_service import ApplyService
from services.stats_service import StatsService
from workers.apply_tasks import apply_to_job

router = APIRouter()

@router.post("/apply")
async def trigger_apply(
    req: ApplyRequest,
    db=Depends(get_db)
):
    # Validate user exists
    from bson import ObjectId
    user = await db.users.find_one(
        {"_id": ObjectId(req.user_id)}
    )
    if not user:
        raise HTTPException(
            status_code=404, detail="User not found"
        )

    # Validate job exists
    job = await db.jobs.find_one(
        {"_id": ObjectId(req.job_id)}
    )
    if not job:
        raise HTTPException(
            status_code=404, detail="Job not found"
        )

    # Check not already applied
    existing = await db.applications.find_one({
        "user_id": ObjectId(req.user_id),
        "job_id":  ObjectId(req.job_id)
    })
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Already applied to this job"
        )

    svc     = ApplyService(db)
    app_doc = await svc.create_pending(
        req.user_id, req.job_id
    )

    # Dispatch to Celery
    apply_to_job.delay(str(app_doc["_id"]))

    return {
        "application_id": str(app_doc["_id"]),
        "status":         "pending",
        "job_title":      job["title"],
        "company":        job["company"],
        "message":        "Application queued. "
                          "Bot will apply shortly."
    }

@router.get("/dashboard")
async def get_dashboard(
    user_id: str = Query(...),
    db=Depends(get_db)
):
    svc = StatsService(db)
    return await svc.get_dashboard(user_id)

@router.get("/")
async def get_applications(
    user_id: str  = Query(...),
    status:  str  = Query(None),
    limit:   int  = Query(50, ge=1, le=200),
    db=Depends(get_db)
):
    svc  = ApplyService(db)
    apps = await svc.list_for_user(
        user_id, status, limit
    )
    return {"total": len(apps), "applications": apps}
