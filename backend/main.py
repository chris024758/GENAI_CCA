from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from graph import run_workflow, stream_workflow_events
from inventory import fetch_inventory
from models import GenerateAdRequest

load_dotenv(Path(__file__).parent / ".env")

app = FastAPI(title="Image Ad Agent Pipeline")

# The React dev server runs on another port during demos, so CORS is required.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/inventory")
async def inventory() -> dict:
    return (await fetch_inventory()).model_dump()


@app.post("/api/generate-ad")
async def generate_ad(request: GenerateAdRequest) -> dict:
    result = await run_workflow(request.model_dump())
    return result.model_dump()


@app.get("/api/generate-ad/stream")
async def generate_ad_stream(
    product_id: str | None = Query(default=None),
    platform: str = Query(default="Instagram"),
    style: str = Query(default="premium social media ad"),
    audience: str | None = Query(default=None),
    cta: str = Query(default="Shop now"),
) -> StreamingResponse:
    async def event_source():
        payload = {
            "product_id": product_id,
            "platform": platform,
            "style": style,
            "audience": audience,
            "cta": cta,
        }
        async for event in stream_workflow_events(payload):
            yield f"data: {json.dumps(event.model_dump())}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")
