"""FastAPI Backend für den Code-Review-Agent."""

import re

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent import review, review_stream
from models import (
    MultiReviewRequest,
    MultiReviewResponse,
    PRRequest,
    ReviewRequest,
    ReviewResponse,
)

app = FastAPI(
    title="Code Review Agent API",
    description="KI-gestützter Code-Review mit Claude",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "https://code-review-agent-ui.onrender.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/review", response_model=ReviewResponse)
def review_code(request: ReviewRequest):
    """Standard Review — gibt fertigen Report zurück."""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code darf nicht leer sein.")
    try:
        report = review(request.code, request.dateiname)
        return ReviewResponse(dateiname=request.dateiname, report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review/stream")
def review_code_stream(request: ReviewRequest):
    """Streaming Review — sendet Live-Events während der Agent arbeitet."""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code darf nicht leer sein.")
    return StreamingResponse(
        review_stream(request.code, request.dateiname),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/review/multi", response_model=MultiReviewResponse)
def review_multi(request: MultiReviewRequest):
    """Reviewt mehrere Dateien auf einmal."""
    if not request.dateien:
        raise HTTPException(status_code=400, detail="Mindestens eine Datei erforderlich.")
    if len(request.dateien) > 10:
        raise HTTPException(status_code=400, detail="Maximal 10 Dateien pro Anfrage.")

    reviews = []
    for datei in request.dateien:
        if not datei.code.strip():
            continue
        try:
            report = review(datei.code, datei.dateiname)
            reviews.append(ReviewResponse(dateiname=datei.dateiname, report=report))
        except Exception as e:
            reviews.append(ReviewResponse(dateiname=datei.dateiname, report=f"Fehler: {e}", status="error"))

    return MultiReviewResponse(reviews=reviews, dateien_gesamt=len(reviews))


@app.post("/review/pr")
def review_pr(request: PRRequest):
    """Reviewt alle geänderten Python-Dateien eines GitHub Pull Requests."""
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", request.pr_url)
    if not match:
        raise HTTPException(status_code=400, detail="Ungültige GitHub PR-URL. Format: https://github.com/owner/repo/pull/123")

    owner, repo, pull_number = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"

    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(api_url, headers={"Accept": "application/vnd.github.v3+json"})
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="PR nicht gefunden. Nur öffentliche Repos werden unterstützt.")
            response.raise_for_status()
            dateien = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GitHub API nicht erreichbar: {e}")

    py_dateien = [d for d in dateien if d["filename"].endswith(".py") and d.get("status") != "removed"]
    if not py_dateien:
        return {"message": "Keine Python-Dateien in diesem PR gefunden.", "reviews": []}

    reviews = []
    for datei in py_dateien[:5]:
        try:
            with httpx.Client(timeout=15) as client:
                code_response = client.get(datei["raw_url"])
                code = code_response.text
            report = review(code, datei["filename"])
            reviews.append({"dateiname": datei["filename"], "report": report, "status": "success"})
        except Exception as e:
            reviews.append({"dateiname": datei["filename"], "report": f"Fehler: {e}", "status": "error"})

    return {
        "pr_url": request.pr_url,
        "dateien_gesamt": len(py_dateien),
        "reviewt": len(reviews),
        "reviews": reviews,
    }
