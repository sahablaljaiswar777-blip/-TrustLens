"""Small SQLite storage layer for analysis history."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ClosingConnection(sqlite3.Connection):
    """SQLite context manager that also releases its file handle on exit."""

    def __exit__(self, exception_type, exception_value, traceback):
        try:
            return super().__exit__(exception_type, exception_value, traceback)
        finally:
            self.close()


def get_connection(database_path: str) -> sqlite3.Connection:
    """Open a configured connection and ensure the parent folder exists."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path), factory=ClosingConnection)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path: str) -> None:
    """Create the analysis table and its recent-history index."""
    with get_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                title TEXT NOT NULL,
                preview TEXT NOT NULL,
                score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100),
                band TEXT NOT NULL,
                decision TEXT NOT NULL,
                result_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC)"
        )


def add_analysis(database_path: str, title: str, preview: str, result: Dict[str, Any]) -> int:
    """Persist a short preview and structured result, never full form contents."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (created_at, title, preview, score, band, decision, result_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp, title[:80], preview[:240], result["score"], result["band"],
                result["decision"], json.dumps(result, ensure_ascii=True),
            ),
        )
        return int(cursor.lastrowid)


def list_analyses(database_path: str, query: str = "", band: str = "") -> List[Dict[str, Any]]:
    """Return recent compact history rows with optional text and band filters."""
    sql = "SELECT id, created_at, title, preview, score, band, decision FROM analyses WHERE 1=1"
    params: List[Any] = []
    if query.strip():
        sql += " AND (title LIKE ? OR preview LIKE ?)"
        pattern = "%" + query.strip()[:80] + "%"
        params.extend([pattern, pattern])
    if band:
        sql += " AND band = ?"
        params.append(band)
    sql += " ORDER BY id DESC LIMIT 200"
    with get_connection(database_path) as connection:
        rows = connection.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def get_analysis(database_path: str, analysis_id: int) -> Optional[Dict[str, Any]]:
    """Fetch one analysis and decode its structured result."""
    with get_connection(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()
    if row is None:
        return None
    analysis = dict(row)
    analysis["result"] = json.loads(analysis.pop("result_json"))
    return analysis


def dashboard_stats(database_path: str) -> Dict[str, Any]:
    """Return aggregate counts for the dashboard."""
    with get_connection(database_path) as connection:
        total = connection.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        high_risk = connection.execute(
            "SELECT COUNT(*) FROM analyses WHERE score >= 80"
        ).fetchone()[0]
        trusted = connection.execute(
            "SELECT COUNT(*) FROM analyses WHERE score BETWEEN 0 AND 19"
        ).fetchone()[0]
        recent = connection.execute(
            "SELECT id, created_at, title, score, band FROM analyses ORDER BY id DESC LIMIT 5"
        ).fetchall()
    return {
        "total": total,
        "high_risk": high_risk,
        "trusted": trusted,
        "recent": [dict(row) for row in recent],
    }
