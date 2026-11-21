"""Code-Review-Agent – agentic loop mit Claude API und Tool Use."""

import json
from typing import Generator

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


def review(code: str, dateiname: str = "code.py") -> str:
    """Führt einen vollständigen Code-Review durch und gibt den Report zurück."""
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

    return "(Max. Iterationen erreicht)"


def review_stream(code: str, dateiname: str = "code.py") -> Generator[str, None, None]:
    """Streamt den Review-Prozess als Server-Sent Events."""
    client = anthropic.Anthropic()
    nachrichten = [
        {
            "role": "user",
            "content": f"Bitte reviewe folgenden Code aus der Datei `{dateiname}`:\n\n```\n{code}\n```",
        }
    ]

    def event(data: dict) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    yield event({"type": "start", "dateiname": dateiname})

    for iteration in range(MAX_ITERATIONEN):
        yield event({"type": "thinking", "iteration": iteration + 1})

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
                    yield event({"type": "report", "content": block.text})
            yield event({"type": "done"})
            return

        if antwort.stop_reason == "tool_use":
            ergebnisse = []
            for block in antwort.content:
                if block.type != "tool_use":
                    continue

                yield event({"type": "tool_call", "name": block.name, "input": block.input})

                funktion = WERKZEUG_MAP.get(block.name)
                ergebnis = funktion(**block.input) if funktion else {"fehler": f"Unbekanntes Werkzeug: {block.name}"}

                yield event({"type": "tool_result", "name": block.name, "result": ergebnis})

                ergebnisse.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(ergebnis, ensure_ascii=False),
                    }
                )
            nachrichten.append({"role": "user", "content": ergebnisse})

    yield event({"type": "error", "message": "Max. Iterationen erreicht"})


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Verwendung: python agent.py <dateipfad>")
        sys.exit(1)

    pfad = sys.argv[1]
    code = Path(pfad).read_text(encoding="utf-8")
    print(f"Starte Review für: {pfad}\n{'─' * 50}\n")
    print(review(code, pfad))
