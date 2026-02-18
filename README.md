# 🤖 LLM Agentic CSV Chatbot Pro

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-AI-F55036?style=for-the-badge&logo=groq&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**An intelligent, production-grade AI-powered data analysis platform that transforms CSV exploration into natural conversations — with automatic visualizations, quality checks, and live dashboards.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [What's New](#-whats-new-v20) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

The **LLM Agentic CSV Chatbot Pro** revolutionizes data exploration. Upload any CSV and interact with it naturally — no SQL, no pandas code, no complex syntax. Ask questions in plain English and get:

- 📊 **Instant answers** from ultra-fast AI (Groq LLMs)
- 📈 **Auto-generated charts** when visualizations enhance understanding
- 🛡️ **Quality reports** highlighting data issues before analysis
- 📊 **Live dashboards** with KPIs, distributions, and correlations
- 💬 **Multi-turn conversations** with full context retention

Whether you're analyzing student records, sales data, customer logs, or any tabular dataset — this tool makes exploration effortless and intelligent.

```
User: "Which student has the highest CGPA?"
  ↓
AI:  Meera Nair has the highest CGPA of 9.77
     [Auto-generated bar chart comparing all students]
```

---

## ✨ Features

### 🚀 Core Features

| Feature | Description |
|--------|-------------|
| 📂 **Instant CSV Upload** | Drag-and-drop any CSV file and see your data immediately |
| 💬 **Natural Language Queries** | Ask questions in plain English — no technical syntax needed |
| 🧠 **Powered by Groq** | Lightning-fast responses using Llama 3.3 70B model |
| 🔍 **Smart Filtering & Sorting** | "Show top 10 customers by revenue" |
| 🔢 **Aggregations & Calculations** | "What's the average salary by department?" |
| 📊 **Multi-turn Context** | Follow-up questions remember previous context |
| 🔎 **Real-time Data Search** | Live filter across all columns in the UI |
| ⬇️ **CSV Export** | Download filtered or full datasets anytime |

### ✨ Advanced Features (v2.0)

| Feature | Description | Benefit |
|--------|-------------|---------|
| 📊 **Auto Visualization** | AI automatically generates charts for trends/comparisons | Visual insights without manual chart creation |
| 🛡️ **Data Quality Checks** | Instant detection of missing values, duplicates, outliers | Catch issues before analysis begins |
| 📈 **Live Dashboard** | Interactive KPI cards + 6 chart types auto-generated | Instant overview of your entire dataset |
| 📉 **Statistical Analysis** | Box plots, correlation heatmaps, summary statistics | Deep insights into data distributions |
| 🎨 **Professional UI** | Color-coded health scores, gradient KPI cards | Production-ready interface |

---

## 🎬 Demo

### Conversation with Auto-Visualization
```
1. Upload students.csv (100 rows)

2. Q: "Which student has the highest CGPA?"
   → "Meera Nair has the highest CGPA of 9.77"
   → [Auto-generated bar chart showing top 10 students]

3. Q: "Show me the trend of average CGPA by year"
   → "Here's the average CGPA by year..."
   → [Auto-generated line chart showing trend]

4. Q: "What percentage of students have CGPA above 8?"
   → "45% of students (45 out of 100) have CGPA above 8"
   → [Auto-generated pie chart showing distribution]
```

### Quality Report Example
```
📊 Data Quality Report
Overall Health: Fair 🟡

✅ Passed Checks:
- No duplicate rows detected
- All column names are valid

⚠️ Warnings:
- Email: 23 missing values (15%)
- Revenue: 2 outliers detected (e.g., $999,999)

💡 Recommendations:
- Consider handling missing values before analysis
- Investigate outlier revenue values
```

### Live Dashboard
Automatically shows:
- 📊 4 KPI cards (Total Records, Columns, Missing Values, Health Score)
- 📈 Data type distribution pie chart
- 📊 Missing values bar chart
- 📉 Numeric columns box plots
- 🎯 Top categories bar chart
- 🔗 Correlation heatmap
- 📋 Summary statistics table

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+** ([Download](https://python.org))
- **Groq API Key** (Free) — [Get yours here](https://console.groq.com/keys)

### Quick Start (5 minutes)

**1. Clone or download the project**
```bash
git clone https://github.com/yourusername/csv-chatbot-pro.git
cd csv_chatbot
```

**2. Create virtual environment**
```bash
# Create environment
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure API key**

Create `.env` file in project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

**5. Launch the app**
```bash
streamlit run app.py
```

App opens at **http://localhost:8501** 🎉

---

## 📁 Project Structure

```
csv_chatbot/
│
├── 📄 app.py                      ← Main Streamlit application (enhanced v2.0)
├── 📄 requirements.txt            ← Python dependencies
├── 📄 .env                        ← API key configuration
├── 📄 README.md                   ← This file
├── 📄 INSTALLATION_GUIDE.md       ← Detailed setup instructions
│
└── 📁 utils/
    ├── 📄 __init__.py             ← Package initializer
    ├── 📄 csv_handler.py          ← CSV loading & data processing
    ├── 📄 llm_agent.py            ← Groq LLM integration & prompting
    ├── 📄 visualizer.py           ← Auto-visualization engine (NEW ✨)
    ├── 📄 data_quality.py         ← Quality checks & validation (NEW ✨)
    └── 📄 dashboard.py            ← Live dashboard generation (NEW ✨)
```

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.9+ | Core programming language |
| **Streamlit** | 1.32+ | Web UI framework for rapid prototyping |
| **Groq SDK** | 0.9+ | Ultra-fast LLM API client |
| **Pandas** | 2.0+ | CSV parsing & data manipulation |
| **NumPy** | 1.24+ | Numerical operations for quality checks |
| **Plotly** | 5.18+ | Interactive charts & visualizations |
| **python-dotenv** | 1.0+ | Environment variable management |
| **openpyxl** | 3.1+ | Excel file compatibility |

### AI Models (via Groq)

| Model | Use Case | Context | Speed |
|-------|----------|---------|-------|
| `llama-3.3-70b-versatile` | Primary — best accuracy | 128K tokens | ⚡⚡⚡ Ultra-fast |
| `llama3-8b-8192` | Fallback — lightweight | 8K tokens | ⚡⚡⚡ Very fast |
| `mixtral-8x7b-32768` | Fallback — large context | 32K tokens | ⚡⚡ Fast |
| `gemma2-9b-it` | Final fallback | 8K tokens | ⚡⚡ Fast |

---

## 🎯 What's New (v2.0)

### 🆕 Three Game-Changing Features

#### 1. 📊 Auto-Visualization Engine
**What it does:** AI detects when charts would enhance answers and generates them automatically

**Example:**
```
Q: "Show revenue by quarter"
→ Text answer + auto-generated bar chart

Q: "What's the trend over time?"
→ Analysis + auto-generated line chart
```

**Supported chart types:**
- Bar charts (comparisons)
- Line charts (trends)
- Pie charts (distributions)
- Scatter plots (correlations)

---

#### 2. 🛡️ Data Quality Alerts
**What it does:** Scans uploaded CSV and reports issues instantly

**7 Quality Checks:**
- ✅ Missing values detection
- ✅ Duplicate rows & IDs
- ✅ Statistical outliers (z-score)
- ✅ Date format validation
- ✅ Email/phone format validation
- ✅ Column name issues
- ✅ Overall health scoring (Good/Fair/Poor)

**Benefits:**
- Catch data issues before analysis
- Understand data quality at a glance
- Get actionable recommendations

---

#### 3. 📈 Live Dashboard
**What it does:** Auto-generates comprehensive analytics dashboard

**Includes:**
- 4 KPI cards with key metrics
- Data type distribution (pie chart)
- Missing values analysis (bar chart)
- Numeric distributions (box plots)
- Category frequencies (bar chart)
- Correlation matrix (heatmap)
- Summary statistics (table)

**Benefits:**
- Instant overview of entire dataset
- No manual dashboard creation needed
- Interactive Plotly charts
- Professional presentation-ready

---

## 💡 Usage Guide

### Asking Effective Questions

| Question Type | Example | Result |
|--------------|---------|--------|
| **Count** | *"How many students have CGPA above 9?"* | Exact count + percentage |
| **Filter** | *"List all employees in Marketing"* | Filtered table |
| **Sort** | *"Show top 10 products by revenue"* | Sorted results + chart |
| **Average** | *"What is average salary by department?"* | Aggregated data + chart |
| **Trend** | *"Show sales over the last 6 months"* | Analysis + line chart |
| **Compare** | *"Compare Q1 vs Q2 revenue"* | Comparison + bar chart |
| **Distribution** | *"What's the breakdown by category?"* | Distribution + pie chart |

### Tips for Best Results
✅ Be specific about column names when known  
✅ Ask one clear question at a time  
✅ Use follow-ups — the AI remembers context  
✅ For charts, mention trends/comparisons explicitly  
✅ Check Quality Report tab for data issues first  

---

## 🧪 Sample Data for Testing

Save this as `sample_students.csv`:

```csv
Student_ID,Name,Age,Department,Year,CGPA,City,Attendance_Percentage
1,Arjun Kumar,22,CSE,3,8.45,Chennai,85
2,Priya Sharma,21,AI & DS,2,9.12,Bangalore,92
3,Rohan Patel,23,ECE,4,7.89,Mumbai,78
4,Meera Nair,23,ECE,2,9.77,Coimbatore,60
5,Aditya Singh,20,CSE,1,8.23,Delhi,88
6,Sneha Reddy,22,AI & DS,3,9.01,Hyderabad,95
7,Vikram Joshi,21,CSE,2,8.67,Pune,82
8,Ananya Das,24,ECE,4,7.45,Kolkata,70
9,Karan Mehta,20,AI & DS,1,8.90,Ahmedabad,91
10,Divya Iyer,23,CSE,3,9.34,Chennai,89
```

**Try these queries:**
1. *"Which student has the highest CGPA?"*
2. *"Show average CGPA by department"*
3. *"List students with attendance below 80%"*
4. *"Compare CGPA across different years"*
5. *"What's the distribution of students by department?"*

---

## ⚡ Groq Free Tier Limits

| Model | Requests/Day | Tokens/Min | Tokens/Day |
|-------|-------------|-----------|-----------|
| `llama-3.3-70b-versatile` | Unlimited | 12,000 | 100,000 |
| `llama3-8b-8192` | Unlimited | 20,000 | 500,000 |
| `mixtral-8x7b-32768` | Unlimited | 5,000 | 500,000 |

> Groq's free tier is extremely generous — hundreds of queries daily at no cost with sub-second latency!

---

## 🔧 Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `GROQ_API_KEY not found` | Missing `.env` file | Create `.env` with your key |
| `401 Unauthorized` | Invalid API key | Verify key at console.groq.com |
| `400 Bad Request` | Chart in conversation history | Update to latest `llm_agent.py` |
| `ModuleNotFoundError: plotly` | Missing dependency | `pip install plotly` |
| `ModuleNotFoundError: numpy` | Missing dependency | `pip install numpy` |
| Charts not displaying | Browser cache | Clear cache and refresh |
| Bright chat bubbles | Old CSS | Update to latest `app.py` |

---

## 🗺️ Roadmap

- [ ] Excel (.xlsx) file upload support
- [ ] Export chat as PDF report with charts
- [ ] Multi-file CSV joins and comparisons
- [ ] Voice query input (speech-to-text)
- [ ] SQL query generation and display
- [ ] Database connection support (PostgreSQL, MySQL)
- [ ] Scheduled data refresh for live dashboards
- [ ] Collaborative sharing with teams
- [ ] Custom dashboard templates
- [ ] ML-powered predictions and forecasting

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Contribution Ideas:**
- Add new chart types (histogram, waterfall, etc.)
- Implement additional quality checks
- Create dashboard templates
- Add export formats (PDF, Excel with charts)
- Improve prompt engineering for better AI responses
- Add unit tests
- Create demo videos

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) — For revolutionary LPU-powered AI inference
- [Streamlit](https://streamlit.io) — For the elegant web framework
- [Meta AI](https://ai.meta.com) — For the Llama 3.3 model
- [Plotly](https://plotly.com) — For beautiful interactive visualizations
- [Pandas](https://pandas.pydata.org) — For powerful data manipulation

---

## 📊 Project Stats

- **Lines of Code:** ~1,500
- **Files:** 8 Python files
- **Features:** 15+ major features
- **Dependencies:** 8 packages
- **Charts Generated:** 8 types
- **Quality Checks:** 7 automated tests

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/yourusername/csv-chatbot-pro/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/csv-chatbot-pro/discussions)
- **Email:** brillingston.jeril@gmail.com

---

<div align="center">

**Built with ❤️ using Python, Streamlit, Groq & Plotly**

⭐ Star this repo if you found it helpful!

[![GitHub stars](https://img.shields.io/github/stars/yourusername/csv-chatbot-pro?style=social)](https://github.com/yourusername/csv-chatbot-pro)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/csv-chatbot-pro?style=social)](https://github.com/yourusername/csv-chatbot-pro)

[Report Bug](https://github.com/yourusername/csv-chatbot-pro/issues) • [Request Feature](https://github.com/yourusername/csv-chatbot-pro/issues) • [View Demo](#-demo)

</div>
