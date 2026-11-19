# 🤖 KI Code-Review-Agent

[![CI](https://github.com/enesdoudouzi-sys/code-review-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/enesdoudouzi-sys/code-review-agent/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docs.docker.com/compose)

Ein autonomer KI-Agent, der Quellcode automatisch analysiert und strukturierte Reviews mit Sicherheits-, Stil- und Logik-Feedback generiert — gebaut auf einem echten agentischen Loop mit Tool Use.

## Quickstart (Docker)

```bash
git clone https://github.com/enesdoudouzi-sys/code-review-agent
cd code-review-agent
cp .env.example .env          # ANTHROPIC_API_KEY eintragen
docker-compose up --build
```

→ Frontend: http://localhost:5173
→ API Docs: http://localhost:8000/docs

## Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

## Deployment

**Backend → Render:**
Root Directory: `backend`, Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Frontend → Vercel:**
Root Directory: `frontend`, Env: `VITE_API_URL` = Render-URL

## Sicherheitsfeatures

- Path Traversal Protection in `datei_lesen()`
- Bounded Iteration: max. 10 Iterationen im agentischen Loop
- Optionale X-API-Key-Auth via `API_KEY` Umgebungsvariable
- Pydantic v2 Input-Validierung
