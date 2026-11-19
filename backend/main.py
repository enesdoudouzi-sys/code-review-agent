"""FastAPI Backend für den Code-Review-Agent."""

import os

from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from agent import review
from models import ReviewRequest, ReviewResponse

app = FastAPI(
    title="Code Review Agent API",
    description="KI-gestützter Code-Review mit Agentic Loop und Tool Use",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def pruefe_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    erwarteter_key = os.getenv("API_KEY")
    if erwarteter_key and api_key != erwarteter_key:
        raise HTTPException(status_code=401, detail="Ungültiger oder fehlender X-API-Key-Header.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
def review_code(request: ReviewRequest, _: None = Security(pruefe_api_key)):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code darf nicht leer sein.")
    try:
        report = review(request.code, request.dateiname)
        return ReviewResponse(dateiname=request.dateiname, report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
