"""SQLite-Datenbank für Review-Historie."""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "reviews.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                dateiname TEXT NOT NULL,
                modus     TEXT NOT NULL DEFAULT 'review',
                erstellt  TEXT NOT NULL,
                vorschau  TEXT NOT NULL
            )
        """)


def save_review(dateiname: str, modus: str, report: str) -> int:
    vorschau = report[:200].replace("\n", " ").strip()
    erstellt = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO reviews (dateiname, modus, erstellt, vorschau) VALUES (?,?,?,?)",
            (dateiname, modus, erstellt, vorschau),
        )
        return cur.lastrowid


def get_history(limit: int = 20) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, dateiname, modus, erstellt, vorschau FROM reviews ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
