"""Unit-Tests für root/werkzeuge.py."""

import importlib.util
import pathlib

import pytest


def _lade_werkzeuge():
    pfad = pathlib.Path(__file__).parent.parent / "werkzeuge.py"
    spec = importlib.util.spec_from_file_location("root_werkzeuge", pfad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_wz = _lade_werkzeuge()


def test_muster_suchen_findet_treffer():
    result = _wz.muster_suchen("x = 1\ny = 2\n", r"x")
    assert result["anzahl"] == 1
    assert result["treffer"][0]["zeile"] == 1


def test_muster_suchen_kein_treffer():
    result = _wz.muster_suchen("a = 1", r"z")
    assert result["anzahl"] == 0
    assert result["treffer"] == []


def test_muster_suchen_ungueltiges_muster():
    result = _wz.muster_suchen("code", r"[ungültig")
    assert "fehler" in result


def test_muster_suchen_mehrere_treffer():
    code = "foo = 1\nbar = 2\nfoo = 3"
    result = _wz.muster_suchen(code, r"foo")
    assert result["anzahl"] == 2


def test_datei_lesen_nicht_gefunden():
    result = _wz.datei_lesen("nicht_vorhanden_xyz.py")
    assert "fehler" in result


def test_datei_lesen_path_traversal_geblockt():
    result = _wz.datei_lesen("../../../etc/passwd")
    assert "fehler" in result
    assert "verweigert" in result["fehler"].lower() or "außerhalb" in result["fehler"].lower()
