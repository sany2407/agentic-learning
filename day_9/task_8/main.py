# main.py
import os
import re
from typing import Literal, TypedDict

# ========================
# 1. Financial calculation functions
# ========================
def simple_interest(principal: float, rate: float, time: float) -> float:
    return principal * (rate / 100) * time

def compound_interest(principal: float, rate: float, time: float, periods: int) -> float:
    amount = principal * (1 + (rate / 100) / periods) ** (periods * time)
    return amount - principal

def future_value(principal: float, rate: float, time: float) -> float:
    return principal * ((1 + rate / 100) ** time)

def present_value(fv: float, rate: float, time: float) -> float:
    return fv / ((1 + rate / 100) ** time)

# ========================
# 2. Gemini LLM for general queries
# ========================
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(
        "Missing GOOGLE_API_KEY! Please set it via: export GOOGLE_API_KEY='your_key_here'"
    )

llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

def llm_node(state: dict) -> dict:
    """Handles general non-financial queries."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{query}")
    ])
    chain = prompt | llm_model
    resp = chain.invoke({"query": state["query"]})
    state["response"] = resp.content
    return state

# ========================
# 3. Financial query handler node
# ========================
def financial_tool_node(state: dict) -> dict:
    query = state["query"].lower()

    # Simple Interest
    if "simple interest" in query:
        match = re.search(r"(\d+\.?\d*).+?(\d+\.?\d*)%.+?(\d+)", query)
        if match:
            p, r, t = map(float, match.groups())
            state["response"] = f"Simple Interest = {simple_interest(p, r, t):.2f}"
            return state

    # Compound Interest
    elif "compound interest" in query:
        match = re.search(r"(\d+\.?\d*).+?(\d+\.?\d*)%.+?(\d+).+?(\d+)", query)
        if match:
            p, r, t, n = map(float, match.groups())
            state["response"] = f"Compound Interest = {compound_interest(p, r, t, int(n)):.2f}"
            return state

    # Future Value
    elif "future value" in query:
        match = re.search(r"(\d+\.?\d*).+?(\d+\.?\d*)%.+?(\d+)", query)
        if match:
            p, r, t = map(float, match.groups())
            state["response"] = f"Future Value = {future_value(p, r, t):.2f}"
            return state

    # Present Value
    elif "present value" in query:
        match = re.search(r"(\d+\.?\d*).+?(\d+\.?\d*)%.+?(\d+)", query)
        if match:
            fv, r, t = map(float, match.groups())
            state["response"] = f"Present Value = {present_value(fv, r, t):.2f}"
            return state

    state["response"] = "I couldn't parse your financial query. Please provide it clearly."
    return state

# ========================
# 4. LangGraph setup
# ========================
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    query: str
    response: str

def router_node(state: AgentState) -> AgentState:
    return state

def router(state: AgentState) -> Literal["financial", "llm"]:
    query = state["query"].lower()
    if any(k in query for k in ["simple interest", "compound interest", "future value", "present value"]):
        return "financial"
    return "llm"

def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("llm", llm_node)
    graph.add_node("financial", financial_tool_node)
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", router, {
        "financial": "financial",
        "llm": "llm"
    })
    return graph.compile()


# ========================
# 5. Run agent
# ========================
if __name__ == "__main__":
    agent_executor = build_agent()
    print("💰 Financial Calculation Agent Ready! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        result = agent_executor.invoke({"query": user_input})
        print("Agent:", result["response"])
        print("-" * 50)
