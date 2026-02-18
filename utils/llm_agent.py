import os
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
from utils.csv_handler import dataframe_to_string, get_column_info

load_dotenv()


def get_client() -> Groq:
    """Create and return a Groq client using GROQ_API_KEY from .env"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file.")
    return Groq(api_key=api_key)


def build_messages(df: pd.DataFrame, question: str, chat_history: list) -> list:
    """
    Build the messages array for Groq chat completion.
    Includes system context, chat history, and current question.
    NOTE: Filters out chart messages as they can't be sent to the LLM.
    """
    col_info = get_column_info(df)
    csv_data = dataframe_to_string(df)

    system_message = f"""You are an intelligent data analyst assistant.
You have been given a CSV dataset to analyze and answer questions about.

=== DATASET OVERVIEW ===
Total Rows: {len(df)}
Total Columns: {len(df.columns)}
Columns: {', '.join(df.columns.tolist())}

=== COLUMN DETAILS ===
{col_info}

=== FULL DATA ===
{csv_data}

=== YOUR TASK ===
Answer the user's question clearly and accurately based ONLY on the data above.
- For filtering requests: list the matching records clearly.
- For counting requests: give the exact number.
- For summarizing: give a concise, readable summary.
- For calculations: show the result with a brief explanation.
- If the question cannot be answered from this data, say so politely.
- Format your response in a clean, readable way.
- Use markdown formatting where helpful (tables, bullet points, bold text).

**IMPORTANT FOR VISUALIZATION**: 
When answering questions about trends, comparisons, or distributions, structure your 
response with clear "Label: Value" pairs on separate lines. This enables auto-visualization.

Example:
Q1: 125000
Q2: 189000
Q3: 234000
"""

    messages = [{"role": "system", "content": system_message}]

    # Add prior chat history - BUT SKIP CHART MESSAGES
    for msg in chat_history:
        # Only include user and model messages, skip chart messages
        if msg["role"] in ["user", "model"]:
            messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            })

    # Add current question
    messages.append({"role": "user", "content": question})

    return messages


# Groq models to try in order (all free tier)
MODELS_TO_TRY = [
    "llama-3.3-70b-versatile",   # Best quality, very fast
    "llama3-8b-8192",            # Lightweight fallback
    "mixtral-8x7b-32768",        # Large context fallback
    "gemma2-9b-it",              # Google Gemma fallback
]


def ask_question(df: pd.DataFrame, question: str, chat_history: list) -> str:
    """
    Send a question to Groq LLM with full CSV context.
    Automatically falls back to next model if one fails.
    Filters out chart messages from history to prevent API errors.
    """
    try:
        client = get_client()
    except ValueError as e:
        return f"❌ {str(e)}"

    messages = build_messages(df, question, chat_history)

    for model_name in MODELS_TO_TRY:
        try:
            print(f"Trying model: {model_name}")

            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model_name,
                temperature=0.3,       # Lower = more factual/accurate
                max_tokens=2048,       # Max response length
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            error_str = str(e)

            # Rate limit — try next model
            if "429" in error_str or "rate_limit" in error_str.lower():
                print(f"⚠️ Rate limit hit for {model_name}, trying next model...")
                continue

            # Model not available — try next
            elif "model" in error_str.lower() and ("not found" in error_str.lower() or "unavailable" in error_str.lower()):
                print(f"⚠️ Model {model_name} unavailable, trying next...")
                continue

            # Bad API key
            elif "401" in error_str or "auth" in error_str.lower():
                return "❌ Invalid Groq API Key. Please check your `.env` file."

            # Unknown error
            else:
                return f"❌ Groq API Error: {error_str}"

    return """❌ All Groq models are currently rate limited.

**Options:**
1. ⏳ Wait a minute and try again — Groq limits reset quickly (per minute)
2. 🔑 Check your API key at https://console.groq.com/keys
3. 📊 Try a shorter/simpler question to reduce token usage"""