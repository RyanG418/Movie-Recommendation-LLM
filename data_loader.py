from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import Tuple
from sqlalchemy import create_engine, text

from db import get_conn, executescript, upsert_many

def load_movielens_to_sqlite(sqlite_path: str, movielens_dir: str, schema_sql: str) -> None:
    conn = get_conn(sqlite_path)
    executescript(conn, schema_sql)

    mv_dir = Path(movielens_dir)
    movies = pd.read_csv(mv_dir / "movies.csv")        # movieId,title,genres
    ratings = pd.read_csv(mv_dir / "ratings.csv")      # userId,movieId,rating,timestamp
    tags = pd.read_csv(mv_dir / "tags.csv")            # userId,movieId,tag,timestamp

    # Extract year from title like "Toy Story (1995)"
    def extract_year(t):
        import re
        m = re.search(r"\((\d{4})\)\s*$", str(t))
        return int(m.group(1)) if m else None

    movies["year"] = movies["title"].apply(extract_year)

    upsert_many(
        conn,
        "movies",
        ["movieId", "title", "year", "genres"],
        movies[["movieId", "title", "year", "genres"]].itertuples(index=False, name=None),
    )

    upsert_many(
        conn,
        "ratings",
        ["userId", "movieId", "rating", "timestamp"],
        ratings[["userId", "movieId", "rating", "timestamp"]].itertuples(index=False, name=None),
    )

    if not tags.empty:
        upsert_many(
            conn,
            "tags",
            ["userId", "movieId", "tag", "timestamp"],
            tags[["userId", "movieId", "tag", "timestamp"]].itertuples(index=False, name=None),
        )

def fetch_tables(sqlite_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    engine = create_engine(f"sqlite:///{sqlite_path}")
    with engine.begin() as con:
        movies = pd.read_sql(text("SELECT * FROM movies"), con)
        ratings = pd.read_sql(text("SELECT * FROM ratings"), con)
        tags = pd.read_sql(text("SELECT * FROM tags"), con)
    return movies, ratings, tags
