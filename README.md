# 🤖 LLM Agentic CSV Chatbot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-AI-F55036?style=for-the-badge&logo=groq&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**An intelligent, fully agentic AI-powered chatbot that lets you have natural conversations with any CSV dataset — no code required.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [Project Structure](#-project-structure) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

The **LLM Agentic CSV Chatbot** transforms the way you interact with data. Instead of writing complex SQL queries or pandas code, simply upload your CSV and ask questions in plain English. The AI understands your intent, analyzes the dataset, and returns clear, human-readable answers — just like talking to a data analyst.

Whether you're an educator reviewing student records, an analyst exploring sales data, or a developer prototyping a data product — this tool makes CSV exploration effortless and intelligent.

```
User: "List all students in Year 3 with CGPA above 8.5"
  ↓
AI:  Here are the students in Year 3 with CGPA above 8.5:
     | Name    | Year | Department | CGPA |
     |---------|------|------------|------|
     | Alice   |  3   | AI & DS    | 9.1  |
     | Charlie |  3   | AI & DS    | 8.7  |
     Total: 2 students found.
```

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 📂 **CSV Upload** | Drag-and-drop any CSV file and instantly preview your data |
| 💬 **Natural Language Queries** | Ask questions in plain English — no SQL or code needed |
| 🧠 **Agentic AI Engine** | Powered by Groq's ultra-fast LLMs (Llama 3.3, Mixtral) |
| 🔍 **Smart Filtering** | "Show all employees in Sales earning above $60k" |
| 🔢 **Auto Counting** | "How many students are in Year 2?" |
| 📊 **Summarization** | "Give me a summary of this dataset" |
| 📈 **Calculations** | "What is the average CGPA by department?" |
| 🔄 **Multi-turn Chat** | Remembers conversation context across multiple questions |
| 🔎 **Live Data Filter** | Real-time search/filter across the full dataset in the UI |
| ⬇️ **CSV Export** | Download the filtered or full dataset anytime |
| ⚡ **Blazing Fast** | Groq's LPU inference delivers sub-second AI responses |
| 🔁 **Model Fallback** | Automatically switches models if rate limits are hit |

---

## 🎬 Demo

### Upload & Chat
```
1. Upload students.csv
2. Ask: "How many students are there in total?"
   → "There are 7 students in total."

3. Ask: "Show names and CGPA of AI & DS students"
   → Lists all AI & DS students with their CGPAs in a clean table.

4. Ask: "Who has the highest CGPA?"
   → "Eve from CSE has the highest CGPA of 9.3"
```

### Supported Query Types
- ✅ Filtering — *"List all records where Department is ECE"*
- ✅ Counting — *"How many rows match Year = 3?"*
- ✅ Aggregation — *"What is the average, min, and max CGPA?"*
- ✅ Sorting — *"Show top 5 students by CGPA"*
- ✅ Summarizing — *"Give me a full summary of this data"*
- ✅ Multi-column — *"Show Name, Department and CGPA for Year 1 students"*

---

## 🚀 Installation

### Prerequisites

