
# 🧠 RAG QA System for Amazon Product Reviews

This system is designed to extract insights from Amazon product reviews using a Retrieval-Augmented Generation (RAG) approach, combining a vector database and an LLM (Gemini) for intelligent Q&A.

---

## 🚀 Features

- ✅ Chunk reviews by **product**, **sentiment**, and **aspect** (battery, camera, etc.)
- 🔍 Retrieve relevant chunks using **ChromaDB** with **SentenceTransformer** embeddings
- 🧾 Summarize pros and cons using **Gemini LLM**
- 🏷️ Cite **reviewer IDs**, **product names**, and **aspects** in the output

---

## 📁 Directory Structure

```
your_project/
├── data/
│   ├── iphone_reviews.csv
│   ├── samsung_reviews.csv
│   └── oneplus_reviews.csv
├── main.py
└── .env
```

Ensure `.env` contains your `GOOGLE_API_KEY`.

---

## 📄 Sample CSV Format

```csv
product,review_text,reviewer_id,sentiment
iPhone 14,"The battery life is amazing, lasts a full day easily.",rev001,positive
```

---

## 🛠️ Setup Instructions

1. **Clone the repository**
```
git clone https://github.com/sany2407/agentic-learning.git
cd day_2
cd task_1
```

2. **Install dependencies**:
```bash
pip install chromadb google-generativeai sentence-transformers pandas tqdm python-dotenv
```

3. **Prepare your data**:
Place all CSV review files inside the `data/` directory.

4. **Run the script**:
```bash
python main.py
```

---

## 🧪 Sample Questions to Ask

Here are some example questions you can try once the system is running:

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

- `chromadb`: Vector store for semantic search
- `sentence-transformers`: For generating embeddings
- `google-generativeai`: Gemini model integration
- `pandas`: Data loading and manipulation
- `tqdm`: Progress bar for review chunking
- `dotenv`: Load API keys from `.env` file

---

## 🧠 What is `tqdm`?

`tqdm` is a Python library that adds a **progress bar** to loops.

Example:
```python
from tqdm import tqdm
for i in tqdm(range(100)):
    time.sleep(0.1)
```

In your code:
```python
for idx, row in tqdm(df.iterrows(), total=len(df), desc="🔍 Chunking reviews"):
```
This helps track how many reviews are being processed live.

---

## ✅ Summary

With this RAG QA system, you can:
- Ingest product reviews from CSV files
- Search by product and aspect
- Ask questions and get summarized answers
- Trace sources by reviewer ID and sentiment

Ideal for generating insights from large volumes of customer feedback.