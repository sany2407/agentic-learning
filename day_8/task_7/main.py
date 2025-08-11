import os
from pathlib import Path
from typing import List, Dict, Any, TypedDict
from datetime import datetime, timezone

# LangGraph
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# LangChain core
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# Gemini
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Vector DB
from langchain_chroma import Chroma

# Tavily search
from langchain_tavily import TavilySearch

# ---------------- ENVIRONMENT ----------------
PRIMARY_KEY = os.environ.get("GOOGLE_API_KEY")
SECONDARY_KEY = os.environ.get("GOOGLE_API_KEY_ALT")  # optional failover
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
if not PRIMARY_KEY or not TAVILY_API_KEY:
    raise RuntimeError("Set GOOGLE_API_KEY (and optionally GOOGLE_API_KEY_ALT) and TAVILY_API_KEY.")

# ---------------- SETUP ----------------
EMBED_MODEL = "models/text-embedding-004"
CHAT_MODEL = "gemini-2.0-flash"

embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=PRIMARY_KEY)

def get_chat_llm(api_key=None):
    return ChatGoogleGenerativeAI(model=CHAT_MODEL,
                                  api_key=api_key or PRIMARY_KEY,
                                  temperature=0.3)

chat_llm = get_chat_llm()

from google.api_core.exceptions import ResourceExhausted, PermissionDenied
def safe_llm_invoke(prompt_msgs):
    global chat_llm
    try:
        return chat_llm.invoke(prompt_msgs).content.strip()
    except (ResourceExhausted, PermissionDenied):
        if SECONDARY_KEY and chat_llm.api_key != SECONDARY_KEY:
            print("\n[INFO] Primary Gemini key quota hit — switching to secondary key.\n")
            chat_llm = get_chat_llm(SECONDARY_KEY)
            return chat_llm.invoke(prompt_msgs).content.strip()
        raise

# Chroma persistence
CHROMA_DIR = "chroma_history"
os.makedirs(CHROMA_DIR, exist_ok=True)
vectorstore = Chroma(collection_name="historical_agent",
                     embedding_function=embeddings,
                     persist_directory=CHROMA_DIR)

# Tavily Search
tavily_search_tool = TavilySearch(
    max_results=5, topic="general",
    include_answer=True, include_raw_content=True,
    search_depth="advanced"
)

# Transcript folder
TRANSCRIPTS_DIR = Path("transcripts")
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- STATE ----------------
class AgentState(TypedDict):
    messages: List[Any]
    query: str
    search_results: List[Dict[str, Any]]
    primary_sources: List[str]
    report_md: str
    answer: str
    to_index: List[Dict[str, str]]

# ---------------- HELPERS ----------------
def save_markdown_transcript(thread_id: str, messages: List[Any], report_md: str = ""):
    fpath = TRANSCRIPTS_DIR / f"conversation_{thread_id}.md"
    lines = []
    if not fpath.exists():
        lines.append(f"# Conversation Transcript (thread: {thread_id})")
    timestamp = datetime.now(timezone.utc).isoformat()
    lines.append(f"\n## Turn @ {timestamp}\n")
    for m in messages:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        lines.append(f"- {role}: {m.content}")
    if report_md:
        lines.append("\n### Generated Report\n")
        lines.append(report_md)
    with open(fpath, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def add_to_chroma(items: List[Dict[str, str]]):
    if not items: return
    vectorstore.add_texts([it["text"] for it in items],
                          metadatas=[{"meta": it.get("meta", "")} for it in items],
                          ids=[it.get("id") for it in items])

def retrieve_context(query: str, k: int = 8) -> str:
    docs = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([f"[{i+1}] {d.page_content}" for i, d in enumerate(docs)])

# ---------------- TOOLS ----------------
def tool_web_search(query: str) -> Dict[str, Any]:
    out = tavily_search_tool.invoke({"query": query})
    results = [{
        "title": r.get("title", f"Source {i+1}"),
        "url": r.get("url", ""),
        "content": r.get("content") or "",
        "raw_content": r.get("raw_content") or ""
    } for i, r in enumerate(out.get("results", []))]
    return {"answer": out.get("answer", ""), "results": results}

def tool_filter_primary_sources(results: List[Dict[str, Any]]) -> List[str]:
    primary = []
    for r in results:
        url = r.get("url", "")
        content = r.get("raw_content") or r.get("content") or ""
        if not content: continue
        if any(k in url for k in [".gov", "archive.org", ".edu"]):
            primary.append(content)
        elif any(kw in content.lower() for kw in ["primary source", "transcript", "official record"]):
            primary.append(content)
    return primary

# ---------------- PROMPTS ----------------
SYSTEM_MESSAGE = SystemMessage(content=(
    "You are a structured-chat zero-shot ReAct agent. Research historical events, "
    "identify causes and impacts, validate primary sources, and answer with citations."
))

REPORT_PROMPT = ChatPromptTemplate.from_messages([
    SYSTEM_MESSAGE,
    ("human", "Write a markdown report on the causes and impacts of: {query}\n"
              "Primary Sources:\n{sources}\n\n"
              "Retrieved Context:\n{retrieved}")
])

ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    SYSTEM_MESSAGE,
    ("human", "Answer the user's question: {query}\n\nContext:\n{retrieved}")
])

