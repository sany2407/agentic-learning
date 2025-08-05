import os
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Ensure API keys are set
if not GEMINI_API_KEY or not TAVILY_API_KEY:
    raise ValueError("Missing API keys. Set GEMINI_API_KEY and TAVILY_API_KEY in your environment.")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GEMINI_API_KEY, temperature=0.7)

# Initialize Tavily Search Tool
search_tool = TavilySearch(api_key=TAVILY_API_KEY, max_results=5, include_domains=[".edu", "khanacademy.org"], topic="general")

# Define the state structure
class State(TypedDict):
    topic: str
    questions: List[str]
    resources: List[Dict]
    markdown: str
    messages: Annotated[list, "Messages for LLM context"]

# System Prompt for generating questions
QUESTION_SYSTEM_PROMPT = """
You are an expert academic researcher. Generate exactly 5 clear, concise research questions for the given topic. 
Format them as a numbered list (1. Question one, 2. Question two, etc.). 
Focus on fundamental, theoretical, and applied aspects suitable for educational resources.
"""

# System Prompt for synthesizing answers
SUMMARY_SYSTEM_PROMPT = """
You are a knowledgeable educator summarizing answers for academic study. 
Provide a concise, accurate summary based only on the provided search results from educational sources. 
If no relevant results, state 'No sufficient educational resources found.' 
Keep the summary to 3-5 sentences, emphasizing key concepts.
"""

# Node 1: Input Topic
def input_topic(state: State) -> State:
    state['topic'] = state.get('topic', '')
    state['messages'] = [SystemMessage(content=QUESTION_SYSTEM_PROMPT),
                         HumanMessage(content=f"Topic: {state['topic']}")]
    return state

# Node 2: Generate Research Questions using Gemini with System Prompt
def generate_questions(state: State) -> State:
    response = llm.invoke(state['messages'])
    # Parse the response into a list of questions
    questions = []
    for line in response.content.split('\n'):
        if line.strip().startswith(tuple(str(i) + '.' for i in range(1, 6))):
            questions.append(line.split('.', 1)[1].strip())
    state['questions'] = questions[:5]  # Ensure exactly 5
    state['messages'].append(AIMessage(content=response.content))
    return state

# Node 3: Gather Resources using Tavily Search
def gather_resources(state: State) -> State:
    resources = []
    for question in state['questions']:
        search_results = search_tool.invoke(question)
        filtered_results = [
            res for res in search_results.get('results', [])
            if any(domain in res['url'] for domain in ['.edu', 'khanacademy.org'])
        ][:3]  # Limit to 3 results per question
        # Use Gemini with system prompt to synthesize a concise answer
        messages = [SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
                    HumanMessage(content=f"Question: {question}\nSearch Results: {filtered_results}")]
        summary_response = llm.invoke(messages)
        summary = summary_response.content
        resources.append({
            'question': question,
            'answer': summary,
            'sources': filtered_results
        })
    state['resources'] = resources
    return state

# Node 4: Compile Markdown Resource List
def compile_markdown(state: State) -> State:
    markdown = f"# Academic Resource List for {state['topic'].title()}\n\n"
    for item in state['resources']:
        if not item['question']:  # Skip empty questions
            continue
        markdown += f"## {item['question']}\n"
        markdown += f"**Answer:** {item['answer']}\n"
        markdown += "**Resources:**\n"
        for src in item['sources']:
            markdown += f"- {src['title']} ({src['url']})\n"
        markdown += "\n"
    state['markdown'] = markdown
    return state

# Function to save the markdown to a file
def save_markdown_file(topic: str, content: str) -> str:
    # Sanitize filename by replacing spaces and lowering case
    filename = topic.replace(' ', '_').lower() + '.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Markdown file saved as: {filename}")
    return filename

# Build the LangGraph Workflow
workflow = StateGraph(state_schema=State)
workflow.add_node("input", input_topic)
workflow.add_node("questions", generate_questions)
workflow.add_node("gather", gather_resources)
workflow.add_node("output", compile_markdown)

# Define edges
workflow.add_edge(START, "input")
workflow.add_edge("input", "questions")
workflow.add_edge("questions", "gather")
workflow.add_edge("gather", "output")
workflow.add_edge("output", END)

# Compile the workflow
compiled_workflow = workflow.compile()

# Example Run
def generate_resource_list(topic: str) -> str:
    initial_state = {"topic": topic, "questions": [], "resources": [], "markdown": "", "messages": []}
    final_state = compiled_workflow.invoke(initial_state)
    markdown_content = final_state['markdown']
    
    # Save the markdown to a file named after the topic
    saved_file = save_markdown_file(topic, markdown_content)
    
    return f"Resource list generated and saved to {saved_file}"

# Test with a sample topic
topic = "Thermodynamics"
result = generate_resource_list(topic)
print(result)
