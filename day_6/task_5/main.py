import os
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.agents import initialize_agent, AgentType
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain_tavily import TavilySearch
import warnings
import datetime  # Added for timestamps
from PyPDF2 import PdfReader  # Added for PDF text extraction

# Temporarily disable warning suppression for debugging
# warnings.filterwarnings("ignore", category=DeprecationWarning)

# === 1. Setup Gemini LLM via langchain-google-genai ===
def get_gemini_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Please set the GOOGLE_API_KEY environment variable.")
    # Initialize Gemini chat model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
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
def create_chroma_vectorstore(embedding_function, persist_directory="chroma_db"):
    """
    Creates or loads a Chroma vector store and initializes with seed documents.
    Now handles PDF text extraction for seed docs.
    """
    # Example seed documents, including PDF text extraction
    seed_docs = []
    
    # Load text from PDF if path provided
    pdf_path = "your_pdf_path_here.pdf"  # Replace with actual PDF path
    if os.path.exists(pdf_path):
        reader = PdfReader(pdf_path)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        seed_docs.append(Document(page_content=pdf_text, metadata={"source": "PDF - Learn French"}))
    else:
        print(f"Warning: PDF path '{pdf_path}' not found. Skipping.")
    
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
    with open(filename, "a", encoding="utf-8") as f:  # Changed to append for conversational history
        f.write("\n\n---\n\n")  # Separator for each interaction
        f.write(content)
    print(f"Output appended to: {filename}")

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

    # Create or load persistent Chroma vector store
    vectordb = create_chroma_vectorstore(embeddings)

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

    # Conversational loop
    chat_history = []  # Maintain chat history for the agent
    print("Welcome to the Language Learning Agent! Type your query or 'exit' to quit.")
    
    while True:
        user_query = input("\nYou: ").strip()
        if user_query.lower() == "exit":
            break
        
        # Retrieve relevant docs from vector store as context
        relevant_docs = retriever.invoke(user_query)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # Combine context with query for richer input to agent
        full_prompt = f"{user_query}\n\nRelevant context:\n{context}"

        # Run agent with chat history
        response = agent.invoke({"input": full_prompt, "chat_history": chat_history})
        
        # Extract output
        if isinstance(response, dict) and 'output' in response:
            agent_output = response['output']
        else:
            agent_output = str(response)
            print("Warning: Unexpected response format.")
        
        print("\nAgent:", agent_output)
        
        # Save to Markdown
        save_to_markdown(f"User: {user_query}\nAgent: {agent_output}")
        
        # Store the response in Chroma DB for future retrieval
        timestamp = datetime.datetime.now().isoformat()
        new_doc = Document(
            page_content=agent_output,
            metadata={"source": "agent_response", "query": user_query, "timestamp": timestamp}
        )
        vectordb.add_documents([new_doc])  # Dynamically add to vector store
        print("Response stored in Chroma DB.")
        
        # Update chat history (simple append for context)
        chat_history.append(f"User: {user_query}")
        chat_history.append(f"Agent: {agent_output}")

    print("Conversation ended.")

if __name__ == "__main__":
    main()
