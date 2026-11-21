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


def komplexitaet_messen(code: str) -> dict:
    """Misst Verschachtelungstiefe und Komplexität pro Funktion."""
    zeilen = code.splitlines()
    max_tiefe = 0
    funktionen = []
    aktuelle_funktion = None
    funktion_tiefe = 0

    for zeile in zeilen:
        stripped = zeile.lstrip()
        einrueckung = (len(zeile) - len(stripped)) // 4
        max_tiefe = max(max_tiefe, einrueckung)

        if re.match(r"def \w+\s*\(", stripped):
            if aktuelle_funktion:
                funktionen.append({"name": aktuelle_funktion, "max_tiefe": funktion_tiefe})
            aktuelle_funktion = stripped.split("(")[0].replace("def ", "")
            funktion_tiefe = einrueckung
        elif aktuelle_funktion:
            funktion_tiefe = max(funktion_tiefe, einrueckung)

    if aktuelle_funktion:
        funktionen.append({"name": aktuelle_funktion, "max_tiefe": funktion_tiefe})

    hohe_komplexitaet = [f for f in funktionen if f["max_tiefe"] > 3]
    return {
        "max_verschachtelungstiefe": max_tiefe,
        "funktionen": funktionen,
        "hohe_komplexitaet": hohe_komplexitaet,
        "warnung": len(hohe_komplexitaet) > 0,
    }


_UNSICHERE_MUSTER = {
    r"\beval\s*\(": "eval() führt beliebigen Code aus — kritisches Sicherheitsrisiko",
    r"\bexec\s*\(": "exec() führt beliebigen Code aus — kritisches Sicherheitsrisiko",
    r"\bpickle\.loads?\s*\(": "pickle kann zu Remote Code Execution führen",
    r"\bos\.system\s*\(": "os.system() führt Shell-Befehle aus",
    r"\bsubprocess\.call\s*\(.*shell\s*=\s*True": "subprocess mit shell=True ist unsicher",
    r"(?i)password\s*=\s*['\"][^'\"]+['\"]": "Hardcodiertes Passwort gefunden",
    r"(?i)secret\s*=\s*['\"][^'\"]+['\"]": "Hardcodiertes Secret gefunden",
    r"(?i)api_key\s*=\s*['\"][^'\"]+['\"]": "Hardcodierter API-Key gefunden",
    r"\b__import__\s*\(": "__import__() kann für Code-Injection missbraucht werden",
    r"(?i)verify\s*=\s*False": "SSL-Zertifikat-Validierung deaktiviert",
}


def abhaengigkeiten_pruefen(code: str) -> dict:
    """Prüft den Code auf bekannte Sicherheitsprobleme und unsichere Muster."""
    warnungen = []
    for muster, beschreibung in _UNSICHERE_MUSTER.items():
        for i, zeile in enumerate(code.splitlines()):
            if re.search(muster, zeile):
                warnungen.append({
                    "zeile": i + 1,
                    "problem": beschreibung,
                    "code": zeile.strip(),
                })
    return {
        "warnungen": warnungen,
        "anzahl": len(warnungen),
        "sicher": len(warnungen) == 0,
    }


def testabdeckung_pruefen(code: str) -> dict:
    """Prüft ob öffentliche Funktionen Tests haben."""
    alle_funktionen = re.findall(r"^\s*def (\w+)\s*\(", code, re.MULTILINE)
    oeffentliche = [f for f in alle_funktionen if not f.startswith("_") and not f.startswith("test_")]
    test_funktionen = [f for f in alle_funktionen if f.startswith("test_")]

    getestet = []
    ungetestet = []
    for f in oeffentliche:
        hat_test = any(f.lower() in t.lower() for t in test_funktionen)
        (getestet if hat_test else ungetestet).append(f)

    total = len(oeffentliche)
    abdeckung = round(len(getestet) / total * 100) if total > 0 else 100

    return {
        "funktionen_gesamt": total,
        "getestet": getestet,
        "ungetestet": ungetestet,
        "abdeckung_prozent": abdeckung,
    }


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
    {
        "name": "komplexitaet_messen",
        "description": "Misst die Verschachtelungstiefe und Komplexität des Codes. Warnt bei Funktionen mit Tiefe > 3.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Der vollständige Code-String."}
            },
            "required": ["code"],
        },
    },
    {
        "name": "abhaengigkeiten_pruefen",
        "description": "Prüft den Code auf bekannte Sicherheitsprobleme: eval, exec, pickle, hardcodierte Secrets, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Der vollständige Code-String."}
            },
            "required": ["code"],
        },
    },
    {
        "name": "testabdeckung_pruefen",
        "description": "Prüft ob öffentliche Funktionen entsprechende Test-Funktionen haben.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Der vollständige Code-String."}
            },
            "required": ["code"],
        },
    },
]

WERKZEUG_MAP = {
    "code_analysieren": code_analysieren,
    "muster_suchen": muster_suchen,
    "komplexitaet_messen": komplexitaet_messen,
    "abhaengigkeiten_pruefen": abhaengigkeiten_pruefen,
    "testabdeckung_pruefen": testabdeckung_pruefen,
}