- Python **3.9 or higher**
- A free **Groq API Key** — get one at [console.groq.com/keys](https://console.groq.com/keys)

### Step-by-Step Setup

**1. Clone or download the project**
```bash
git clone https://github.com/yourusername/csv-chatbot.git
cd csv_chatbot
```

**2. Create and activate a virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — Mac/Linux
source venv/bin/activate
```

**3. Upgrade pip**
```bash
python -m pip install --upgrade pip
```

**4. Install all dependencies**
```bash
pip install -r requirements.txt
```

**5. Configure your API key**

Create a `.env` file in the root of the project:
```env
GROQ_API_KEY=your_groq_api_key_here
```

**6. Launch the app**
```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501** 🎉

---

## 📁 Project Structure

```
csv_chatbot/
│
├── 📄 app.py                  ← Main Streamlit application & UI
├── 📄 requirements.txt        ← Python dependencies
├── 📄 .env                    ← API key configuration (you create this)
├── 📄 README.md               ← Project documentation
│
└── 📁 utils/
    ├── 📄 __init__.py         ← Package initializer
    ├── 📄 csv_handler.py      ← CSV loading, parsing & summarization
    └── 📄 llm_agent.py        ← Groq LLM integration & prompt engineering
```

### File Responsibilities

| File | Responsibility |
|------|---------------|
| `app.py` | Streamlit UI, session state, chat display, tab layout |
| `utils/csv_handler.py` | CSV loading, column profiling, data-to-string conversion |
| `utils/llm_agent.py` | Groq client, prompt building, model fallback logic |
| `.env` | Stores `GROQ_API_KEY` securely outside source code |

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.9+ | Core programming language |
| **Streamlit** | Latest | Web UI framework |
| **Groq SDK** | Latest | LLM API client |
| **Pandas** | Latest | CSV parsing & data manipulation |
| **python-dotenv** | Latest | Environment variable management |
| **openpyxl** | Latest | Excel file compatibility |

### AI Models Used (via Groq)

| Model | Use Case | Context Window |
|-------|----------|---------------|
| `llama-3.3-70b-versatile` | Primary — best accuracy | 128K tokens |
| `llama3-8b-8192` | Fallback — lightweight | 8K tokens |
| `mixtral-8x7b-32768` | Fallback — large context | 32K tokens |
| `gemma2-9b-it` | Final fallback | 8K tokens |

---

## 💡 Usage Guide

### Asking Good Questions

| Question Type | Example |
|--------------|---------|
| Count | *"How many students have CGPA above 9?"* |
| Filter | *"List all employees in the Marketing department"* |
| Sort | *"Show the top 10 products by revenue"* |
| Average | *"What is the average salary by department?"* |
| Summary | *"Give me an overview of this dataset"* |
| Specific column | *"Show only Name and Email columns"* |
| Conditional | *"Who joined after January 2023?"* |

### Tips for Best Results
- Be specific about column names if you know them
- Ask one question at a time for clearest answers
- Use follow-up questions — the chatbot remembers context
- For large datasets, ask targeted questions to avoid token limits

---

## 🧪 Sample CSV to Test With

Save this as `students.csv` and upload it to try the app:

```csv
Name,Year,Department,CGPA
Alice,3,AI & DS,9.1
Bob,2,CSE,7.8
Charlie,3,AI & DS,8.5
Diana,1,ECE,8.9
Eve,3,CSE,9.3
Frank,2,AI & DS,7.5
Grace,1,ECE,9.0
Henry,2,CSE,8.2
Iris,1,AI & DS,8.8
James,3,ECE,7.9
```

**Try asking:**
- *"How many students are in Year 3?"*
- *"List all AI & DS students sorted by CGPA"*
- *"What is the average CGPA per department?"*
- *"Who are the top 3 students overall?"*

---

## ⚡ Groq Free Tier Limits

| Model | Requests/Day | Tokens/Min | Tokens/Day |
|-------|-------------|-----------|-----------|
| `llama-3.3-70b-versatile` | Unlimited | 12,000 | 100,000 |
| `llama3-8b-8192` | Unlimited | 20,000 | 500,000 |
| `mixtral-8x7b-32768` | Unlimited | 5,000 | 500,000 |

> Groq's free tier is extremely generous. You can run hundreds of queries per day at no cost.

---

## 🔧 Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `GROQ_API_KEY not found` | Missing `.env` file | Create `.env` with your key |
| `401 Unauthorized` | Invalid API key | Check key at console.groq.com |
| `429 Rate Limited` | Too many requests | App auto-retries with fallback models |
| `ModuleNotFoundError` | Missing library | Run `pip install -r requirements.txt` |
| `python not recognized` | Python not in PATH | Reinstall Python, check "Add to PATH" |
| `venv\Scripts\activate` fails | PowerShell policy | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## 🗺️ Roadmap

- [ ] Support for Excel (`.xlsx`) file uploads
- [ ] Export chat history as PDF report
- [ ] Data visualization (auto-generate charts from queries)
- [ ] Multi-file CSV comparison
- [ ] Support for Google Sheets URLs
- [ ] User authentication & saved sessions

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) — For blazing fast LLM inference
- [Streamlit](https://streamlit.io) — For the elegant web framework
- [Meta AI](https://ai.meta.com) — For the Llama 3.3 model
- [Pandas](https://pandas.pydata.org) — For powerful data handling

---

<div align="center">

**Built with ❤️ using Python, Streamlit & Groq**

⭐ Star this repo if you found it helpful!

</div>
