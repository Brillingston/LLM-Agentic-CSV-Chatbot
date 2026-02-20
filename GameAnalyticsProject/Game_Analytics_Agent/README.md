# 🎮 Game Analytics Agent

An AI-powered analytics agent that answers natural language questions about Steam games using Groq LLM + pandas, exposed via a FastAPI REST endpoint.

---

## 📁 Project Structure

```
GameAnalyticsProject/
│
├── EDA_notebook.ipynb               ← Data exploration, cleaning & analysis
├── README.md                        ← This file
├── .gitignore
│
└── Game_Analytics_Agent/
    ├── main.py                      ← FastAPI app (POST /game/analytics)
    ├── agent.py                     ← LLM routing + fallback logic
    ├── data_loader.py               ← CSV loading, merging & cleaning
    ├── tools.py                     ← 7 pandas analytics tool functions
    ├── requirements.txt             ← Python dependencies
    ├── .env                         ← API keys (not committed to git)
    ├── .env.example                 ← Template for .env
    └── data/                        ← Place your CSV files here
        ├── game_ids.csv
        ├── additional_data.csv
        └── game_data.csv            ← Optional (~270MB), enables release year filtering
```

---

## ⚙️ Setup & Installation

### 1. Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
cd Game_Analytics_Agent
pip install -r requirements.txt
```

### 3. Add CSV data files

Place the 3 CSV files inside the `data/` folder:

```
Game_Analytics_Agent/data/game_ids.csv
Game_Analytics_Agent/data/additional_data.csv
Game_Analytics_Agent/data/game_data.csv      ← optional but recommended
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Get a free Groq API key at → https://console.groq.com

### 5. Run the server

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
[data_loader] ✅ Loaded 29235 games
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

## 🚀 API Usage

### Endpoint

```
POST http://127.0.0.1:8000/game/analytics
Content-Type: application/json
```

### Request Format

```json
{
  "query": "Your question here"
}
```

### Response Format

```json
{
  "response": "Human readable answer",
  "metadata": { }
}
```

---

## 🧪 Sample Queries & Responses

### Query 1 — Free vs Paid Ratings
```json
{ "query": "Do free games have higher ratings on average than paid games?" }
```
```json
{
  "response": "Free games average rating : 70.3%\nPaid games average rating : 71.3%\n→ Paid games have a higher average rating.",
  "metadata": {
    "free_avg_rating": 70.3,
    "paid_avg_rating": 71.3,
    "total_free_games": 3652,
    "total_paid_games": 25554,
    "top_free_games": [...],
    "top_paid_games": [...]
  }
}
```

### Query 2 — Genre + Language Count
```json
{ "query": "How many Action games support Korean?" }
```
```json
{
  "response": "Number of Action games supporting Korean: 1093",
  "metadata": [{ "name": "Counter-Strike", "genre": "Action", ... }]
}
```

### Query 3 — Best Games with Filters
```json
{ "query": "Best multiplayer shooters released after 2015" }
```
```json
{
  "response": "Top 10 Shooter multiplayer games:\n  • DUSK (2018) — Rating: 97.6%\n  • ...",
  "metadata": [...]
}
```

### Query 4 — Price in INR and USD
```json
{ "query": "What is the price of Counter Strike game in INR and USD?" }
```
```json
{
  "response": "Price information:\n  • Counter-Strike: $9.99 USD  |  ₹834.17 INR",
  "metadata": [{ "name": "Counter-Strike", "price_usd": 9.99, "price_inr": 834.17 }]
}
```

### Query 5 — Most Popular Game
```json
{ "query": "What is the most popular game on Steam?" }
```

### Query 6 — Developer Lookup
```json
{ "query": "Games developed by Valve" }
```

---

## 🏗️ Architecture

### How It Works

```
User Query (POST /game/analytics)
          │
          ▼
     main.py (FastAPI)
          │
          ▼
     agent.py
     ├── Groq LLM (llama-3.3-70b-versatile)
     │   Reads query → outputs tool selection JSON
     │   e.g. {"tool": "get_game_price", "params": {"game_name": "DOTA 2"}}
     │
     └── Regex Fallback (if LLM unavailable)
          │
          ▼
     Tool Dispatcher
     ├── compare_free_vs_paid_rating()
     ├── count_games_by_genre_and_language()
     ├── find_best_games()
     ├── get_game_price()              ← pandas queries
     ├── general_stats()                  on DataFrame
     ├── games_by_developer()
     └── most_popular_games()
               │
               ▼
     { "response": "...", "metadata": {...} }
```

### The LLM's Role

The LLM (Groq / LLaMA-3.3-70b) acts purely as a **language router**. It does NOT touch the data. It only reads the user's question and outputs a JSON object specifying which tool to call and with what parameters.

This approach is called a **Tool-Calling Architecture** — the LLM handles natural language understanding, pandas handles data crunching.

---

## 🧹 Data Cleaning (done in data_loader.py)

| Issue Found | Fix Applied |
|---|---|
| Price stored in cents (999 = $9.99) | Divided by 100 |
| `score_rank` 99.8% missing | Dropped column |
| Duplicate name columns after merge | Resolved to single `name` column |
| `release_date` stored as nested dict string | Regex extraction → datetime |
| Missing developer/publisher/genre | Filled with `"Unknown"` |
| No `release_date` in additional_data.csv | Year filter skipped gracefully |
| `positive_ratio` not in raw data | Computed as `positive / total_reviews` |

---

## 🛠️ Available Tools

| Tool | Answers Questions Like |
|---|---|
| `compare_free_vs_paid_rating` | "Do free games have better ratings?" |
| `count_games_by_genre_and_language` | "How many RPG games support Japanese?" |
| `find_best_games` | "Best indie games", "Top shooters after 2018" |
| `get_game_price` | "Price of DOTA 2 in INR and USD" |
| `general_stats` | "Give me an overview of the dataset" |
| `games_by_developer` | "Games made by Valve" |
| `most_popular_games` | "Most popular game on Steam" |

---

## 📊 EDA Notebook

The `EDA_notebook.ipynb` at the root covers:

- Loading and merging all 3 CSV files
- Identifying and fixing data quality issues
- Feature engineering (positive_ratio, price_usd, price_tier, review_label, etc.)
- Visualizations — genre distribution, price breakdown, rating analysis
- Answering the 4 core analytical questions with real numbers

To run it:
```bash
pip install jupyter matplotlib seaborn
jupyter notebook
```

---

## 🔧 Tech Stack

| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **Groq (LLaMA-3.3-70b)** | Natural language → tool selection |
| **pandas / numpy** | Data loading, cleaning, analytics |
| **python-dotenv** | Secure API key management |
| **uvicorn** | ASGI server |
| **Jupyter** | EDA and data exploration |

---

## 📌 Notes

- The server loads all 29,235 games into memory on startup — queries are fast after that
- If `game_data.csv` is not present, the agent still works using `additional_data.csv` alone — only the release year filter is skipped
- Currency conversion rate used: **1 USD = 83.5 INR** (update in `tools.py` if needed)
- Interactive API docs available at: `http://127.0.0.1:8000/docs`

---

## 👤 Branch

All work is on the `Game_Analytics_Agent` branch of the Round 0 repository.
