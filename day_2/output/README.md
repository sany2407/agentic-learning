# 🧠 RAG QA System for Amazon Product Reviews

This system leverages **Retrieval-Augmented Generation (RAG)** to extract insights from Amazon product reviews using a combination of **LangChain**, **ChromaDB**, and **Google's Gemini LLM**. It's now implemented as a fully interactive Jupyter Notebook (`rag.ipynb`) for exploration, visualization, and experimentation.

---

## 🚀 Features

- ✅ Chunk reviews by **product**, **sentiment**, and **aspect** (battery, camera, screen, etc.)
- 🔍 Retrieve relevant content using **ChromaDB** and **LangChain's retriever interface**
- 📌 Embeddings powered by **Google Generative AI** or `sentence-transformers`
- 🧾 Summarize **pros and cons** using **Gemini LLM**
- 🏷️ Cite **reviewer IDs**, **product names**, and **review aspects** in answers
- 📓 Implemented in **Jupyter Notebook (`rag.ipynb`)** for easy analysis and experimentation

---

## 📁 Directory Structure

```
your_project/
├── data/
│   ├── iphone_reviews.csv
│   ├── samsung_reviews.csv
│   └── oneplus_reviews.csv
├── rag.ipynb
├── main.py (optional script version)
└── .env
```

Make sure your `.env` contains:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 📄 Sample CSV Format

```csv
product,review_text,reviewer_id,sentiment
iPhone 14,"The battery life is amazing, lasts a full day easily.",rev001,positive
```

Ensure all your CSV files follow this structure and are stored in the `data/` directory.

---

## 🛠️ Setup Instructions

### 1. **Clone the Repository**
```bash
git clone https://github.com/sany2407/agentic-learning.git
cd agentic-learning/day_2/task_1
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```
Or manually install:
```bash
pip install langchain chromadb google-generativeai sentence-transformers pandas tqdm python-dotenv
```

### 3. **Prepare Your Data**
Place all product review CSV files inside the `data/` folder.

### 4. **Run the Notebook**
Open and run:
```bash
jupyter notebook rag.ipynb
```

---

## 📓 Key Implementation Highlights (`rag.ipynb`)

- Uses **LangChain's `CSVLoader`** and **TextSplitter** for document preprocessing
- Embeds review chunks into **ChromaDB**
- Utilizes **Google Generative AI** (`embedding-001`) for vector embedding
- Queries are answered by combining search results + Gemini LLM using **LangChain RAG chain**
- Tracks and cites sources (e.g., reviewer ID, sentiment, product)

---

## 🧪 Sample Questions to Ask

### 🔋 Battery
- What do users say about the iPhone 14 battery life?
- Are there complaints about the Samsung Galaxy A54's battery?

### 📷 Camera
- How is the camera quality of the Samsung Galaxy A54?
- Is the OnePlus Nord's camera suitable for photography?

### 📱 Screen / Design
- What do people think about the screen of the OnePlus Nord?
- Is the design of the Samsung Galaxy A54 appreciated?

### 🚀 Performance
- How is the performance of the iPhone 14?
- What are the pros and cons of the OnePlus Nord's performance?

### 💰 Worth/Price
- Is the OnePlus Nord worth buying?
- Do users think the Samsung Galaxy A54 is affordable?

---

## 📦 Libraries Used

- `langchain`: Orchestration of embedding, retrieval, and LLM interaction
- `chromadb`: Vector store for semantic document retrieval
- `sentence-transformers`: Alternative embeddings backend
- `google-generativeai`: Gemini LLM + embeddings integration
- `pandas`: Data manipulation
- `tqdm`: Progress tracking
- `dotenv`: Secure key loading

---

## ✅ Summary

With the LangChain-powered RAG notebook, you can:

- Ingest and semantically chunk product reviews from CSVs
- Query using natural language
- Get summarized answers with citation support
- Adapt easily for other domains (surveys, support tickets, etc.)

This RAG QA pipeline is ideal for generating actionable insights from large-scale user feedback.