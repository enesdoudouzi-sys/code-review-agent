"""FastAPI Backend für den Code-Review-Agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent import review
from models import ReviewRequest, ReviewResponse

app = FastAPI(
    title="Code Review Agent API",
    description="KI-gestützter Code-Review mit Claude",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
def review_code(request: ReviewRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code darf nicht leer sein.")
    try:
        report = review(request.code, request.dateiname)
        return ReviewResponse(dateiname=request.dateiname, report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