# ---------------- NODES ----------------
def node_receive(state: AgentState) -> AgentState:
    user_msg = next((m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None)
    state["query"] = user_msg.content.strip() if user_msg else ""
    state["to_index"] = []
    return state

def node_search(state: AgentState) -> AgentState:
    q = state["query"]
    web = tool_web_search(q)
    results = web["results"]
    state["search_results"] = results
    ts = datetime.now(timezone.utc).timestamp()
    for i, r in enumerate(results):
        text_blob = r.get("raw_content") or r.get("content")
        if text_blob:
            state["to_index"].append({
                "id": f"web::{ts}::{i}",
                "text": text_blob,
                "meta": f"title={r['title']};url={r['url']}"
            })
    if web.get("answer"):
        state["to_index"].append({
            "id": f"web_answer::{ts}",
            "text": web["answer"],
            "meta": "type=tavily_answer"
        })
    return state

def node_primary(state: AgentState) -> AgentState:
    prim = tool_filter_primary_sources(state.get("search_results", []))
    state["primary_sources"] = prim
    ts = datetime.now(timezone.utc).timestamp()
    for i, content in enumerate(prim):
        state["to_index"].append({
            "id": f"primary::{ts}::{i}",
            "text": content,
            "meta": "type=primary_source"
        })
    return state

def node_generate(state: AgentState) -> AgentState:
    # index conversation
    last_turn = "\n".join([f"{'user' if isinstance(m, HumanMessage) else 'assistant'}: {m.content}"
                           for m in state["messages"]])
    state["to_index"].append({
        "id": f"conv::{datetime.now(timezone.utc).timestamp()}",
        "text": last_turn,
        "meta": "type=conversation_turn"
    })
    add_to_chroma(state.get("to_index", []))
    state["to_index"] = []

    retrieved = retrieve_context(state["query"], k=8)

    # clickable citations
    citations = [f"[{r['title']}]({r['url']})" for r in state.get("search_results", []) if r.get("url")]
    citations_md = "\n".join(citations) if citations else "No references found."
    sources_block = "\n".join(state.get("primary_sources", [])) if state.get("primary_sources") else "None"

    # report
    report_msgs = REPORT_PROMPT.format_messages(
        query=state["query"], sources=sources_block,
        retrieved=f"{retrieved}\n\n### References\n{citations_md}"
    )
    state["report_md"] = safe_llm_invoke(report_msgs)

    # answer
    answer_msgs = ANSWER_PROMPT.format_messages(query=state["query"], retrieved=retrieved)
    state["answer"] = safe_llm_invoke(answer_msgs)

    add_to_chroma([{
        "id": f"report::{datetime.now(timezone.utc).timestamp()}",
        "text": state["report_md"],
        "meta": "type=report_md"
    }])
    return state

# ---------------- GRAPH ----------------
graph = StateGraph(AgentState)
graph.add_node("receive", node_receive)
graph.add_node("search", node_search)
graph.add_node("primary", node_primary)
graph.add_node("generate", node_generate)
graph.add_edge("receive", "search")
graph.add_edge("search", "primary")
graph.add_edge("primary", "generate")
graph.add_edge("generate", END)
graph.set_entry_point("receive")

checkpointer = MemorySaver()
compiled = graph.compile(checkpointer=checkpointer)

# ---------------- CHAT FUNCTION ----------------
def chat(thread_id: str, user_input: str) -> Dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    initial = {"messages": [HumanMessage(content=user_input)]}
    state = compiled.invoke(initial, config=config)
    full_msgs = initial["messages"] + [AIMessage(content=state["answer"])]
    save_markdown_transcript(thread_id, full_msgs, report_md=state["report_md"])
    return {
        "answer": state["answer"],
        "report_md": state["report_md"],
        "transcript_path": str(TRANSCRIPTS_DIR / f"conversation_{thread_id}.md")
    }

# ---------------- INTERACTIVE LOOP ----------------
if __name__ == "__main__":
    print("Historical Agent Chat — type 'exit' or 'quit' to end.")
    thread_id = "thread-1"
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting chat. Transcript saved.")
                break
            response = chat(thread_id, user_input)
            print("\nAssistant:", response["answer"])
            print("(Transcript updated:", response["transcript_path"], ")")
        except KeyboardInterrupt:
            print("\nExiting chat. Transcript saved.")
            break
