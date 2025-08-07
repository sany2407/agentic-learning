import os
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.agents import initialize_agent, AgentType
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain_tavily import TavilySearch  
import warnings

# Temporarily disable warning suppression for debugging
# warnings.filterwarnings("ignore", category=DeprecationWarning)

# === 1. Setup Gemini LLM via langchain-google-genai ===
def get_gemini_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Please set the GOOGLE_API_KEY environment variable.")
    # Initialize Gemini chat model
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    return llm

# === 2. Tavily Search Tool (Updated to use langchain_tavily) ===
def create_tavily_tool() -> Tool:
    # Instantiate official TavilySearch tool
    # Note: Assumes TAVILY_API_KEY is set in environment
    tavily = TavilySearch(
        max_results=5, 
        topic="general",  
        description="Useful to search up-to-date web information about languages."
    )
    return tavily

# === 3. Chroma Vector Store Setup ===
def create_chroma_vectorstore(documents, embedding_function, persist_directory="chroma_db"):
    """
    Creates or loads a Chroma vector store from given documents and saves data persistently.
    """
    seed_docs = [
    Document(page_content="/Users/subashkannan/Desktop/agentic-learning-main/day_6/task_5/Learn-French-the-Fast-and-Fun-Way french free.pdf"),
]
    try:
        vectordb = Chroma.from_documents(
            documents=seed_docs,
            embedding=embedding_function,
            persist_directory=persist_directory
        )
        # Check if directory was created
        if os.path.exists(persist_directory):
            print(f"Chroma DB successfully created/loaded at: {persist_directory}")
        else:
            print(f"Warning: Chroma DB directory '{persist_directory}' not found after creation.")
        return vectordb
    except Exception as e:
        raise ValueError(f"Error creating Chroma vector store: {str(e)}")

# === 4. Custom Practice Exercise Generator Tool ===
class PracticeExerciseGenerator:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm

    def run(self, input_text: str) -> str:
        prompt = f"""
You are an expert language tutor. Generate personalized practice exercises in JSON format based on the following request:

{input_text}

The JSON should contain:
- exercise_type (e.g., vocabulary, grammar)
- instructions (string)
- questions (list of questions)
- explanations (if applicable)

Please provide only the JSON output.
"""
        response = self.llm.invoke(prompt)
        return response.content

def create_practice_tool(llm: ChatGoogleGenerativeAI) -> Tool:
    practice_gen = PracticeExerciseGenerator(llm)
    return Tool(
        name="PracticeExerciseGenerator",
        func=practice_gen.run,
        description="Generates personalized language practice exercises in JSON format."
    )

# === 5. Function to save generated content to Markdown ===
def save_to_markdown(content: str, filename: str = "language_learning_output.md"):
    """
    Saves the generated content to a Markdown file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Language Learning Agent Output\n\n")
        f.write(content)
    print(f"Output saved to: {filename}")

# === 6. Main program & agent integration ===
def main():
    # Load API keys from env
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("Please set the TAVILY_API_KEY environment variable.")

    # Initialize Gemini LLM
    gemini_llm = get_gemini_llm()

    # Use Google's Gemini embedding model for vector embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Example seed documents (could be extended or updated dynamically)
    seed_docs = [
        Document(page_content="Basic Spanish grammar includes verb conjugations.",
                 metadata={"source": "language_tips"}),
        Document(page_content="French verb conjugations vary with tense and subject pronoun.",
                 metadata={"source": "language_tips"})
    ]

    # Create or load persistent Chroma vector store
    vectordb = create_chroma_vectorstore(seed_docs, embeddings, persist_directory="chroma_db")

    # Setup retriever from Chroma vector store (top 3 similar docs)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # Create LangChain tools
    tavily_tool = create_tavily_tool()
    practice_tool = create_practice_tool(gemini_llm)
    tools = [tavily_tool, practice_tool]

    # Initialize agent with structured chat zero-shot React type
    agent = initialize_agent(
        tools,
        gemini_llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        return_intermediate_steps=False
    )

    # Example user query
    user_query = (
        "Give me grammar tips for beginner French focusing on verb conjugations, "
        "also generate practice exercises for the same."
    )

    # Retrieve relevant docs from vector store as context
    relevant_docs = retriever.invoke(user_query) 
    context = "\n".join([doc.page_content for doc in relevant_docs])

    # Combine context with query for richer input to agent
    full_prompt = f"{user_query}\n\nRelevant context:\n{context}"

    # Run agent and get response (provide empty chat_history)
    response = agent.invoke({"input": full_prompt, "chat_history": []})

    print("Agent Response:\n", response)

    # Save the generated response to a Markdown file (extract string from dict)
    if isinstance(response, dict) and 'output' in response:
        save_to_markdown(response['output'])
    else:
        print("Error: Unexpected response format from agent.")

if __name__ == "__main__":
    main()
