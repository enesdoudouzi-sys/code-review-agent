"""Werkzeuge, die der Code-Review-Agent aufrufen kann."""

import re


def code_analysieren(code: str) -> dict:
    """Gibt Metadaten über den Code zurück (Zeilen, Funktionen, Klassen)."""
    zeilen = code.splitlines()
    funktionen = [z.strip() for z in zeilen if re.match(r"^\s*def ", z)]
    klassen = [z.strip() for z in zeilen if re.match(r"^\s*class ", z)]
    return {
        "zeilen_gesamt": len(zeilen),
        "funktionen": funktionen,
        "klassen": klassen,
    }


def muster_suchen(code: str, muster: str) -> dict:
    """Sucht ein Regex-Muster im Code und gibt alle Treffer mit Zeilennummer zurück."""
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
        "name": "code_analysieren",
        "description": "Analysiert den Code-String und gibt Metadaten zurück: Zeilenanzahl, Funktionen, Klassen.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Der vollständige Code-String."}
            },
            "required": ["code"],
        },
    },
    {
        "name": "muster_suchen",
        "description": "Sucht mit einem regulären Ausdruck im Code und gibt Treffer mit Zeilennummer zurück.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Der Code-String."},
                "muster": {"type": "string", "description": "Regulärer Ausdruck (Python re-Syntax)."},
            },
            "required": ["code", "muster"],
        },
    },
]

WERKZEUG_MAP = {
    "code_analysieren": code_analysieren,
    "muster_suchen": muster_suchen,
}
