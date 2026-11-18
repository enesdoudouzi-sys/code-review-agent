"""Werkzeuge, die der Code-Review-Agent aufrufen kann."""

import re
from pathlib import Path


def datei_lesen(pfad: str) -> dict:
    try:
        inhalt = Path(pfad).read_text(encoding="utf-8")
        return {"inhalt": inhalt, "zeilen": inhalt.count("\n") + 1}
    except FileNotFoundError:
        return {"fehler": f"Datei nicht gefunden: {pfad}"}
    except Exception as e:
        return {"fehler": str(e)}


def muster_suchen(code: str, muster: str) -> dict:
    try:
        treffer = [
            {"zeile": i + 1, "text": zeile.strip()}
            for i, zeile in enumerate(code.splitlines())
            if re.search(muster, zeile)
        ]
        return {"treffer": treffer, "anzahl": len(treffer)}
    except re.error as e:
        return {"fehler": f"Ungültiges Muster: {e}"}


WERKZEUG_DEFINITIONEN = [
    {
        "name": "datei_lesen",
        "description": "Liest den Inhalt einer lokalen Code-Datei.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pfad": {
                    "type": "string",
                    "description": "Relativer oder absoluter Pfad zur Datei.",
                }
            },
            "required": ["pfad"],
        },
    },
    {
        "name": "muster_suchen",
        "description": "Sucht mit einem regulären Ausdruck im gegebenen Code-String.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Der Code-String, in dem gesucht wird.",
                },
                "muster": {
                    "type": "string",
                    "description": "Regulärer Ausdruck (Python re-Syntax).",
                },
            },
            "required": ["code", "muster"],
        },
    },
]

WERKZEUG_MAP = {
    "datei_lesen": datei_lesen,
    "muster_suchen": muster_suchen,
}
