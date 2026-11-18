# code-review-agent

Ein KI-Agent, der automatisch Code-Reviews durchführt – powered by [Claude](https://www.anthropic.com/).

## Was macht der Agent?

Der Agent nimmt eine Code-Datei entgegen, analysiert sie eigenständig mithilfe von Werkzeugen und liefert ein strukturiertes Review mit Fokus auf:

- **Sicherheit** – potenzielle Schwachstellen
- **Stil** – Lesbarkeit und Konventionen
- **Logik** – Fehler und Verbesserungsvorschläge

## Architektur

```
Nutzer gibt Datei an
        │
        ▼
   KI-Agent (Claude)
        │
        ├──▶ Werkzeug: datei_lesen()
        ├──▶ Werkzeug: muster_suchen()
        │
        ▼
  Strukturierter Review-Report
```

## Quickstart

```bash
git clone https://github.com/enesdoudouzi-sys/code-review-agent.git
cd code-review-agent
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...
python agent.py beispiel.py
```

## Projektstruktur

```
code-review-agent/
├── agent.py          # Haupt-Agent (agentic loop)
├── werkzeuge.py      # Werkzeuge, die der Agent aufrufen kann
├── requirements.txt
└── README.md
```

## Tech Stack

- Python 3.11+
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- Claude claude-sonnet-4-6

## Team-Workflow

1. Eigenen Branch erstellen: `git checkout -b feature/mein-feature`
2. Änderungen committen und pushen
3. Pull Request öffnen
4. Gegenseitiges Code-Review
5. Merge in `main`

## Lizenz

MIT
