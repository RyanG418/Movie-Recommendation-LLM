from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any

from flask import Flask, render_template, request
import pandas as pd

# Fallback if tomllib not available
try:
    import tomllib
except Exception:
    import tomli as tomllib  # type: ignore

from data_loader import load_movielens_to_sqlite, fetch_tables
from recommender import MovieRecommender, RecsConfig
from llm import QueryLLM

app = Flask(__name__)

def load_config():
    cfg_path = "config.toml"
    if not os.path.exists(cfg_path):
        raise RuntimeError("Missing config.toml. Copy config.example.toml to config.toml and adjust paths.")
    with open(cfg_path, "rb") as f:
        return tomllib.load(f)

cfg = load_config()

# Initialize DB if needed
schema_sql = Path("schema.sql").read_text(encoding="utf-8")
sqlite_path = cfg["paths"]["sqlite_path"]
movielens_dir = cfg["paths"]["movielens_dir"]
cache_dir = cfg["paths"]["cache_dir"]

if not os.path.exists(sqlite_path):
    print("Loading MovieLens into SQLite...")
    load_movielens_to_sqlite(sqlite_path, movielens_dir, schema_sql)

movies_df, ratings_df, tags_df = fetch_tables(sqlite_path)

recs_cfg = RecsConfig(
    cache_dir=cache_dir,
    min_rating_count=cfg["recs"].get("min_rating_count", 20),
    top_k=cfg["recs"].get("top_k", 30),
    return_k=cfg["recs"].get("return_k", 10),
)
recommender = MovieRecommender(movies_df, ratings_df, tags_df, recs_cfg)
qllm = QueryLLM()

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/recommend")
def recommend():
    query_text = request.form.get("query", "").strip()
    parsed = qllm.parse_query(query_text)
    results = recommender.recommend(query_text, parsed)
    titles = results["title"].tolist()
    reasons = results["reason"].tolist()
    explanation = qllm.explain(query_text, titles, reasons)

    # Prepare for template
    rows = results.to_dict(orient="records")
    for r in rows:
        r["genres"] = (r["genres"] or "").replace("|", ", ")
        r["rating_mean"] = f"{r['rating_mean']:.2f}"
    return render_template("results.html", query=query_text, parsed=parsed, explanation=explanation, rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
