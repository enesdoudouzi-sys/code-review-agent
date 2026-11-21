"""Code-Review-Agent – agentic loop mit Google Gemini API und Tool Use."""

import json
import os
from typing import Generator

from google import genai
from google.genai import types

from werkzeuge import WERKZEUG_DEFINITIONEN, WERKZEUG_MAP

MODEL = "gemini-1.5-flash"
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


def _build_tool() -> types.Tool:
    """Konvertiert unsere Werkzeug-Definitionen in eine Gemini Tool-Definition."""
    declarations = []
    for w in WERKZEUG_DEFINITIONEN:
        props = {}
        for name, schema in w["input_schema"]["properties"].items():
            props[name] = types.Schema(
                type=types.Type.STRING,
                description=schema.get("description", ""),
            )
        declarations.append(
            types.FunctionDeclaration(
                name=w["name"],
                description=w["description"],
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties=props,
                    required=w["input_schema"].get("required", []),
                ),
            )
        )
    return types.Tool(function_declarations=declarations)


def _get_client() -> genai.Client:
    return genai.Client(api_key=os.environ["GOOGLE_API_KEY"])


def _ausfuehren(name: str, args: dict) -> dict:
    funktion = WERKZEUG_MAP.get(name)
    if funktion:
        return funktion(**args)
    return {"fehler": f"Unbekanntes Werkzeug: {name}"}


def _fn_calls(response) -> list:
    """Gibt alle Parts mit einem echten function_call zurück."""
    result = []
    try:
        for part in response.candidates[0].content.parts:
            if part.function_call and part.function_call.name:
                result.append(part.function_call)
    except Exception:
        pass
    return result


def review(code: str, dateiname: str = "code.py") -> str:
    """Führt einen vollständigen Code-Review durch und gibt den Report zurück."""
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[_build_tool()],
    )
    contents = [f"Bitte reviewe folgenden Code aus der Datei `{dateiname}`:\n\n```\n{code}\n```"]

    for _ in range(MAX_ITERATIONEN):
        antwort = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=config,
        )

        aufrufe = _fn_calls(antwort)
        if not aufrufe:
            return antwort.text

        # Tool-Ergebnisse sammeln und als nächste Nachricht anhängen
        contents.append(antwort.candidates[0].content)
        fn_parts = []
        for fc in aufrufe:
            ergebnis = _ausfuehren(fc.name, dict(fc.args))
            fn_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": json.dumps(ergebnis, ensure_ascii=False)},
                )
            )
        contents.append(types.Content(role="user", parts=fn_parts))

    return "(Max. Iterationen erreicht)"


def review_stream(code: str, dateiname: str = "code.py") -> Generator[str, None, None]:
    """Streamt den Review-Prozess als Server-Sent Events."""
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[_build_tool()],
    )
    contents = [f"Bitte reviewe folgenden Code aus der Datei `{dateiname}`:\n\n```\n{code}\n```"]

    def event(data: dict) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    yield event({"type": "start", "dateiname": dateiname})

    for iteration in range(MAX_ITERATIONEN):
        yield event({"type": "thinking", "iteration": iteration + 1})

        antwort = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=config,
        )

        aufrufe = _fn_calls(antwort)
        if not aufrufe:
            yield event({"type": "report", "content": antwort.text})
            yield event({"type": "done"})
            return

        contents.append(antwort.candidates[0].content)
        fn_parts = []
        for fc in aufrufe:
            args = dict(fc.args)
            yield event({"type": "tool_call", "name": fc.name, "input": args})

            ergebnis = _ausfuehren(fc.name, args)
            yield event({"type": "tool_result", "name": fc.name, "result": ergebnis})

            fn_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": json.dumps(ergebnis, ensure_ascii=False)},
                )
            )
        contents.append(types.Content(role="user", parts=fn_parts))

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
