# 💰 Financial Calculation Agent with LangGraph

This project implements a **Basic Financial Calculation Agent** using **LangGraph** and Google's **Gemini LLM**.
It can **answer general questions** via a Large Language Model and **perform basic financial calculations** like:

- Simple Interest
- Compound Interest
- Future Value
- Present Value

The agent **automatically routes** each query either to:

- **A Financial Calculation Tool** (if the query is finance-related)
- **The LLM** (if it's a general question)

***

## 📌 Features

- **💬 General Chat** — Ask any non-financial question, and the LLM answers it.
- **📈 Financial Calculations** — Calculates:
    - Simple Interest
    - Compound Interest
    - Future Value of investment
    - Present Value of investment
- **🤖 Smart Query Routing** — Uses a **LangGraph router node** to decide where to send the query.
- **⚡ Real‑time Interaction** — Runs as a simple CLI chatbot.

***

## 📂 Project Structure

```
.
├── main.py             # Main application file
├── README.md           # Documentation
```


***

## 🛠 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/sany2407/agentic-learning.git
cd day_9
cd task_8
```


### 2️⃣ Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
```


### 3️⃣ Install required dependencies

```bash
pip install -U pip
pip install langgraph langchain-google-genai langchain-core
```


***

## 🔑 API Key Setup

The project uses **Google's Gemini LLM**.
You must set your `GOOGLE_API_KEY`:

**Linux / macOS**

```bash
export GOOGLE_API_KEY="your_key_here"
```

**Windows PowerShell**

```powershell
setx GOOGLE_API_KEY "your_key_here"
```


***

## 🚀 Running the Agent

In your terminal:

```bash
python main.py
```

You will see:

```
💰 Financial Calculation Agent Ready! Type 'exit' to quit.
```

Now you can start chatting.

***

## 💡 Usage Examples

### 📈 Financial Queries

```
You: Calculate simple interest for 1000 at 5% for 2 years
Agent: Simple Interest = 100.00
--------------------------------------------------
```

```
You: What is the compound interest for 2000 at 6% for 3 years compounded 4 times a year?
Agent: Compound Interest = 387.46
--------------------------------------------------
```

```
You: What is the future value of 5000 at 4% for 5 years?
Agent: Future Value = 6083.26
--------------------------------------------------
```

```
You: Calculate the present value of 10000 at 7% for 10 years
Agent: Present Value = 5083.49
--------------------------------------------------
```


### 💬 General Queries

```
You: What is interest?
Agent: Interest is the cost of borrowing money, usually expressed as a percentage of the principal...
--------------------------------------------------
```

```
You: Who is the CEO of Google?
Agent: Sundar Pichai
--------------------------------------------------
```


***

## 🧮 How It Works

1. **Router Node**: Checks if a query matches keywords like "simple interest", "compound interest", etc.
2. **Financial Node**:
    - Extracts numbers from the query using regex
    - Calls the appropriate financial calculation function
3. **LLM Node**: Sends the query to the Gemini model for a general knowledge answer.
4. **LangGraph Flow**:

```
[User Query] → [Router Node] ──► [Financial Node] (if financial)
                │
                └──► [LLM Node] (if general)
```
