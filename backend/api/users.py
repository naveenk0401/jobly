from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from models.user import UserCreate, UserUpdate
from bson import ObjectId
from datetime import datetime

router = APIRouter()

def _serialize(user: dict) -> dict:
    user["_id"] = str(user["_id"])
    return user

@router.post("/")
async def create_user(
    user: UserCreate, db=Depends(get_db)
):
    # Check duplicate email
    existing = await db.users.find_one(
        {"email": user.email}
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    doc = user.model_dump()
    doc["autopilot_enabled"]    = False
    doc["is_paused"]            = False
    doc["autopilot_started_at"] = None
    doc["last_scraped_at"]      = None
    doc["created_at"]           = datetime.utcnow()
    doc["stats"] = {
        "total_applied":     0,
        "applied_today":     0,
        "applied_this_week": 0,
    }

    result = await db.users.insert_one(doc)
    return {
        "user_id": str(result.inserted_id),
        "email":   user.email,
        "name":    user.name,
        "message": "User created successfully"
    }

@router.get("/{user_id}")
async def get_user(
    user_id: str, db=Depends(get_db)
):
    user = await db.users.find_one(
        {"_id": ObjectId(user_id)}
    )
    if not user:
        raise HTTPException(
            status_code=404, detail="User not found"
        )
    return _serialize(user)

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    updates: UserUpdate,
    db=Depends(get_db)
):
    update_data = {
        k: v for k, v in updates.model_dump().items()
        if v is not None
    }
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields to update"
        )
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return {"message": "Updated", "user_id": user_id}
