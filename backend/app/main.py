from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import briefing

app = FastAPI(title="AcademicBriefer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(briefing.router)
