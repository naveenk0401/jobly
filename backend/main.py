from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_db, close_db
from api import users, resumes, jobs, applications, autopilot

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(
    title="Jobly API",
    description="AI-powered job application autopilot",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "app": "Jobly", "version": "1.0.0"}

# All routers
app.include_router(
    users.router,
    prefix="/user",
    tags=["users"]
)
app.include_router(
    resumes.router,
    prefix="/resume",
    tags=["resumes"]
)
app.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["jobs"]
)
app.include_router(
    autopilot.router,
    prefix="/autopilot",
    tags=["autopilot"]
)
app.include_router(
    applications.router,
    prefix="/applications",
    tags=["applications"]
)
