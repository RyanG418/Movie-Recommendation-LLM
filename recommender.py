from __future__ import annotations
from typing import Dict, Any
import json
import os
import sys

# Fallback if tomllib not available (py<3.11)
try:
    import tomllib
except Exception:
    import tomli as tomllib  # type: ignore

from llama_cpp import Llama

class QueryLLM:
    """
    Thin wrapper around llama-cpp to:
    1) Parse free-text queries into structured filters (JSON).
    2) Generate natural-language rationales for recommendations.
    """

    def __init__(self, config_path: str = "config.toml"):
        with open(config_path, "rb") as f:
            cfg = tomllib.load(f)
        llm_cfg = cfg.get("llm", {})
        model_path = llm_cfg.get("model_path")
        if not model_path or not os.path.exists(model_path):
            # Defer initialize; operate in heuristic-only mode
            self.llm = None
            self.cfg = llm_cfg
            return

        self.llm = Llama(
            model_path=model_path,
            n_ctx=llm_cfg.get("n_ctx", 4096),
            n_threads=llm_cfg.get("n_threads", None),
            n_gpu_layers=llm_cfg.get("n_gpu_layers", 0),
            verbose=False,
        )
        self.cfg = llm_cfg

    def parse_query(self, text: str) -> Dict[str, Any]:
        """
        Return a dict like:
        {
          "genres": ["sci-fi","thriller"],
          "min_year": 2000,
          "max_year": 2022,
          "max_runtime": 130,
          "include_keywords": ["time travel","heist"],
          "exclude_keywords": ["horror"]
        }
        """
        # Heuristic fallback if no model
        base = {"genres": [], "min_year": None, "max_year": None, "max_runtime": None,
                "include_keywords": [], "exclude_keywords": []}
        if self.llm is None:
            # naive parse
            t = text.lower()
            for g in ["action","adventure","animation","children","comedy","crime","documentary","drama",
                      "fantasy","film-noir","horror","musical","mystery","romance","sci-fi","thriller","war","western"]:
                if g in t:
                    base["genres"].append(g)
            import re
            yrs = [int(x) for x in re.findall(r"(19|20)\d{2}", t)]
            if yrs:
                base["min_year"] = min(yrs)
                base["max_year"] = max(yrs)
            if "short" in t or "under" in t:
                m = re.search(r"(?:under|<|less than)\s*(\d{2,3})\s*min", t)
                base["max_runtime"] = int(m.group(1)) if m else 120
            # crude include/exclude
            if "not scary" in t or "no horror" in t:
                base["exclude_keywords"].append("horror")
            return base

        system = (
            "You convert user movie requests into a strict, compact JSON object "
            'with keys: genres (array of lowercase MovieLens genres), min_year, max_year, '
            "max_runtime (minutes), include_keywords (array), exclude_keywords (array). "
            "Only output JSON. If a field is unknown, use null or empty array."
        )
        user = f"Query: {text}"

        out = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=self.cfg.get("temperature", 0.2),
            top_p=self.cfg.get("top_p", 0.9),
        )
        content = out["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except Exception:
            return base

    def explain(self, query_text: str, titles: list[str], reasons: list[str]) -> str:
        if self.llm is None:
            return "Recommendations based on your request and similarity of genres, tags, and popularity."
        prompt = (
            "Write a short, friendly explanation (2–3 sentences) for the following movie recommendations. "
            f"User query: {query_text}\n"
            f"Movies: {', '.join(titles)}\n"
            "Reasons (per movie, terse phrases):\n- " + "\n- ".join(reasons)
        )
        out = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": "You write concise, helpful explanations for recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.cfg.get("temperature", 0.4),
            top_p=self.cfg.get("top_p", 0.9),
        )
        return out["choices"][0]["message"]["content"].strip()
