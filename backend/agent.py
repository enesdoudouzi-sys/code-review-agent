"""Code-Review-Agent – agentic loop mit Google Gemini API und Tool Use."""

import json
import os
from typing import Generator

import google.generativeai as genai
from google.generativeai import protos

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


def _build_tool() -> protos.Tool:
    """Konvertiert unsere Werkzeug-Definitionen in eine Gemini Tool-Definition."""
    declarations = []
    for w in WERKZEUG_DEFINITIONEN:
        props = {}
        for name, schema in w["input_schema"]["properties"].items():
            props[name] = protos.Schema(
                type=protos.Type.STRING,
                description=schema.get("description", ""),
            )
        declarations.append(
            protos.FunctionDeclaration(
                name=w["name"],
                description=w["description"],
                parameters=protos.Schema(
                    type=protos.Type.OBJECT,
                    properties=props,
                    required=w["input_schema"].get("required", []),
                ),
            )
        )
    return protos.Tool(function_declarations=declarations)


def _get_model() -> genai.GenerativeModel:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    return genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=SYSTEM_PROMPT,
        tools=[_build_tool()],
    )


def _ausfuehren(name: str, args: dict) -> dict:
    funktion = WERKZEUG_MAP.get(name)
    if funktion:
        return funktion(**args)
    return {"fehler": f"Unbekanntes Werkzeug: {name}"}


def _fn_calls(antwort) -> list:
    """Gibt alle Teile mit einem echten function_call zurück."""
    result = []
    for part in antwort.parts:
        try:
            if part.function_call.name:
                result.append(part)
        except Exception:
            pass
    return result


def review(code: str, dateiname: str = "code.py") -> str:
    """Führt einen vollständigen Code-Review durch und gibt den Report zurück."""
    model = _get_model()
    contents = [
        {
            "role": "user",
            "parts": [f"Bitte reviewe folgenden Code aus der Datei `{dateiname}`:\n\n```\n{code}\n```"],
        }
    ]

    for _ in range(MAX_ITERATIONEN):
        antwort = model.generate_content(contents)
        contents.append({"role": "model", "parts": antwort.parts})

        aufrufe = _fn_calls(antwort)
        if not aufrufe:
            return antwort.text

        fn_responses = []
        for part in aufrufe:
            fc = part.function_call
            ergebnis = _ausfuehren(fc.name, dict(fc.args))
            fn_responses.append(
                protos.Part(
                    function_response=protos.FunctionResponse(
                        name=fc.name,
                        response={"result": json.dumps(ergebnis, ensure_ascii=False)},
                    )
                )
            )
        contents.append({"role": "user", "parts": fn_responses})

    return "(Max. Iterationen erreicht)"


def review_stream(code: str, dateiname: str = "code.py") -> Generator[str, None, None]:
    """Streamt den Review-Prozess als Server-Sent Events."""
    model = _get_model()
    contents = [
        {
            "role": "user",
            "parts": [f"Bitte reviewe folgenden Code aus der Datei `{dateiname}`:\n\n```\n{code}\n```"],
        }
    ]

    def event(data: dict) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    yield event({"type": "start", "dateiname": dateiname})

    for iteration in range(MAX_ITERATIONEN):
        yield event({"type": "thinking", "iteration": iteration + 1})

        antwort = model.generate_content(contents)
        contents.append({"role": "model", "parts": antwort.parts})

        aufrufe = _fn_calls(antwort)
        if not aufrufe:
            yield event({"type": "report", "content": antwort.text})
            yield event({"type": "done"})
            return

        fn_responses = []
        for part in aufrufe:
            fc = part.function_call
            args = dict(fc.args)

            yield event({"type": "tool_call", "name": fc.name, "input": args})

            ergebnis = _ausfuehren(fc.name, args)

            yield event({"type": "tool_result", "name": fc.name, "result": ergebnis})

            fn_responses.append(
                protos.Part(
                    function_response=protos.FunctionResponse(
                        name=fc.name,
                        response={"result": json.dumps(ergebnis, ensure_ascii=False)},
                    )
                )
            )
        contents.append({"role": "user", "parts": fn_responses})

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
