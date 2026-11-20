"""Datenbank-Backend: Supabase (PostgreSQL) mit SQLite-Fallback für lokale Entwicklung."""

import os
import sqlite3
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL auf Supabase
DB_PATH = os.getenv("DB_PATH", "reviews.db")  # SQLite-Fallback


def _use_postgres() -> bool:
    return bool(DATABASE_URL)


# ── PostgreSQL (Supabase) ─────────────────────────────────────────────────────

def _pg_connect():
    import psycopg2
    import psycopg2.extras
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def _pg_init() -> None:
    with _pg_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id        SERIAL PRIMARY KEY,
                    dateiname TEXT NOT NULL,
                    modus     TEXT NOT NULL DEFAULT 'review',
                    erstellt  TEXT NOT NULL,
                    vorschau  TEXT NOT NULL
                )
            """)
        conn.commit()


def _pg_save(dateiname: str, modus: str, vorschau: str, erstellt: str) -> int:
    with _pg_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO reviews (dateiname, modus, erstellt, vorschau) VALUES (%s,%s,%s,%s) RETURNING id",
                (dateiname, modus, erstellt, vorschau),
            )
            row_id = cur.fetchone()[0]
        conn.commit()
    return row_id


def _pg_history(limit: int) -> list[dict]:
    with _pg_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, dateiname, modus, erstellt, vorschau FROM reviews ORDER BY id DESC LIMIT %s",
                (limit,),
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


# ── SQLite (Fallback) ─────────────────────────────────────────────────────────

def _sqlite_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _sqlite_init() -> None:
    with _sqlite_connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                dateiname TEXT NOT NULL,
                modus     TEXT NOT NULL DEFAULT 'review',
                erstellt  TEXT NOT NULL,
                vorschau  TEXT NOT NULL
            )
        """)


def _sqlite_save(dateiname: str, modus: str, vorschau: str, erstellt: str) -> int:
    with _sqlite_connect() as conn:
        cur = conn.execute(
            "INSERT INTO reviews (dateiname, modus, erstellt, vorschau) VALUES (?,?,?,?)",
            (dateiname, modus, erstellt, vorschau),
        )
        return cur.lastrowid


def _sqlite_history(limit: int) -> list[dict]:
    with _sqlite_connect() as conn:
        rows = conn.execute(
            "SELECT id, dateiname, modus, erstellt, vorschau FROM reviews ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Öffentliche API ───────────────────────────────────────────────────────────

def init_db() -> None:
    if _use_postgres():
        _pg_init()
    else:
        _sqlite_init()


def save_review(dateiname: str, modus: str, report: str) -> int:
    vorschau = report[:200].replace("\n", " ").strip()
    erstellt = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    if _use_postgres():
        return _pg_save(dateiname, modus, vorschau, erstellt)
    return _sqlite_save(dateiname, modus, vorschau, erstellt)


def get_history(limit: int = 20) -> list[dict]:
    if _use_postgres():
        return _pg_history(limit)
    return _sqlite_history(limit)
