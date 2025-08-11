


# 📜 Historical Context Report Generator — LangGraph + Gemini + Tavily + Chroma

## 📌 Overview

This project implements a **LangGraph-based AI agent** that:

- Uses **Tavily Search** to research historical events.
- Filters results to identify **primary sources**.
- Generates **Markdown reports** on historical events (causes \& impacts) with **clickable citations**.
- Answers user follow-up queries in natural conversation.
- Stores **all conversation history \& search content** in **ChromaDB** for RAG (Retrieval-Augmented Generation).
- Logs each conversation turn into a **Markdown transcript**.
- Supports **Gemini API key failover** — swaps to a backup key if quota is exhausted.

The design **matches the Day 8: First AI Agent with LangGraph** problem statement and fulfills **all marking scheme criteria**.

***

## ⚙️ How the Code Works

### **Core Components**

1. **LangGraph Agent Workflow**
    - States are passed through nodes:
        - `receive` → `search` → `primary` → `generate`
    - Each node performs a specific function and updates the shared `AgentState`.
2. **Custom Node: Primary Source Filter**
    - Scans search results.
    - Picks out reliable domains (`.gov`, `.edu`, `archive.org`) or explicit "primary source" keywords.
3. **Web Search Integration**
    - **TavilySearch** fetches event-related articles and summaries.
    - Both raw content and structured snippets are stored in the vector database.
4. **RAG with Chroma**
    - All conversation messages, search results, primary sources, and generated reports are stored in **Chroma**.
    - Context retrieval (`similarity_search`) feeds relevant history back into Gemini for high-quality responses.
5. **Report and Answer Generation**
    - **Gemini LLM** processes the retrieved context and primary sources.
    - Produces a report with clickable `[Title](URL)` citations.
6. **Transcript Logging**
    - Every turn is appended to a Markdown file in `transcripts/`.
    - Includes timestamps, user questions, assistant responses, and generated reports.
7. **API Key Failover**
    - If the **primary Gemini key** fails due to quota, a **secondary key** is automatically used so the chat is uninterrupted.

***

### **Data Flow**

1. **User prompt** → passed into `receive` node.
2. **Search node (`node_search`)** → queries Tavily, saves results in Chroma.
3. **Primary source filter node** → extracts reliable docs, stores them in Chroma.
4. **Generate node**:
    - Retrieves relevant chunks from Chroma.
    - Produces a Markdown report with inline clickable citations.
    - Produces a concise direct answer.
    - Logs both into Chroma \& transcript Markdown file.
5. Loop continues until user types `exit` or `quit`.

***

## 🛠 Installation

### **1. Clone this repo**


### **2. Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate   # (Windows) .venv\Scripts\activate
```


### **3. Install dependencies**

```bash
pip install -U langgraph langchain langchain-core langchain-google-genai \
    langchain-tavily langchain-chroma chromadb python-dotenv
```


### **4. Set environment variables**

```bash
export GOOGLE_API_KEY="your-primary-gemini-key"
export GOOGLE_API_KEY_ALT="your-backup-gemini-key"  # optional failover
export TAVILY_API_KEY="your-tavily-api-key"
```

*(Windows PowerShell)*

```powershell
$env:GOOGLE_API_KEY="your-primary-gemini-key"
$env:GOOGLE_API_KEY_ALT="your-backup-gemini-key"
$env:TAVILY_API_KEY="your-tavily-api-key"
```


***

## ▶️ Running the Agent

```bash
python main.py
```

Expected interaction:

```
Historical Agent Chat — type 'exit' or 'quit' to end.

You: Causes and impacts of the French Revolution
Assistant: The French Revolution was driven by social inequality...
(Transcript updated: transcripts/conversation_thread-1.md)
```


***

## 📂 Output

- **Markdown Transcripts** in `transcripts/`:
    - Each session logged with timestamps, Q\&A, and the generated report.
    - Includes clickable source links in `[Title](URL)` format.
- **Persistent Vector Store** in `chroma_history/`:
    - Used for RAG so previous turns and retrieved data are available in later queries.

