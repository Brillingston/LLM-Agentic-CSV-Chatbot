import streamlit as st
import pandas as pd
from utils.csv_handler import load_csv, get_csv_summary
from utils.llm_agent import ask_question
from utils.visualizer import auto_visualize
from utils.data_quality import generate_quality_report, format_quality_report
from utils.dashboard import (
    generate_kpi_cards,
    create_column_distribution_chart,
    create_missing_values_chart,
    create_numeric_summary_chart,
    create_categorical_chart,
    create_correlation_heatmap,
    generate_summary_stats
)

# ─────────────────────────────────────────────
#  Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🤖 CSV Chatbot Pro",
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
        background: #bbdefb;
        border-left: 4px solid #2196F3;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: #1a1a1a;
    }
    .chat-bot {
        background: #e1bee7;
        border-left: 4px solid #9C27B0;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: #1a1a1a;
    }
    .kpi-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    .kpi-title {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
    }
    .health-good {
        color: #28a745;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .health-fair {
        color: #ffc107;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .health-poor {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.1rem;
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
if "quality_report" not in st.session_state:
    st.session_state.quality_report = None

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 LLM Agentic CSV Chatbot Pro</h1>
    <p>Upload any CSV and chat with your data using Groq ⚡ | Now with Auto-Viz & Quality Checks</p>
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
            # New file uploaded
            st.session_state.df = load_csv(uploaded_file)
            st.session_state.file_name = uploaded_file.name
            st.session_state.chat_history = []
            
            # Run quality checks
            with st.spinner("🔍 Analyzing data quality..."):
                st.session_state.quality_report = generate_quality_report(st.session_state.df)
            
            st.success(f"✅ Loaded: **{uploaded_file.name}**")
            
            # Show quality badge
            health = st.session_state.quality_report['overall_health']
            if health == 'Good':
                st.markdown(f"<div class='health-good'>🟢 Data Health: {health}</div>", unsafe_allow_html=True)
            elif health == 'Fair':
                st.markdown(f"<div class='health-fair'>🟡 Data Health: {health}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='health-poor'>🔴 Data Health: {health}</div>", unsafe_allow_html=True)

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

        # Quality Report Preview
        if st.session_state.quality_report:
            with st.expander("🛡️ Quick Quality Summary", expanded=False):
                report = st.session_state.quality_report
                st.write(f"**Health**: {report['overall_health']}")
                st.write(f"**Warnings**: {len(report['warnings'])}")
                st.write(f"**Errors**: {len(report['errors'])}")
                if report['errors'] or report['warnings']:
                    st.info("View full report in Quality Tab")

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
        - *"Show revenue by quarter"* 📊
        """)

# ─────────────────────────────────────────────
#  Main Area
# ─────────────────────────────────────────────
if st.session_state.df is not None:
    df = st.session_state.df

    # Tabs: Chat | Dashboard | Data Preview | Quality Report
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📊 Live Dashboard", "📋 Data Preview", "🛡️ Quality Report"])

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
                elif msg["role"] == "chart":
                    # Display auto-generated charts
                    st.plotly_chart(msg["content"], use_container_width=True, key=f"chart_{msg.get('id', id(msg))}")
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
            "What are the column names?",
            "Give me a summary of the data",
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
            placeholder="e.g., Show revenue by quarter with a chart",
            key="question_input"
        )

        col_ask, _ = st.columns([1, 5])
        with col_ask:
            ask_clicked = st.button("🚀 Ask", use_container_width=True)

        if ask_clicked and user_question.strip():
            with st.spinner("🤔 Groq AI is thinking..."):
                response = ask_question(
                    df=df,
                    question=user_question,
                    chat_history=st.session_state.chat_history
                )

            # Save to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question
            })
            st.session_state.chat_history.append({
                "role": "model",
                "content": response
            })
            
            # Try to auto-generate visualization
            try:
                fig = auto_visualize(df, user_question, response)
                if fig:
                    st.session_state.chat_history.append({
                        "role": "chart",
                        "content": fig,
                        "id": len(st.session_state.chat_history)
                    })
            except Exception as e:
                print(f"Visualization error: {e}")
            
            st.rerun()

    # ── Tab 2: Live Dashboard ────────────────
    with tab2:
        st.subheader("📊 Live Data Dashboard")
        
        # KPI Cards
        kpi_cards = generate_kpi_cards(df)
        cols = st.columns(len(kpi_cards))
        for i, card in enumerate(kpi_cards):
            with cols[i]:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">{card['icon']} {card['title']}</div>
                    <div class="kpi-value">{card['value']}</div>
                    {f"<div style='font-size: 0.9rem; color: #95a5a6;'>{card['delta']}</div>" if card['delta'] else ""}
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container():
                fig = create_column_distribution_chart(df)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            with st.container():
                fig = create_missing_values_chart(df)
                st.plotly_chart(fig, use_container_width=True)
        
        # Charts Row 2
        col3, col4 = st.columns(2)
        
        with col3:
            with st.container():
                fig = create_numeric_summary_chart(df)
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            with st.container():
                fig = create_categorical_chart(df)
                st.plotly_chart(fig, use_container_width=True)
        
        # Correlation Heatmap
        st.subheader("🔗 Correlation Analysis")
        fig = create_correlation_heatmap(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary Statistics Table
        st.subheader("📈 Summary Statistics")
        stats_df = generate_summary_stats(df)
        st.dataframe(stats_df, use_container_width=True)

    # ── Tab 3: Data Preview ──────────────────
    with tab3:
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

    # ── Tab 4: Quality Report ────────────────
    with tab4:
        st.subheader("🛡️ Data Quality Analysis")
        
        if st.session_state.quality_report:
            report = st.session_state.quality_report
            
            # Health Score Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                health_color = {"Good": "🟢", "Fair": "🟡", "Poor": "🔴"}[report['overall_health']]
                st.metric("Overall Health", f"{health_color} {report['overall_health']}")
            with col2:
                st.metric("Checks Run", report['checks_run'])
            with col3:
                st.metric("⚠️ Warnings", len(report['warnings']))
            with col4:
                st.metric("❌ Errors", len(report['errors']))
            
            st.divider()
            
            # Detailed report
            report_md = format_quality_report(report)
            st.markdown(report_md)
            
            # Download report button
            st.download_button(
                label="📥 Download Quality Report",
                data=report_md,
                file_name="data_quality_report.md",
                mime="text/markdown"
            )
        else:
            st.info("Upload a CSV file to see the quality report")

else:
    # Landing screen when no file uploaded
    st.markdown("""
    ## 👋 Welcome to the LLM Agentic CSV Chatbot Pro!

    ### ✨ New Features:
    - 📊 **Auto Visualization** — AI automatically generates charts for your queries
    - 🛡️ **Data Quality Checks** — Instant alerts for missing values, duplicates, outliers
    - 📈 **Live Dashboard** — Beautiful interactive dashboard with KPIs and charts

    ### How to use:
    1. **Upload** a CSV file using the sidebar on the left
    2. **View** automatic quality report and health score
    3. **Explore** live dashboard with interactive charts
    4. **Ask** natural language questions in the Chat tab
    5. **Get** AI-powered answers with automatic visualizations!

    ### Powered by:
    - 🧠 **Groq** (Llama 3.3) for blazing-fast AI responses
    - 📊 **Plotly** for interactive visualizations
    - 🐼 **Pandas** for data processing
    - 🎈 **Streamlit** for the beautiful UI
    """)

    st.image(
        "https://via.placeholder.com/800x300/667eea/ffffff?text=Upload+a+CSV+to+Get+Started",
        use_column_width=True
    )