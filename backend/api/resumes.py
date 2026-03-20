from fastapi import (
    APIRouter, Depends, UploadFile,
    File, Form, HTTPException
)
from database import get_db
from utils.pdf_parser import extract_text
from utils.supabase_client import upload_resume
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/")
async def upload_resume_endpoint(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db=Depends(get_db)
):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    # Read file bytes
    file_bytes = await file.read()

    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Max 10MB."
        )

    # Parse text from PDF
    parsed_text = extract_text(file_bytes)
    if not parsed_text or len(parsed_text) < 50:
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from PDF. "
                   "Ensure the PDF is not scanned/image-only."
        )

    # Upload to Supabase Storage (S3)
    filename  = f"resume_{user_id}.pdf"
    file_url  = await upload_resume(
        user_id, file_bytes, filename
    )

    # Store metadata in MongoDB
    doc = {
        "user_id":     ObjectId(user_id),
        "filename":    filename,
        "file_url":    file_url,
        "parsed_text": parsed_text,
        "embedding":   [],     # filled Day 4
        "char_count":  len(parsed_text),
        "uploaded_at": datetime.utcnow(),
    }

    await db.resumes.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": doc},
        upsert=True
    )

    return {
        "status":               "uploaded",
        "file_url":             file_url,
        "char_count":           len(parsed_text),
        "parsed_text_preview":  parsed_text[:200] + "...",
        "message": "Resume uploaded to Supabase and parsed"
    }

@router.get("/{user_id}")
async def get_resume(
    user_id: str, db=Depends(get_db)
):
    resume = await db.resumes.find_one(
        {"user_id": ObjectId(user_id)}
    )
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="No resume found for this user"
        )
    return {
        "user_id":              user_id,
        "filename":             resume.get("filename"),
        "file_url":             resume.get("file_url"),
        "char_count":           resume.get("char_count"),
        "parsed_text_preview":  resume.get(
            "parsed_text", ""
        )[:300],
        "uploaded_at":          resume.get("uploaded_at"),
        "has_embedding":        len(
            resume.get("embedding", [])
        ) > 0,
    }
