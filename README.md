# 🤖 KI Code-Review-Agent

[![CI](https://github.com/enesdoudouzi-sys/code-review-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/enesdoudouzi-sys/code-review-agent/actions/workflows/ci.yml)
[![Backend](https://img.shields.io/badge/Backend-Live%20on%20Render-46E3B7?logo=render)](https://code-review-agent-f9aa.onrender.com/health)
[![Frontend](https://img.shields.io/badge/Frontend-Live%20on%20Vercel-000000?logo=vercel)](https://code-review-agent-js5w.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose)

Ein autonomer KI-Agent, der Quellcode automatisch analysiert und strukturierte Reviews mit Sicherheits-, Stil- und Logik-Feedback generiert — gebaut auf einem echten agentischen Loop mit Tool Use.

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| **Frontend** | https://code-review-agent-js5w.vercel.app |
| **Backend API** | https://code-review-agent-f9aa.onrender.com |
| **API Docs** | https://code-review-agent-f9aa.onrender.com/docs |

## 🏗️ Architektur

```
┌──────────────────────────────────────────────────────────┐
│                    Code-Review-Agent                     │
├──────────────┬──────────────────┬───────────────────────┤
│   Frontend   │      Backend     │       KI-Agent        │
│  React + TS  │    FastAPI       │   Agentic Loop        │
│  Vite + TW   │    Pydantic v2   │   Tool Use API        │
│   Vercel     │     Render       │   LLM-Integration     │
└──────────────┴──────────────────┴───────────────────────┘
```

**Datenfluss:**
```
Browser → Vercel (React) → Render (FastAPI) → LLM-Agent → Tools → Report
```

## ✨ Features

- **Agentischer Loop** — das Modell ruft Tools eigenständig auf und iteriert bis zum fertigen Report
- **Tool Use API** — zwei strukturierte Werkzeuge mit JSON-Schema: `code_analysieren` + `muster_suchen`
- **FastAPI Backend** — typsicheres REST-API mit Pydantic v2, CORS, optionaler X-API-Key-Auth
- **React Frontend** — modernes UI mit TypeScript, Vite und Tailwind CSS v4
- **Sicherheit** — Path Traversal Protection, bounded Iteration (max. 10), Input-Validierung
- **Tests** — 10 pytest Tests (Unit + Integration) mit gemockten LLM-Calls
- **CI/CD** — GitHub Actions: Backend-Tests + Frontend-Build bei jedem Push

## 🚀 Quickstart (Docker)

```bash
git clone https://github.com/enesdoudouzi-sys/code-review-agent
cd code-review-agent
cp .env.example .env          # ANTHROPIC_API_KEY eintragen
docker-compose up --build
```

→ Frontend: http://localhost:5173  
→ API Docs: http://localhost:8000/docs

## 💻 Lokale Entwicklung

**Backend:**
```bash
pip install -r backend/requirements.txt
cd backend && uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend && npm install && npm run dev
```

**CLI-Modus:**
```bash
pip install -r requirements.txt
python agent.py mein_code.py
```

## 🔌 API-Endpoints

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| `GET` | `/health` | Statusprüfung |
| `POST` | `/review` | Code-Review starten |
| `GET` | `/docs` | Swagger-UI |

**Beispiel-Request:**
```bash
curl -X POST https://code-review-agent-f9aa.onrender.com/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a, b): return a + b", "dateiname": "math.py"}'
```

**Beispiel-Response:**
```json
{
  "dateiname": "math.py",
  "report": "## 🔒 Sicherheit\n- Keine Probleme gefunden.\n\n## ✏️ Stil\n...",
  "status": "success"
}
```

## 🧪 Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

```
tests/test_werkzeuge.py::test_muster_suchen_findet_treffer       PASSED
tests/test_werkzeuge.py::test_muster_suchen_kein_treffer         PASSED
tests/test_werkzeuge.py::test_muster_suchen_ungueltiges_muster   PASSED
tests/test_werkzeuge.py::test_muster_suchen_mehrere_treffer      PASSED
tests/test_werkzeuge.py::test_datei_lesen_nicht_gefunden         PASSED
tests/test_werkzeuge.py::test_datei_lesen_path_traversal_geblockt PASSED
tests/test_api.py::test_health                                   PASSED
tests/test_api.py::test_leerer_code_gibt_400                     PASSED
tests/test_api.py::test_fehlender_body_gibt_422                  PASSED
tests/test_api.py::test_review_erfolg_mit_mock                   PASSED
```

## 📁 Projektstruktur

```
code-review-agent/
├── agent.py              # CLI-Agent (Agentic Loop)
├── werkzeuge.py          # Tool-Definitionen (datei_lesen, muster_suchen)
├── backend/
│   ├── agent.py          # Backend-Agent (Agentic Loop)
│   ├── main.py           # FastAPI-App (CORS, Auth, Endpoints)
│   ├── models.py         # Pydantic-Modelle
│   ├── werkzeuge.py      # Backend-Werkzeuge
│   └── requirements.txt
├── frontend/             # React + TypeScript + Vite + Tailwind
├── tests/
│   ├── test_werkzeuge.py # Unit-Tests
│   └── test_api.py       # Integrations-Tests
├── .github/workflows/    # GitHub Actions CI
├── render.yaml           # Render Deployment-Konfiguration
├── docker-compose.yml
└── .env.example
```

## 🔒 Sicherheitsfeatures

| Feature | Beschreibung |
|---------|-------------|
| **Path Traversal Protection** | `datei_lesen()` blockt Pfade außerhalb des Projektverzeichnisses |
| **Bounded Iteration** | Max. 10 Iterationen verhindert unbegrenzte API-Kosten |
| **API-Key-Auth** | Optional via `API_KEY` Umgebungsvariable (`X-API-Key` Header) |
| **Input-Validierung** | Pydantic v2 validiert alle eingehenden Requests |

## ☁️ Deployment

**Backend → Render:**
```
Build Command:  pip install -r backend/requirements.txt
Start Command:  cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
Env Vars:       ANTHROPIC_API_KEY=<your-key>
```

**Frontend → Vercel:**
```
Root Directory: frontend
Env Vars:       VITE_API_URL=https://code-review-agent-f9aa.onrender.com
```
