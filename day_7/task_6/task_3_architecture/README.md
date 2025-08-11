

# Architecture Blueprint for Academic Resource List Generator

This document outlines the architecture of the provided LangGraph-based agentic AI system, which generates an academic resource list for a given topic. The system uses a sequential workflow to process inputs, generate questions, gather and summarize resources, and compile output. Below, I detail the components as per the required blueprint.

## 1. Overall System Architecture

The system is built as a directed acyclic graph (DAG) using LangGraph's StateGraph. It consists of four main nodes representing sequential processing steps: input handling, question generation, resource gathering, and markdown compilation. The state is maintained across nodes via a shared `State` dictionary, which tracks the topic, generated questions, resources, markdown output, and message history for LLM context.

The architecture follows a linear pipeline pattern, where each node performs a specific task and passes updated state to the next. There are no loops or conditional branches; it's a straightforward flow from start to end. The system integrates an LLM for content generation and a search tool for external data retrieval, making it an agentic setup focused on educational resource curation.

## 2. Applied Agentic AI Patterns

The system implicitly applies the following patterns from Agentic AI design principles:

- **Tool Use Pattern**:The TavilySearch tool is invoked to fetch educational resources based on generated questions. The LLM then processes these results to create summaries, demonstrating tool integration for augmenting AI capabilities with external data.
- **Planning Pattern**: Applied through the structured workflow. The graph defines a clear plan: start with topic input, generate questions, search for resources, summarize, and compile output. This sequences tasks logically to achieve the overall goal without runtime decision-making.
- **Multi-Agent Pattern**: Partially applied. While not a full multi-agent system with independent collaborating agents, the nodes can be viewed as specialized "agents" (e.g., question generator agent, resource gatherer agent) that collaborate via state passing. However, it's more of a single-agent pipeline with modular components.
- **Reflection Pattern**: There is no mechanism for the system to self-evaluate outputs, revise plans, or loop back based on intermediate results.


## 3. Flow of Data, Control, and Decision-Making

The flow is linear and deterministic, with control passing sequentially through nodes via defined edges in the StateGraph:

- **Start → Input Node**: User provides a topic (e.g., "Data Analytics"). Data: Topic string. Control: Initializes state with system prompt and human message for LLM.
- **Input → Questions Node**: LLM generates 5 research questions. Data: Passes messages to LLM; parses response into a list of questions. Control: No decisions; always proceeds to next node.
- **Questions → Gather Node**: For each question, invokes search tool, then uses LLM to summarize results. Data: Questions list → search results → summaries stored as resources (dicts with question, answer, sources). Control: Iterates over questions; no branching.
- **Gather → Output Node**: Compiles resources into markdown format. Data: Resources list → formatted string. Control: Final step; saves to file externally.
- **Output → End**: Workflow completes, returning the markdown content.

Data flows via the shared state dictionary, updated at each node. Control is predefined in the graph edges, with no runtime decisions or error handling in the provided code. Decision-making is embedded in the LLM calls (e.g., question generation, summarization) but not in the graph structure.

## 4. Roles of Agents/Tools/Functions and Collaboration

- **Agents/Nodes**:
    - **Input Node**: Role: Captures and initializes the topic. Collaboration: Prepares message context for the next node.
    - **Questions Node**: Role: Acts as a question-generating agent using LLM. Collaboration: Outputs questions to drive resource gathering.
    - **Gather Node**: Role: Resource collector and summarizer; invokes search tool and LLM. Collaboration: Processes questions in parallel (loop), integrating external data with AI synthesis.
    - **Output Node**: Role: Compiler; formats data into readable markdown. Collaboration: Aggregates all prior outputs for final delivery.
- **Tools/Functions**:
    - **TavilySearch Tool**: Role: Retrieves up to 5 search results per question, filtered for educational domains (e.g., .edu, khanacademy.org). Collaboration: Provides raw data to the summarization step.
    - **save_markdown_file Function**: Role: Persists the compiled markdown to a file. Collaboration: External to the graph; called after workflow completion.
- **Collaboration**: Components collaborate through state updates. For example, questions from the LLM agent feed into the search tool, whose results are summarized by another LLM call, ensuring a cohesive output. This modular design allows each part to focus on a sub-task while contributing to the end goal of resource list generation.


## 5. LLMs, Vector Stores, Tools, Databases, APIs Involved

- **LLMs**: ChatGoogleGenerativeAI (Gemini model "gemini-2.5-flash"). Used for generating research questions (with QUESTION_SYSTEM_PROMPT) and summarizing search results (with SUMMARY_SYSTEM_PROMPT). Temperature set to 0.7 for balanced creativity.
- **Vector Stores**: None involved. No embedding or retrieval-augmented generation (RAG) mechanisms are used.
- **Tools**: TavilySearch (configured with max_results=5, domain filtering, and general topic). Integrated via LangChain.
- **Databases**: None. All data is ephemeral within the state or saved to a local markdown file.
- **APIs**:
    - Google Generative AI API (via GEMINI_API_KEY) for LLM invocations.
    - Tavily Search API (via TAVILY_API_KEY) for web searches.
