# 🤖 code-review-agent

> Ein KI-Agent, der Code-Dateien automatisch reviewt – powered by Claude (Anthropic).

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Sonnet%204.6-D97706?style=flat-square)
![License](https://img.shields.io/badge/Lizenz-MIT-22C55E?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Entwicklung-F59E0B?style=flat-square)

---

## Was macht dieser Agent?

Der Agent bekommt eine Code-Datei – und erledigt den Rest selbst.  
Er entscheidet eigenständig, welche Werkzeuge er aufruft, liest den Code, analysiert ihn und liefert einen strukturierten Review-Report.

```
$ python agent.py mein_code.py

──────────────────────────────────────────────────
## 1. Sicherheit
  ⚠ Zeile 14: eval() mit externem Input – potenziell gefährlich

## 2. Stil
  • Funktionsname `x` zu unspezifisch → umbenennen in `berechne_summe`
  • Fehlende Typannotationen in 3 Funktionen

## 3. Logik
  ✓ Keine kritischen Fehler gefunden
  • Division ohne Nullprüfung in Zeile 42
──────────────────────────────────────────────────
```

---

## Architektur

```
┌─────────────────────────────────────────┐
│           Nutzer gibt Datei an           │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│           KI-Agent  (Claude)             │
│                                          │
│  entscheidet selbst, was er als          │
│  Nächstes braucht (agentic loop)         │
└──────┬──────────────────────┬───────────┘
       │                      │
       ▼                      ▼
┌─────────────┐       ┌──────────────────┐
│ datei_lesen │       │  muster_suchen   │
│  Dateiinhalt│       │  Regex im Code   │
│  + Zeilenzahl       │  → Treffer-Liste │
└──────┬──────┘       └────────┬─────────┘
       │                       │
       └──────────┬────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         Strukturierter Report            │
│   🔒 Sicherheit  ✏ Stil  🧠 Logik       │
└─────────────────────────────────────────┘
```

---

## Quickstart

```bash
# 1. Repo klonen
git clone https://github.com/enesdoudouzi-sys/code-review-agent.git
cd code-review-agent

# 2. Virtuelle Umgebung
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. API-Key setzen
export ANTHROPIC_API_KEY=sk-ant-...

# 5. Loslegen
python agent.py mein_code.py
```

---

## Projektstruktur

```
code-review-agent/
│
├── agent.py          ← Haupt-Agent mit agentic loop
├── werkzeuge.py      ← Werkzeuge: datei_lesen, muster_suchen
├── requirements.txt  ← anthropic, httpx
└── README.md
```

---

## Tech Stack

| Komponente | Details |
|---|---|
| Sprache | Python 3.11+ |
| KI-Modell | Claude Sonnet 4.6 (Anthropic) |
| SDK | [anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python) |
| Muster | Agentic Loop mit Tool Use |

---

## Team-Workflow

```
main
 │
 ├── feature/sicherheits-check   ← Mitglied A
 ├── feature/stil-analyse         ← Mitglied B
 │
 └── Pull Request → Review → Merge
```

1. `git checkout -b feature/mein-feature`
2. Änderungen entwickeln & committen
3. Pull Request öffnen
4. Gegenseitiges Code-Review
5. Merge in `main`

---

## Lizenz

MIT © 2026 enesdoudouzi-sys
