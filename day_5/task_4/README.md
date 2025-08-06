# Journal Entry Analyzer

## Overview

This project builds a LangChain agent that processes a PDF file containing journal entries, identifies recurring themes and emotions, and generates a detailed analysis report. It uses Google Gemini as the large language model (LLM) for emotion detection and thematic analysis, ChromaDB for vectorization and semantic search, and LangChain for orchestration. The agent can answer queries about specific entries or overall patterns, producing outputs in Markdown format.

Key features include:

- Loading and parsing PDF journal entries.
- Vectorizing content for efficient retrieval.
- Detecting emotions and themes using AI tools.
- Generating a comprehensive report on recurring patterns.

This setup is ideal for personal journaling analysis, therapy aids, or sentiment tracking over time.

## Prerequisites

- Python 3.8+ installed.
- A Google API key for Gemini (obtain from Google AI Studio).
- A PDF file with journal entries (e.g., "journal-entries.pdf").


## Installation

1. Clone the code
2. Install dependencies using pip:

```bash
pip install langchain langchain-google-genai langchain-community chromadb pypdf google-generativeai
```

3. Set your Google API key as an environment variable:

```python
import os
os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"  # Replace with your actual key
```


## Usage

1. Prepare your journal PDF: Ensure it's text-extractable. Place it in your working directory or update the file path in the code.
2. Run the script:

```bash
python main.ipynb
```

This will:
    - Load and vectorize the PDF.
    - Initialize the LLM and agent.
    - Generate a complete analysis report.
    - Save it as `complete_journal_analysis_report.md`.
3. Customize the analysis: Modify the agent's run prompt or add tools for specific queries (e.g., mood on a particular day).


## How It Works

1. **PDF Loading:** Uses PyPDFLoader to extract and chunk text from the journal PDF.
2. **Vectorization:** Embeds chunks with Gemini embeddings and stores them in ChromaDB for similarity searches.
3. **LLM Integration:** Google Gemini handles natural language tasks like emotion detection and theme identification.
4. **Agent Tools:** Custom tools retrieve relevant text and analyze it.
5. **Report Generation:** The agent runs queries to compile themes, emotions, and insights into a Markdown file.






