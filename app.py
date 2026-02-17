import streamlit as st
import pandas as pd
from utils.csv_handler import load_csv, get_csv_summary
from utils.llm_agent import ask_question

# ─────────────────────────────────────────────
#  Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🤖 CSV Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Custom CSS Styling
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .chat-user {
        background: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .chat-bot {
        background: #f3e5f5;
        border-left: 4px solid #9C27B0;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Session State Initialization
# ─────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "df" not in st.session_state:
    st.session_state.df = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 LLM Agentic CSV Chatbot</h1>
    <p>Upload any CSV and chat with your data using Gemini 2.5 Flash</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Sidebar — File Upload & Info
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Your CSV")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload any CSV file to start chatting with your data"
    )

    if uploaded_file is not None:
        if st.session_state.file_name != uploaded_file.name:
            st.session_state.df = load_csv(uploaded_file)
            st.session_state.file_name = uploaded_file.name
            st.session_state.chat_history = []
            st.success(f"✅ Loaded: **{uploaded_file.name}**")

        df = st.session_state.df
        summary = get_csv_summary(df)

        st.divider()
        st.header("📊 Dataset Info")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", summary["total_rows"])
        with col2:
            st.metric("Columns", summary["total_columns"])

        st.write("**Columns:**")
        for col in summary["columns"]:
            st.write(f"• `{col}`")

        st.divider()
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

    else:
        st.info("👆 Please upload a CSV file to get started.")
        st.markdown("""
        **Example questions you can ask:**
        - *"How many rows are there?"*
        - *"List all students in Year 3"*
        - *"Show names and CGPA sorted by highest"*
        - *"What is the average CGPA?"*
        - *"Count students by department"*
        """)

# ─────────────────────────────────────────────
#  Main Area
# ─────────────────────────────────────────────
if st.session_state.df is not None:
    df = st.session_state.df

    tab1, tab2 = st.tabs(["💬 Chat", "📋 Data Preview"])

    # ── Tab 1: Chat ──────────────────────────
    with tab1:
        st.subheader("💬 Ask Anything About Your Data")

        # Display chat history
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-user">
                        <strong>🧑 You:</strong><br>{msg["content"]}
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(
                        "<div class='chat-bot'><strong>🤖 AI:</strong></div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(msg["content"])
        else:
            st.info("👋 Start by asking a question about your data below!")

        # Suggested quick questions
        st.write("**💡 Try asking:**")
        suggestions = [
            "How many rows are in this dataset?",
            "Show me the first 5 records",
            "What are the unique values in each column?",
            "Summarize the dataset for me",
        ]
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"suggest_{i}"):
                    st.session_state["prefill_question"] = suggestion
                    st.rerun()

        # Chat input
        prefill = st.session_state.pop("prefill_question", "")
        user_question = st.text_input(
            "Ask a question:",
            value=prefill,
            placeholder="e.g. List all students with CGPA above 8.5",
            key="question_input"
        )

        col_ask, _ = st.columns([1, 5])
        with col_ask:
            ask_clicked = st.button("🚀 Ask", use_container_width=True)

        if ask_clicked and user_question.strip():
            with st.spinner("🤔 Gemini is thinking..."):
                response = ask_question(
                    df=df,
                    question=user_question,
                    chat_history=st.session_state.chat_history
                )

            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question
            })
            st.session_state.chat_history.append({
                "role": "model",
                "content": response
            })
            st.rerun()

    # ── Tab 2: Data Preview ──────────────────
    with tab2:
        st.subheader("📋 Full Dataset Preview")

        search_term = st.text_input("🔍 Quick filter (search across all columns):", "")
        if search_term:
            mask = df.apply(
                lambda col: col.astype(str).str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            filtered_df = df[mask]
            st.write(f"Found **{len(filtered_df)}** matching rows:")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_bytes,
            file_name="data_export.csv",
            mime="text/csv"
        )

else:
    st.markdown("""
    ## 👋 Welcome to the LLM Agentic CSV Chatbot!

    ### How to use:
    1. **Upload** a CSV file using the sidebar on the left
    2. **View** your data in the Data Preview tab
    3. **Ask** natural language questions in the Chat tab
    4. **Get** intelligent AI-powered answers instantly!

    ### Powered by:
    - 🧠 **Gemini 2.5 Flash** via the new `google-genai` SDK
    - 🐼 **Pandas** for CSV processing
    - 🎈 **Streamlit** for the UI
    """)