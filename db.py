from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable, Tuple, Any

def get_conn(sqlite_path: str) -> sqlite3.Connection:
    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(sqlite_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def executescript(conn: sqlite3.Connection, sql_text: str) -> None:
    conn.executescript(sql_text)
    conn.commit()

def upsert_many(conn: sqlite3.Connection, table: str, cols: Iterable[str], rows: Iterable[Tuple[Any, ...]]):
    placeholders = ",".join("?" for _ in cols)
    col_list = ",".join(cols)
    sql = f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})"
    conn.executemany(sql, list(rows))
    conn.commit()
