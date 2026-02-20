import os
import re
import json
from dotenv import load_dotenv
from groq import Groq
from data_loader import load_data
from tools import (
    compare_free_vs_paid_rating,
    count_games_by_genre_and_language,
    find_best_games,
    get_game_price,
    general_stats,
    games_by_developer,
    most_popular_games,
)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are a Game Analytics assistant working with a Steam games dataset.
Given a user question, output ONLY a JSON object choosing one tool and its parameters.

Available tools:
1. compare_free_vs_paid_rating       — params: {}
2. count_games_by_genre_and_language — params: {"genre": str, "language": str}
3. find_best_games                   — params: {"genre": str, "tag": str, "after_year": int|null, "multiplayer": bool, "limit": int}
4. get_game_price                    — params: {"game_name": str}
5. general_stats                     — params: {}
6. games_by_developer                — params: {"dev_name": str}
7. most_popular_games                — params: {"by": "reviews"|"ccu", "limit": int}

Rules:
- "most popular", "most played", "top game on steam", "most reviewed", "best game" → most_popular_games
- "best multiplayer shooters after 2015" → find_best_games with tag="Shooter", multiplayer=true, after_year=2015
- "price of X" or "how much does X cost" → get_game_price, game_name = game title only (no extra words)
- "how many X games support Y language" → count_games_by_genre_and_language
- "do free games have higher ratings" or "free vs paid" → compare_free_vs_paid_rating
- "games by X" or "developed by X" or "made by X" → games_by_developer
- "total games", "statistics", "overview", "dataset summary" → general_stats
- Output ONLY valid JSON, no markdown, no explanation.

Examples:
{"tool": "most_popular_games", "params": {"by": "reviews", "limit": 10}}
{"tool": "find_best_games", "params": {"genre": "Action", "tag": "Shooter", "after_year": 2015, "multiplayer": true, "limit": 10}}
{"tool": "get_game_price", "params": {"game_name": "Counter-Strike"}}
{"tool": "get_game_price", "params": {"game_name": "DOTA 2"}}
{"tool": "count_games_by_genre_and_language", "params": {"genre": "Action", "language": "Korean"}}
{"tool": "games_by_developer", "params": {"dev_name": "Valve"}}
{"tool": "compare_free_vs_paid_rating", "params": {}}
"""

class GameAnalyticsAgent:
    def __init__(self):
        self.df = load_data()
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        if not self.client:
            print("[agent] WARNING: GROQ_API_KEY not set. Using rule-based fallback.")

    def _classify_with_llm(self, query):
        resp = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": query},
            ],
            temperature=0,
            max_tokens=200,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Non-JSON response: {raw}")

    def _classify_fallback(self, query):
        q = query.lower()

        if any(k in q for k in ["most popular", "most played", "top game", "highest rated",
                                  "most reviewed", "best game on steam"]):
            return {"tool": "most_popular_games", "params": {"by": "reviews", "limit": 10}}

        if any(k in q for k in ["free", "paid", "higher rating", "average rating",
                                  "free vs paid", "do free"]):
            return {"tool": "compare_free_vs_paid_rating", "params": {}}

        if any(k in q for k in ["price", "how much", "cost", "inr", "usd", "rupee"]):
            m = (re.search(r"price of (.+?)(?:\s+game|\s+in|\?|$)", q) or
                 re.search(r"(?:of|for)\s+(.+?)(?:\s+in|\s+game|\?|$)", q) or
                 re.search(r"(?:cost|price)\s+(?:of\s+)?([a-z0-9 :'\-]+?)(?:\s+in|\?|$)", q))
            game = m.group(1).strip() if m else query
            game = re.sub(r"\b(game|the|a|an|what|is|tell|me)\b", "", game).strip()
            return {"tool": "get_game_price", "params": {"game_name": game}}

        if re.search(r"how many|count|number of", q):
            genre = _guess_genre(q)
            lang  = _extract_language(q)
            return {"tool": "count_games_by_genre_and_language",
                    "params": {"genre": genre, "language": lang}}

        if any(k in q for k in ["best", "top", "recommend", "multiplayer", "shooter", "fps"]):
            genre       = _guess_genre(q)
            tag         = "Shooter" if ("shooter" in q or "fps" in q) else ""
            after_year  = _extract_year(q)
            multiplayer = any(k in q for k in ["multiplayer", "multi-player", "multi player"])
            return {"tool": "find_best_games", "params": {
                "genre": genre, "tag": tag,
                "after_year": after_year,
                "multiplayer": multiplayer,
                "limit": 10
            }}

        if any(k in q for k in ["developer", "studio", "made by", "developed by",
                                  "publisher", "games by"]):
            m = re.search(r"(?:by|from|developer|studio|publisher|developed by|games by)\s+(.+?)(?:\?|$)", q)
            return {"tool": "games_by_developer",
                    "params": {"dev_name": m.group(1).strip() if m else ""}}

        if any(k in q for k in ["total", "statistic", "overview", "how many games",
                                  "dataset", "summary"]):
            return {"tool": "general_stats", "params": {}}

        # Default
        return {"tool": "most_popular_games", "params": {"by": "reviews", "limit": 10}}

    def _dispatch(self, tool_name, params):
        df = self.df
        dispatch = {
            "compare_free_vs_paid_rating":
                lambda: compare_free_vs_paid_rating(df),
            "count_games_by_genre_and_language":
                lambda: count_games_by_genre_and_language(
                    df, params.get("genre", ""), params.get("language", "")),
            "find_best_games":
                lambda: find_best_games(
                    df,
                    genre       = params.get("genre", ""),
                    tag         = params.get("tag", ""),
                    after_year  = params.get("after_year"),
                    multiplayer = params.get("multiplayer", False),
                    limit       = params.get("limit", 10)),
            "get_game_price":
                lambda: get_game_price(df, params.get("game_name", "")),
            "general_stats":
                lambda: general_stats(df),
            "games_by_developer":
                lambda: games_by_developer(df, params.get("dev_name", "")),
            "most_popular_games":
                lambda: most_popular_games(
                    df,
                    by    = params.get("by", "reviews"),
                    limit = params.get("limit", 10)),
        }
        fn = dispatch.get(tool_name)
        return fn() if fn else {"result": f"Unknown tool: {tool_name}", "records": {}}

    def answer(self, query):
        try:
            plan = self._classify_with_llm(query) if self.client else self._classify_fallback(query)
        except Exception as e:
            print(f"[agent] LLM error: {e}. Using fallback.")
            plan = self._classify_fallback(query)

        print(f"[agent] Tool: {plan.get('tool')} | Params: {plan.get('params')}")
        result = self._dispatch(plan.get("tool", "general_stats"), plan.get("params", {}))
        return {
            "response": result.get("result", "No result."),
            "metadata": result.get("records", {})
        }


# ── Helpers ───────────────────────────────────────────────────────────────────
def _guess_genre(text):
    for g in ["action", "rpg", "shooter", "strategy", "adventure",
              "indie", "sports", "racing", "simulation", "horror", "puzzle"]:
        if g in text.lower():
            return g.capitalize()
    return ""

def _extract_language(text):
    for lang in ["korean", "japanese", "chinese", "french", "german",
                 "spanish", "portuguese", "russian", "arabic", "thai",
                 "turkish", "italian", "dutch", "polish", "hindi"]:
        if lang in text.lower():
            return lang.capitalize()
    return ""

def _extract_year(text):
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return int(m.group()) if m else None
