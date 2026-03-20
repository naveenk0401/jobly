from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

async def _get_user_or_404(user_id: str, db):
    user = await db.users.find_one(
        {"_id": ObjectId(user_id)}
    )
    if not user:
        raise HTTPException(
            status_code=404, detail="User not found"
        )
    return user

@router.post("/enable")
async def enable_autopilot(
    user_id: str, db=Depends(get_db)
):
    await _get_user_or_404(user_id, db)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "autopilot_enabled":    True,
            "is_paused":            False,
            "autopilot_started_at": datetime.utcnow(),
        }}
    )
    return {
        "autopilot": "enabled",
        "user_id":   user_id,
        "message":   "Autopilot is now ON. "
                     "Jobly will apply to jobs every 6 hours."
    }

@router.post("/pause")
async def pause_autopilot(
    user_id: str, db=Depends(get_db)
):
    await _get_user_or_404(user_id, db)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_paused": True}}
    )
    return {
        "autopilot": "paused",
        "user_id":   user_id,
        "message":   "Autopilot paused. "
                     "No new applications will be submitted."
    }

@router.post("/resume")
async def resume_autopilot(
    user_id: str, db=Depends(get_db)
):
    await _get_user_or_404(user_id, db)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_paused": False}}
    )
    return {
        "autopilot": "resumed",
        "user_id":   user_id,
        "message":   "Autopilot resumed."
    }

@router.post("/disable")
async def disable_autopilot(
    user_id: str, db=Depends(get_db)
):
    await _get_user_or_404(user_id, db)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "autopilot_enabled": False,
            "is_paused":         False,
        }}
    )
    return {
        "autopilot": "disabled",
        "user_id":   user_id,
    }

@router.get("/status")
async def autopilot_status(
    user_id: str, db=Depends(get_db)
):
    user = await _get_user_or_404(user_id, db)
    return {
        "autopilot_enabled":    user.get(
            "autopilot_enabled", False
        ),
        "is_paused":            user.get(
            "is_paused", False
        ),
        "autopilot_started_at": user.get(
            "autopilot_started_at"
        ),
        "last_scraped_at":      user.get(
            "last_scraped_at"
        ),
        "stats":                user.get("stats", {}),
        "preferences":          user.get("preferences", {}),
    }
