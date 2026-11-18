"""Code-Review-Agent – liest eine Datei und liefert ein strukturiertes Review."""

import json
import sys

import anthropic

from werkzeuge import WERKZEUG_DEFINITIONEN, WERKZEUG_MAP

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Du bist ein erfahrener Code-Reviewer.
Analysiere den bereitgestellten Code gründlich und erstelle einen strukturierten Report mit drei Abschnitten:

1. **Sicherheit** – potenzielle Schwachstellen (SQL-Injection, unsichere Imports, etc.)
2. **Stil** – Lesbarkeit, Namenskonventionen, unnötige Komplexität
3. **Logik** – Fehler, Edge Cases, Verbesserungsvorschläge

Nutze die verfügbaren Werkzeuge, um den Code zu lesen und zu analysieren.
Halte den Report präzise und actionable."""


def review(dateipfad: str) -> str:
    client = anthropic.Anthropic()
    nachrichten = [
        {
            "role": "user",
            "content": f"Bitte reviewe die Datei: {dateipfad}",
        }
    ]

    while True:
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
            werkzeug_ergebnisse = []
            for block in antwort.content:
                if block.type != "tool_use":
                    continue
                funktion = WERKZEUG_MAP.get(block.name)
                if funktion is None:
                    ergebnis = {"fehler": f"Unbekanntes Werkzeug: {block.name}"}
                else:
                    ergebnis = funktion(**block.input)
                werkzeug_ergebnisse.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(ergebnis, ensure_ascii=False),
                    }
                )
            nachrichten.append({"role": "user", "content": werkzeug_ergebnisse})


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: python agent.py <dateipfad>")
        sys.exit(1)

    pfad = sys.argv[1]
    print(f"Starte Review für: {pfad}\n{'─' * 50}\n")
    print(review(pfad))
