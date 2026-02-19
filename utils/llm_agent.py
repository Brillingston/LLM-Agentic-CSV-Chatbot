import os
import time
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


def ask_question(df: pd.DataFrame, question: str, chat_history: list) -> dict:
    """
    Send a question to Groq LLM with full CSV context.
    Returns a dict with response text and metadata.
    
    Returns:
        {
            "response": str,      # AI's answer
            "metadata": dict      # JSON metadata about the request
        }
    """
    start_time = time.time()
    
    try:
        client = get_client()
    except ValueError as e:
        return {
            "response": f"❌ {str(e)}",
            "metadata": None
        }

    messages = build_messages(df, question, chat_history)
    
    # Calculate token estimates (rough approximation)
    total_chars = sum(len(str(m.get("content", ""))) for m in messages)
    estimated_input_tokens = total_chars // 4  # Rough estimate: 1 token ≈ 4 chars

    for model_name in MODELS_TO_TRY:
        try:
            print(f"Trying model: {model_name}")

            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model_name,
                temperature=0.3,
                max_tokens=2048,
            )

            response_time = time.time() - start_time
            response_text = chat_completion.choices[0].message.content

            # Build metadata JSON
            metadata = {
                "model": model_name,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "response_time_seconds": round(response_time, 2),
                "tokens": {
                    "prompt_tokens": getattr(chat_completion.usage, 'prompt_tokens', estimated_input_tokens),
                    "completion_tokens": getattr(chat_completion.usage, 'completion_tokens', len(response_text) // 4),
                    "total_tokens": getattr(chat_completion.usage, 'total_tokens', estimated_input_tokens + len(response_text) // 4)
                },
                "dataset_info": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "rows_sent_to_llm": min(50, len(df)),
                    "columns": list(df.columns)
                },
                "conversation": {
                    "turn_number": len([m for m in chat_history if m["role"] == "user"]) + 1,
                    "history_messages": len([m for m in chat_history if m["role"] in ["user", "model"]])
                },
                "api_info": {
                    "provider": "Groq",
                    "temperature": 0.3,
                    "max_tokens": 2048
                }
            }

            return {
                "response": response_text,
                "metadata": metadata
            }

        except Exception as e:
            error_str = str(e)

            # Token limit error
            if "reduce the length" in error_str.lower() or "too long" in error_str.lower():
                return {
                    "response": """❌ Dataset too large for analysis.

**The CSV has too many rows/columns to process in one query.**

**Solutions:**
1. 🔍 Ask more specific questions (e.g., "Show top 10..." instead of "Show all...")
2. ✂️ Filter your CSV before upload (remove unnecessary columns)
3. 📊 Use the Dashboard tab for overview instead
4. 📋 Use Data Preview tab to explore raw data

Try asking: "What are the column names?" or "Summarize the first 10 rows" """,
                    "metadata": {
                        "error": "Token limit exceeded",
                        "dataset_rows": len(df),
                        "dataset_columns": len(df.columns),
                        "estimated_tokens": estimated_input_tokens
                    }
                }

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
                return {
                    "response": "❌ Invalid Groq API Key. Please check your `.env` file.",
                    "metadata": {"error": "Authentication failed"}
                }

            # Unknown error
            else:
                return {
                    "response": f"❌ Groq API Error: {error_str}",
                    "metadata": {"error": error_str}
                }

    return {
        "response": """❌ All Groq models are currently rate limited.

**Options:**
1. ⏳ Wait a minute and try again — Groq limits reset quickly (per minute)
2. 🔑 Check your API key at https://console.groq.com/keys
3. 📊 Try a shorter/simpler question to reduce token usage""",
        "metadata": {"error": "All models rate limited"}
    }