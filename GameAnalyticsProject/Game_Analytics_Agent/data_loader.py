import re
import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def find_id_column(df):
    for candidate in ["app_id", "appid", "id", "steam_appid", "gameid", "game_id"]:
        if candidate in df.columns:
            return candidate
    return None

def load_data() -> pd.DataFrame:
    game_ids_path  = os.path.join(DATA_DIR, "game_ids.csv")
    add_data_path  = os.path.join(DATA_DIR, "additional_data.csv")
    game_data_path = os.path.join(DATA_DIR, "game_data.csv")

    # ── Load the two small files ───────────────────────────────────────────
    game_ids = pd.read_csv(game_ids_path)
    add_data = pd.read_csv(add_data_path)

    for df in [game_ids, add_data]:
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    for df in [game_ids, add_data]:
        id_col = find_id_column(df)
        if id_col and id_col != "app_id":
            df.rename(columns={id_col: "app_id"}, inplace=True)

    # ── Merge game_ids + additional_data ──────────────────────────────────
    df = game_ids.merge(add_data, on="app_id", how="left")

    # Fix duplicate name columns produced by merge
    if "name_x" in df.columns:
        df["name"] = df["name_x"].fillna(df.get("name_y", ""))
        df.drop(columns=["name_x", "name_y"], inplace=True, errors="ignore")

    # ── Try loading game_data.csv (large ~270MB, optional) ────────────────
    if os.path.exists(game_data_path):
        try:
            print("[data_loader] Loading game_data.csv (this may take a moment)...")
            game_data = pd.read_csv(game_data_path, low_memory=False)
            game_data.columns = game_data.columns.str.strip().str.lower().str.replace(" ", "_")

            id_col = find_id_column(game_data)
            if id_col and id_col != "app_id":
                game_data.rename(columns={id_col: "app_id"}, inplace=True)

            # Keep only useful columns to save memory
            useful = ["app_id", "release_date", "supported_languages",
                      "categories", "genres", "platforms", "metacritic"]
            useful = [c for c in useful if c in game_data.columns]
            game_data = game_data[useful]

            df = df.merge(game_data, on="app_id", how="left", suffixes=("", "_gd"))

            # Parse release_date: stored as "{'date': 'Nov 8, 2004', 'coming_soon': False}"
            if "release_date" in df.columns:
                def extract_date(val):
                    if pd.isna(val):
                        return None
                    s = str(val)
                    m = re.search(r"'date':\s*'([^']+)'", s)
                    return m.group(1) if m else None

                df["release_date"] = df["release_date"].apply(extract_date)
                df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
                df["release_year"] = df["release_date"].dt.year
                valid = df["release_year"].dropna()
                if not valid.empty:
                    print(f"[data_loader] Release years: {int(valid.min())} – {int(valid.max())}")

            print("[data_loader] game_data.csv merged ✅")
        except Exception as e:
            print(f"[data_loader] Could not load game_data.csv: {e}")
    else:
        print("[data_loader] game_data.csv not found — using 2 CSVs only.")

    # Ensure release_year exists even without game_data
    if "release_year" not in df.columns:
        df["release_year"] = None

    # ── Price fix: additional_data stores price in CENTS → divide by 100 ─
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0) / 100
    else:
        df["price"] = 0.0

    # ── is_free flag ──────────────────────────────────────────────────────
    if "is_free" in df.columns and df["is_free"].dtype == object:
        df["is_free"] = df["is_free"].astype(str).str.lower().isin(["true", "1", "yes"])
    elif "is_free" in df.columns:
        df["is_free"] = df["is_free"].astype(bool)
    else:
        df["is_free"] = df["price"] == 0.0

    # ── Fill missing text columns ─────────────────────────────────────────
    for col in ["developer", "publisher", "genre", "languages", "name"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # ── Numeric columns ───────────────────────────────────────────────────
    for col in ["positive", "negative", "userscore", "score_rank",
                "average_forever", "median_forever", "initialprice", "discount", "ccu"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Ratings ───────────────────────────────────────────────────────────
    if "positive" in df.columns and "negative" in df.columns:
        df["total_reviews"] = df["positive"].fillna(0) + df["negative"].fillna(0)
        df["positive_ratio"] = np.where(
            df["total_reviews"] > 0,
            df["positive"] / df["total_reviews"],
            np.nan
        )

    df.drop_duplicates(subset=["app_id"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"[data_loader] ✅ Loaded {len(df)} games")
    print(f"[data_loader] Columns: {list(df.columns)}")
    return df
