# Educational Resource Compiler Agent

This project implements an **agentic AI system** that compiles educational resources for a user-specified academic topic by generating research questions, finding answers from free educational websites, and creating a structured Markdown resource list.

## Key Features

- Uses **Google Gemini LLM** as the orchestrator to generate relevant research questions and synthesize answers.
- Integrates with **Tavily Search API** to query credible, free educational content from domains such as `.edu` and Khan Academy.
- Orchestrates the workflow using **LangGraph**, enabling a ReAct pattern with context management.
- Outputs a neatly formatted Markdown file with questions, answers, and resource citations to aid academic study.


## Approach

The agent follows these steps:

1. **Input Topic**: Accept an academic topic from the user.
2. **Generate Research Questions**: Gemini generates 5 focused research questions about the topic.
3. **Search for Answers**: For each question, Tavily Search retrieves relevant educational content.
4. **Synthesize Answers**: Gemini synthesizes concise, accurate answers based on retrieved content.
5. **Compile Resource List**: Outputs a Markdown file pairing each question with its summary and sources.

## Technology Stack

- [Gemini API](https://ai.google.dev/gemini-api/docs/): Google’s advanced multimodal LLM platform.
- [Tavily Search API](https://docs.tavily.com/): AI-optimized educational search API.
- [LangGraph](https://github.com/langchain-ai/langgraph): Workflow orchestration library for AI agents.


## Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/sany2407/agentic-learning.git
cd day_4
cd task_3
```

2. **Create and activate a Python virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up API keys**

Create a `.env` file in the root directory and add:

```
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Replace `your_gemini_api_key` and `your_tavily_api_key` with your actual keys obtained from Google AI Studio and Tavily platform respectively.

5. **Run the agent**
```bash
python your_script.py
```

Replace `your_script.py` with your Python script filename containing the LangGraph workflow.

## Example Usage

The agent will generate a Markdown file named after the input topic (e.g., `thermodynamics.md`) with research questions, answers, and resource links.

## Contribution

Feel free to open issues or pull requests if you want to improve the agent or adapt it to other academic domains.

## License

This project is licensed under the MIT License.

