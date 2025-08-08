# RAG QA System for Amazon Product Reviews

This README provides a clear overview of the Project Architecture Blueprint for the Day 2 project. It's a Retrieval-Augmented Generation (RAG) system built in Python to query and analyze Amazon product reviews. The blueprint breaks down the design, focusing on how it uses Langchain for data handling, vector search, and AI generation, with ties to Agentic AI concepts.

## Project Overview

This system ingests product reviews from CSV files, chunks them for search, stores embeddings in a vector database, and uses an AI model to answer questions with relevant summaries. It's modular and straightforward, running in a query-response style without complex loops. Key flow: Load data → Embed and store → Retrieve and generate answers.


## Agentic AI Patterns Applied

The system uses some basic agentic ideas but isn't fully autonomous. Here's a quick eval:

- **Reflection**: Not used—no self-checks or refinements.
- **Tool Use**: Yes—the retriever pulls review chunks to boost AI answers with real data.
- **Planning**: Not used—no breaking down tasks or dynamic steps.
- **Multi-Agent**: Not used—it's a single pipeline, no team of agents.

Overall, it's strong on retrieval tools but keeps things simple without advanced AI autonomy.

## Data, Control, and Decision Flow

- **Data Path**: CSVs from `data/` get loaded, split into chunks, embedded, and stored in ChromaDB. Queries fetch top matches (default top 3) via similarity, then the LLM summarizes with pros, cons, and cites like reviewer IDs.
- **Control Path**: Sequential script: Set up env/embeddings → Process data → Load vector store → Run retrieval chain → Answer query. No branches—just straight execution.
- **Decisions**: Retriever picks chunks by similarity scores; LLM synthesizes content. No fancy choices like picking tools on the fly.


## Roles and Collaboration

- **Agents**: None—it's a non-agentic chain.
- **Key Tools/Functions**:
    - CSVLoader: Pulls in review data.
    - RecursiveCharacterTextSplitter: Chops docs into embeddable pieces.
    - Retriever (Chroma): Finds and grabs relevant chunks.
    - RetrievalQA Chain: Ties retrieval to LLM for smooth answers.
- **How They Work Together**: Linear handoff—loaders to splitters to storage, then retriever feeds the LLM. All connected via Langchain for efficient query handling.


## Tech Stack

- **LLMs**: Google Gemini (model: gemini-2.0-flash) at temperature 0 for consistent responses.
- **Vector Stores**: ChromaDB for embedding storage and queries.
- **Tools**: Google embeddings (model: embedding-001); tqdm for progress bars.
- **Databases**: Just Chroma—nothing else.
- **APIs**: Google Generative AI for embeddings and inference, keyed from `.env`.

This blueprint keeps the project focused and effective for review insights. For setup details, check the main repo docs. Happy building!

