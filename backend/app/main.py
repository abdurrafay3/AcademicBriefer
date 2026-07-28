from fastapi import FastAPI

from backend.api import briefing

app = FastAPI(title="AcademicBriefer")
app.include_router(briefing.router)
