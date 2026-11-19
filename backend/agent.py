"""Code-Review-Agent – agentic loop mit LLM-API und Tool Use."""

import json

import anthropic

from werkzeuge import WERKZEUG_DEFINITIONEN, WERKZEUG_MAP

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONEN = 10

SYSTEM_PROMPT = """Du bist ein erfahrener Senior-Software-Ingenieur und Code-Reviewer.
Analysiere den bereitgestellten Code gründlich mithilfe der verfügbaren Werkzeuge.

Erstelle anschließend einen strukturierten Markdown-Report mit genau diesen drei Abschnitten:

## 🔒 Sicherheit
Potenzielle Schwachstellen (z. B. Injection, unsichere Imports, hartcodierte Secrets).

## ✏️ Stil
Lesbarkeit, Namenskonventionen, unnötige Komplexität, fehlende Typannotationen.

## 🧠 Logik
Fehler, fehlende Edge-Case-Behandlung, Verbesserungsvorschläge.

Sei präzise und actionable. Nutze Bullet Points."""


SECURITY_PROMPT = """Du bist ein erfahrener Penetration Tester und Security Engineer.
Analysiere den bereitgestellten Code auf Sicherheitslücken nach OWASP Top 10 und weiteren Best Practices.

Erstelle einen strukturierten Markdown-Report mit genau diesen Abschnitten:

## 🔒 Kritische Schwachstellen
Schwerwiegende Sicherheitslücken (z.B. SQL Injection, Command Injection, RCE).

## ⚠️ Mittlere Risiken
Path Traversal, unsichere Deserialisierung, fehlende Input-Validierung.

## 💡 Empfehlungen
Konkrete Fixes mit Code-Beispielen. Priorisiert nach Kritikalität.

## ✅ Positiv bewertet
Was bereits sicher implementiert ist.

Bewerte jede Schwachstelle mit CVSS-Schweregrad: Kritisch / Hoch / Mittel / Niedrig.
Sei präzise. Nenne konkrete Zeilen und Funktionen."""


def security_scan(code: str, dateiname: str = "code.py") -> str:
    client = anthropic.Anthropic()
    nachrichten = [
        {
            "role": "user",
            "content": f"Führe einen Security Scan für folgenden Code aus der Datei `{dateiname}` durch:\n\n```\n{code}\n```",
        }
    ]

    for _ in range(MAX_ITERATIONEN):
        antwort = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SECURITY_PROMPT,
            tools=WERKZEUG_DEFINITIONEN,
            messages=nachrichten,
        )

        nachrichten.append({"role": "assistant", "content": antwort.content})

        if antwort.stop_reason == "end_turn":
            for block in antwort.content:
                if hasattr(block, "text"):
                    return block.text
            return "(kein Text erhalten)"

        if antwort.stop_reason == "tool_use":
            ergebnisse = []
            for block in antwort.content:
                if block.type != "tool_use":
                    continue
                funktion = WERKZEUG_MAP.get(block.name)
                ergebnis = funktion(**block.input) if funktion else {"fehler": f"Unbekanntes Werkzeug: {block.name}"}
                ergebnisse.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(ergebnis, ensure_ascii=False),
                    }
                )
            nachrichten.append({"role": "user", "content": ergebnisse})

    return "(Maximale Iterationszahl erreicht)"


def review(code: str, dateiname: str = "code.py") -> str:
    client = anthropic.Anthropic()
    nachrichten = [
        {
            "role": "user",
            "content": f"Bitte reviewe folgenden Code aus der Datei `{dateiname}`:\n\n```\n{code}\n```",
        }
    ]

    for _ in range(MAX_ITERATIONEN):
        antwort = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=WERKZEUG_DEFINITIONEN,
            messages=nachrichten,
        )

        nachrichten.append({"role": "assistant", "content": antwort.content})

        if antwort.stop_reason == "end_turn":
            for block in antwort.content:
                if hasattr(block, "text"):
                    return block.text
            return "(kein Text erhalten)"

        if antwort.stop_reason == "tool_use":
            ergebnisse = []
            for block in antwort.content:
                if block.type != "tool_use":
                    continue
                funktion = WERKZEUG_MAP.get(block.name)
                ergebnis = funktion(**block.input) if funktion else {"fehler": f"Unbekanntes Werkzeug: {block.name}"}
                ergebnisse.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(ergebnis, ensure_ascii=False),
                    }
                )
            nachrichten.append({"role": "user", "content": ergebnisse})

    return "(Maximale Iterationszahl erreicht)"
