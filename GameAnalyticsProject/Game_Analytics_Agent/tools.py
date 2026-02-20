import re
import pandas as pd
import numpy as np
from typing import Optional

USD_TO_INR = 83.5

def _col(df, *candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def _to_records(df, limit=10):
    essential = [
        "app_id", "name", "genre", "price", "price_usd", "price_inr",
        "is_free", "release_year", "positive_ratio", "positive",
        "negative", "total_reviews", "developer", "publisher",
        "languages", "tags", "owners", "ccu"
    ]
    cols = [c for c in essential if c in df.columns]
    return (
        df.head(limit)[cols]
        .replace({np.nan: None})
        .to_dict(orient="records")
    )


# ── TOOL 1: Free vs Paid rating ───────────────────────────────────────────────
def compare_free_vs_paid_rating(df: pd.DataFrame) -> dict:
    rating_col = _col(df, "positive_ratio", "userscore")
    if not rating_col:
        return {"result": "No rating column found.", "records": {}}

    multiplier = 100 if rating_col == "positive_ratio" else 1
    free_vals  = df[df["is_free"] == True][rating_col].dropna()
    paid_vals  = df[df["is_free"] == False][rating_col].dropna()
    free_avg   = round(free_vals.mean() * multiplier, 2)
    paid_avg   = round(paid_vals.mean() * multiplier, 2)
    winner     = "Free" if free_avg > paid_avg else "Paid"

    result = (
        f"Free games average rating : {free_avg}%\n"
        f"Paid games average rating : {paid_avg}%\n"
        f"→ {winner} games have a higher average rating."
    )
    records = {
        "free_avg_rating":  free_avg,
        "paid_avg_rating":  paid_avg,
        "total_free_games": int(free_vals.count()),
        "total_paid_games": int(paid_vals.count()),
        "top_free_games":   _to_records(df[df["is_free"] == True].nlargest(5, rating_col)),
        "top_paid_games":   _to_records(df[df["is_free"] == False].nlargest(5, rating_col)),
    }
    return {"result": result, "records": records}


# ── TOOL 2: Count by genre + language ────────────────────────────────────────
def count_games_by_genre_and_language(df: pd.DataFrame, genre: str, language: str = "") -> dict:
    gcol = _col(df, "genre", "genres")
    if not gcol:
        return {"result": "No genre column found.", "records": {}}

    filtered = df[df[gcol].str.contains(genre, case=False, na=False)]

    if language:
        lcol = _col(df, "languages", "supported_languages")
        if lcol:
            filtered = filtered[filtered[lcol].str.contains(language, case=False, na=False)]

    lang_str = f" supporting {language}" if language else ""
    result   = f"Number of {genre} games{lang_str}: {len(filtered)}"
    return {"result": result, "records": _to_records(filtered, 10)}


# ── TOOL 3: Best games with filters ──────────────────────────────────────────
def find_best_games(df: pd.DataFrame,
                    genre: str = "",
                    tag: str = "",
                    after_year: Optional[int] = None,
                    multiplayer: bool = False,
                    limit: int = 10) -> dict:
    f = df.copy()
    gcol = _col(f, "genre", "genres")
    tcol = _col(f, "tags", "categories")

    if genre and gcol:
        f = f[f[gcol].str.contains(genre, case=False, na=False)]

    # tags column is a dict-string e.g. "{'Shooter': 1420, 'FPS': 2048}"
    if tag and tcol:
        f = f[f[tcol].str.contains(tag, case=False, na=False)]

    if multiplayer and tcol:
        f = f[f[tcol].str.contains("Multiplayer", case=False, na=False)]

    # Only apply year filter if release_year data actually exists
    has_year_data = "release_year" in f.columns and f["release_year"].notna().sum() > 100
    if after_year and has_year_data:
        f = f[f["release_year"] > after_year]

    if f.empty:
        return {"result": "No games found matching your criteria.", "records": []}

    rating_col = _col(f, "positive_ratio", "userscore")
    if rating_col:
        if "total_reviews" in f.columns:
            f = f[f["total_reviews"] >= 50]
        if not f.empty:
            f = f.nlargest(limit, rating_col)

    if f.empty:
        return {"result": "No games found matching your criteria.", "records": []}

    name_col   = _col(f, "name", "title")
    desc_parts = []
    if genre:       desc_parts.append(genre)
    if tag:         desc_parts.append(tag)
    if multiplayer: desc_parts.append("multiplayer")
    if after_year and has_year_data:
        desc_parts.append(f"released after {after_year}")
    desc = " ".join(desc_parts)

    result = f"Top {len(f)} {desc} games:\n"
    if name_col and rating_col:
        for _, row in f.iterrows():
            val  = row[rating_col]
            if rating_col == "positive_ratio":
                val = round(val * 100, 1)
            year = int(row["release_year"]) if pd.notna(row.get("release_year")) else "N/A"
            result += f"  • {row[name_col]} ({year}) — Rating: {val}%\n"

    return {"result": result.strip(), "records": _to_records(f, limit)}


# ── TOOL 4: Price lookup ──────────────────────────────────────────────────────
def get_game_price(df: pd.DataFrame, game_name: str) -> dict:
    name_col = _col(df, "name", "title")
    if not name_col:
        return {"result": "No name column found.", "records": {}}
    if not game_name.strip():
        return {"result": "No game name provided.", "records": {}}

    exact   = df[df[name_col].str.lower() == game_name.lower()]
    partial = df[df[name_col].str.contains(game_name, case=False, na=False, regex=False)]
    matches = exact if not exact.empty else partial

    # Fallback: word-by-word match
    if matches.empty:
        words = [w for w in game_name.split() if len(w) > 3]
        for word in words:
            matches = df[df[name_col].str.contains(word, case=False, na=False)]
            if not matches.empty:
                break

    if matches.empty:
        return {"result": f"No game found matching '{game_name}'.", "records": {}}

    lines   = []
    records = []
    for _, row in matches.head(5).iterrows():
        price_usd = float(row.get("price", 0) or 0)
        price_inr = round(price_usd * USD_TO_INR, 2)
        status    = "Free to Play" if price_usd == 0 else f"${price_usd:.2f} USD  |  ₹{price_inr:.2f} INR"
        lines.append(f"  • {row[name_col]}: {status}")
        records.append({
            "app_id":         row.get("app_id"),
            "name":           row[name_col],
            "price_usd":      price_usd,
            "price_inr":      price_inr,
            "is_free":        bool(row.get("is_free", False)),
            "genre":          row.get("genre"),
            "developer":      row.get("developer"),
            "release_year":   int(row["release_year"]) if pd.notna(row.get("release_year")) else None,
            "positive_ratio": round(row["positive_ratio"] * 100, 1)
                              if pd.notna(row.get("positive_ratio")) else None,
        })

    return {
        "result": "Price information:\n" + "\n".join(lines),
        "records": records
    }


# ── TOOL 5: General stats ─────────────────────────────────────────────────────
def general_stats(df: pd.DataFrame) -> dict:
    stats = {
        "total_games": len(df),
        "free_games":  int(df["is_free"].sum()),
        "paid_games":  int((~df["is_free"]).sum()),
    }

    if "release_year" in df.columns:
        yr = df["release_year"].dropna()
        if not yr.empty:
            stats["year_range"] = f"{int(yr.min())} – {int(yr.max())}"

    if "positive_ratio" in df.columns:
        stats["avg_positive_ratio_pct"] = round(df["positive_ratio"].mean() * 100, 2)

    if "price" in df.columns:
        paid = df[df["is_free"] == False]["price"].dropna()
        if not paid.empty:
            stats["avg_paid_price_usd"] = round(float(paid.mean()), 2)
            stats["max_price_usd"]      = round(float(paid.max()), 2)

    if "genre" in df.columns:
        top_genre = df["genre"].value_counts()
        if not top_genre.empty:
            stats["most_common_genre"] = top_genre.idxmax()

    if "total_reviews" in df.columns and "name" in df.columns:
        top = df[df["total_reviews"].notna()].nlargest(1, "total_reviews")
        if not top.empty:
            stats["most_reviewed_game"]  = top.iloc[0]["name"]
            stats["most_reviewed_count"] = int(top.iloc[0]["total_reviews"])

    if "ccu" in df.columns and "name" in df.columns:
        top_ccu = df[df["ccu"].notna()].nlargest(1, "ccu")
        if not top_ccu.empty:
            stats["highest_ccu_game"] = top_ccu.iloc[0]["name"]
            stats["highest_ccu"]      = int(top_ccu.iloc[0]["ccu"])

    return {
        "result": "\n".join(f"{k}: {v}" for k, v in stats.items()),
        "records": stats
    }


# ── TOOL 6: Games by developer ────────────────────────────────────────────────
def games_by_developer(df: pd.DataFrame, dev_name: str) -> dict:
    dcol = _col(df, "developer", "developers", "publisher", "publishers")
    if not dcol:
        return {"result": "No developer column found.", "records": {}}

    filtered   = df[df[dcol].str.contains(dev_name, case=False, na=False, regex=False)]
    rating_col = _col(filtered, "positive_ratio")
    if rating_col and not filtered.empty:
        filtered = filtered.nlargest(10, rating_col)

    return {
        "result": f"Found {len(filtered)} games by '{dev_name}'.",
        "records": _to_records(filtered, 10)
    }


# ── TOOL 7: Most popular games ────────────────────────────────────────────────
def most_popular_games(df: pd.DataFrame, by: str = "reviews", limit: int = 10) -> dict:
    name_col = _col(df, "name", "title")

    if by == "ccu" and "ccu" in df.columns:
        sort_col = "ccu"
        label    = "peak concurrent users"
    elif "total_reviews" in df.columns:
        sort_col = "total_reviews"
        label    = "total reviews"
    else:
        return {"result": "No popularity metric found.", "records": []}

    top = df[df[sort_col].notna()].nlargest(limit, sort_col)

    result = f"Top {len(top)} most popular games by {label}:\n"
    for _, row in top.iterrows():
        val    = int(row[sort_col])
        rating = round(row["positive_ratio"] * 100, 1) if pd.notna(row.get("positive_ratio")) else "N/A"
        result += f"  • {row[name_col]} — {label}: {val:,} | Rating: {rating}%\n"

    return {"result": result.strip(), "records": _to_records(top, limit)}
