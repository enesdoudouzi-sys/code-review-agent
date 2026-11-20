"""FastAPI Backend für den KI Code-Review & Security-Scan Agent."""

import os

from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from agent import review, security_scan
from database import get_history, init_db, save_review
from models import ReviewRequest, ReviewResponse

app = FastAPI(
    title="KI Code-Review-Agent API",
    description=(
        "Automatisierter Code-Review und Security-Scan powered by Anthropic LLM API. "
        "Verwendet einen agentischen Loop mit Tool Use für strukturierte Markdown-Reports. "
        "Endpoints: POST /review (Code-Review), POST /security-scan (OWASP-basierter Security Scan), "
        "GET /history (letzte Analysen), GET /health (Status)."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def pruefe_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    erwarteter_key = os.getenv("API_KEY")
    if erwarteter_key and api_key != erwarteter_key:
        raise HTTPException(status_code=401, detail="Ungültiger oder fehlender X-API-Key-Header.")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health", summary="Health Check", tags=["Status"])
def health():
    """Gibt den API-Status zurück. Wird von Render als Health-Check-Endpoint genutzt."""
    return {"status": "ok", "version": "2.0.0"}


@app.post(
    "/review",
    response_model=ReviewResponse,
    summary="Code-Review starten",
    tags=["Review"],
)
def review_code(request: ReviewRequest, _: None = Security(pruefe_api_key)):
    """
    Analysiert den übergebenen Code und erstellt einen strukturierten Review-Report.

    Der KI-Agent durchläuft einen agentischen Loop (max. 10 Iterationen) und verwendet
    Tool Use um den Code zu analysieren. Der Report enthält Sektionen zu Sicherheit,
    Stil und Logik als Markdown.
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code darf nicht leer sein.")
    try:
        report = review(request.code, request.dateiname)
        save_review(request.dateiname, "review", report)
        return ReviewResponse(dateiname=request.dateiname, report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/security-scan",
    response_model=ReviewResponse,
    summary="Security Scan (OWASP)",
    tags=["Security"],
)
def security_scan_code(request: ReviewRequest, _: None = Security(pruefe_api_key)):
    """
    Führt einen OWASP-basierten Security Scan durch.

    Analysiert den Code auf Sicherheitslücken nach OWASP Top 10:
    SQL Injection, Command Injection, Path Traversal, XSS, CSRF und weitere.
    Jede Schwachstelle wird mit CVSS-Schweregrad bewertet (Kritisch / Hoch / Mittel / Niedrig).
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code darf nicht leer sein.")
    try:
        report = security_scan(request.code, request.dateiname)
        save_review(request.dateiname, "security", report)
        return ReviewResponse(dateiname=request.dateiname, report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history", summary="Analyse-Historie", tags=["Status"])
def history(limit: int = 20):
    """Gibt die letzten Analysen zurück (max. 20). Jeder Eintrag enthält Dateiname, Modus, Zeitstempel und Vorschau."""
    return get_history(limit)
