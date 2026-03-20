from fastapi import APIRouter, Depends, Query, HTTPException
from database import get_db
from workers.scrape_tasks import scrape_company_for_user
from bson import ObjectId

router = APIRouter()

@router.get("/")
async def list_jobs(
    skip:     int = Query(0, ge=0),
    limit:    int = Query(20, ge=1, le=100),
    source:   str = Query(None),
    company:  str = Query(None),
    location: str = Query(None),
    db=Depends(get_db)
):
    query = {"is_active": True}
    if source:
        query["source"] = source
    if company:
        query["company"] = {
            "$regex": company, "$options": "i"
        }
    if location:
        query["location"] = {
            "$regex": location, "$options": "i"
        }

    total  = await db.jobs.count_documents(query)
    cursor = db.jobs.find(query)\
                    .sort("scraped_at", -1)\
                    .skip(skip)\
                    .limit(limit)

    jobs = []
    async for j in cursor:
        j["_id"] = str(j["_id"])
        # Remove large embedding field from response
        j.pop("embedding", None)
        jobs.append(j)

    return {
        "total": total,
        "skip":  skip,
        "limit": limit,
        "jobs":  jobs
    }

@router.get("/{job_id}")
async def get_job(
    job_id: str, db=Depends(get_db)
):
    job = await db.jobs.find_one(
        {"_id": ObjectId(job_id)}
    )
    if not job:
        raise HTTPException(
            status_code=404, detail="Job not found"
        )
    job["_id"] = str(job["_id"])
    job.pop("embedding", None)
    return job

@router.post("/scrape")
async def trigger_scrape(
    platform: str = Query(...),
    company:  str = Query(...),
    user_id:  str = Query(
        "manual", description="user_id or 'manual'"
    )
):
    if platform not in ["greenhouse", "lever", "workday"]:
        raise HTTPException(
            status_code=400,
            detail="Platform must be: greenhouse, lever, workday"
        )
    task = scrape_company_for_user.delay(
        user_id, platform, company
    )
    return {
        "status":   "queued",
        "task_id":  task.id,
        "platform": platform,
        "company":  company,
        "message":  "Scrape task dispatched to Celery"
    }
