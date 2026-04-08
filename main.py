from dotenv import load_dotenv
load_dotenv()  # Must be first — loads .env before any app module reads env vars

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Claim Processing Pipeline",
    description="AI-powered insurance claim PDF processor using LangGraph",
    version="1.0.0",
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
