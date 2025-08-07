# LangChain Language Learning Agent

This project implements a LangChain-based AI agent designed as a language learning aid. It provides tips, grammar explanations, vocabulary insights, and generates personalized practice exercises for user-specified languages. The agent integrates web search via Tavily, semantic retrieval from a Chroma vector store, and Google's Gemini LLM for natural language processing and generation. Outputs are structured in JSON where applicable and saved to a Markdown file for easy reference.

## Overview

The agent processes queries about language learning, such as grammar rules or vocabulary, by:

- Retrieving relevant context from a local Chroma vector store seeded with example language tips.
- Searching the web using Tavily for up-to-date information.
- Generating custom practice exercises in JSON format.
- Saving the final response to a Markdown file.

This setup follows the problem statement for building a LangChain agent with web search, a custom tool for exercises, and structured outputs. It uses Gemini LLM for multilingual capabilities and ensures persistent storage of knowledge via Chroma.

Key components:

- **LLM**: Google Gemini (via `langchain-google-genai`).
- **Web Search**: Tavily (via `langchain_tavily`).
- **Vector Store**: Chroma for semantic search.
- **Custom Tool**: Practice exercise generator.
- **Output Handling**: Automatic saving to Markdown.

**Note**: This implementation uses deprecated LangChain agent features. For production or long-term use, consider migrating to LangGraph for better flexibility, as recommended by LangChain documentation.

## Features

- **Query Handling**: Answers questions on grammar, vocabulary, and tips for any language.
- **Web Integration**: Fetches real-time data from the web to supplement responses.
- **Semantic Retrieval**: Uses embeddings to pull relevant pre-stored tips.
- **Exercise Generation**: Creates tailored JSON-formatted exercises (e.g., vocabulary drills, grammar questions).
- **Output Persistence**: Saves agent responses to a Markdown file for offline review.
- **Conversational Support**: Handles single-turn queries; extendable to multi-turn with chat history.


## Prerequisites

- Python 3.8+.
- A Google API key for Gemini LLM and embeddings (obtain from Google AI Studio).
- A Tavily API key for web search (sign up at Tavily's website).
- Basic familiarity with command-line tools and virtual environments.


## Installation

1. **Clone the Repository**
2. **Set Up a Virtual Environment**:

```
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# Or on Windows: .venv\Scripts\activate
```

3. **Install Dependencies**:

```
pip install langchain langchain-google-genai langchain_tavily chromadb requests
```

    - `langchain`: Core framework.
    - `langchain-google-genai`: Integration for Gemini LLM and embeddings.
    - `langchain_tavily`: Official Tavily search tool.
    - `chromadb`: Vector store for semantic retrieval.
    - `requests`: For any HTTP operations (though mostly handled by tools).
4. **Set Environment Variables**:

```
export GOOGLE_API_KEY="your_google_api_key_here"
export TAVILY_API_KEY="your_tavily_api_key_here"
```

Replace with your actual keys. On Windows, use `set` instead of `export`.

## Usage

1. **Run the Script**:

```
python main.py
```

    - The script initializes the agent with example seed documents in Chroma.
    - It processes a hardcoded example query (e.g., French verb conjugations).
    - Outputs the response to the console and saves it to `language_learning_output.md`.
2. **Customize the Query**:
    - Edit the `user_query` variable in `main()` to your desired language learning question.
    - For example: `"Provide vocabulary tips for intermediate Japanese and generate exercises."`
3. **Extend for Custom Use**:
    - Add more seed documents to `seed_docs` for richer context.
    - Modify prompts in `PracticeExerciseGenerator` for different exercise formats.
    - To handle multi-turn conversations, populate `"chat_history"` in `agent.invoke()` with a list of previous messages.
4. **Output File**:
    - The generated Markdown file includes a header and the agent's full response.
    - Customize the filename or format in `save_to_markdown()`.

## Example Output

For the default query on French verb conjugations, the agent might output something like:

```
### Grammar Tips for Beginner French Verb Conjugations
- Verbs are grouped into -er, -ir, -re types...
- Example: Parler (to speak) - je parle, tu parles...

### Practice Exercises (JSON)
{
  "exercise_type": "grammar",
  "instructions": "Conjugate the following verbs...",
  "questions": ["Conjugate 'manger' in present tense."],
  "explanations": ["Manger is an -er verb..."]
}
```

This is saved to `language_learning_output.md` for easy sharing or review.

## Troubleshooting

- **API Key Errors**: Ensure environment variables are set correctly.
- **Deprecation Warnings**: These are from LangChain; the code works but consider LangGraph for future-proofing.
- **Model Availability**: If "gemini-2.5-flash" is unavailable, replace with another Gemini model like "gemini-pro".
- **Chroma Persistence**: Data is stored in `chroma_db`; delete this folder to reset the vector store.
- **Runtime Issues**: Check for package updates with `pip install -U <package>` or verify Python version.

If you encounter issues, ensure your API keys have the necessary permissions and quotas.
