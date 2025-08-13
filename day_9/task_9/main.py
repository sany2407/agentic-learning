import os
import re
import requests
import logging
import json

from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langgraph_supervisor import create_supervisor
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# --------------------
# LOGGING SETUP
# --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------
# CONFIG
# --------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY environment variable")
if not OPENWEATHER_API_KEY:
    raise ValueError("Missing OPENWEATHER_API_KEY environment variable")

# Gemini LLM model
gemini_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)

# Gemini embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)

# --------------------
# VECTORSTORE SETUP
# --------------------
def initialize_vectorstore():
    try:
        persist_dir = "./chroma_db"
        vectorstore = Chroma(
            collection_name="weather_history",
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
        
        existing_docs = vectorstore.get()
        if not existing_docs['ids']:
            initial_documents = [
                Document(page_content="Coimbatore historical climate: Average annual temperature 24-28°C, monsoon season June-September with 600mm rainfall."),
                Document(page_content="Tamil Nadu weather patterns: Hot summers (35-40°C), moderate winters (20-25°C), southwest monsoon brings most rainfall."),
                Document(page_content="Coimbatore temperature trends: City experiences tropical wet and dry climate with moderate temperatures year-round."),
            ]
            vectorstore.add_documents(initial_documents)
            vectorstore.persist()
            logger.info(f"ChromaDB initialized in {persist_dir}")
        
        return vectorstore
    except Exception as e:
        logger.error(f"ChromaDB error: {e}")
        raise

vectorstore = initialize_vectorstore()

# --------------------
# ENHANCED TOOLS
# --------------------
def extract_city_from_query(query: str) -> str:
    """Extract city name from query."""
    patterns = [
        r"weather in ([A-Za-z\s,]+?)(?:\s|$|for)",
        r"([A-Za-z\s,]+?) weather",
        r"forecast for ([A-Za-z\s,]+?)(?:\s|$)",
        r"current weather ([A-Za-z\s,]+?)(?:\s|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            city = match.group(1).strip().rstrip(',')
            logger.info(f"Extracted city: {city}")
            return city
    
    return "London"

def classify_query(query: str) -> str:
    """Classify weather query type."""
    q = query.lower()
    
    if any(k in q for k in ["current", "today", "now", "right now"]):
        return "realtime"
    elif any(k in q for k in ["forecast", "tomorrow", "next", "will it"]):
        return "forecast"
    elif any(k in q for k in ["historical", "climate", "past", "trends"]):
        return "historical"
    
    return "realtime"  # Default to current weather

def openweather_fetch(city: str, mode: str = "weather"):
    """Fetch weather data from OpenWeather API."""
    try:
        base_url = "https://api.openweathermap.org/data/2.5/"
        endpoint = "forecast" if mode == "forecast" else "weather"
        params = {
            "q": city, 
            "appid": OPENWEATHER_API_KEY, 
            "units": "metric"
        }
        
        logger.info(f"Fetching {mode} data for {city}")
        response = requests.get(f"{base_url}{endpoint}", params=params, timeout=10)
        
        if response.status_code == 401:
            return {"error": "Invalid API key"}
        elif response.status_code == 404:
            return {"error": f"City '{city}' not found"}
        elif not response.ok:
            return {"error": f"API error: {response.status_code}"}
            
        data = response.json()
        logger.info(f"Successfully fetched data for {city}")
        return data
        
    except Exception as e:
        logger.error(f"API fetch error: {e}")
        return {"error": f"Network error: {str(e)}"}

def rag_search(query: str):
    """Search historical weather data."""
    try:
        results = vectorstore.similarity_search(query, k=2)
        if results:
            return "\n".join([doc.page_content for doc in results])
        return "No historical data found."
    except Exception as e:
        return f"Search error: {str(e)}"

def format_weather_response(raw_data: str) -> str:
    """Format raw weather data into user-friendly response."""
    try:
        # Try to parse as JSON if it's API data
        if raw_data.startswith('{'):
            data = json.loads(raw_data)
            
            if "error" in data:
                return f"Sorry, {data['error']}"
            
            # Current weather format
            if "main" in data and "weather" in data:
                temp = data["main"]["temp"]
                condition = data["weather"][0]["description"]
                city = data["name"]
                humidity = data["main"]["humidity"]
                
                return f"Current weather in {city} is {temp:.0f}°C with {condition}. Humidity: {humidity}%"
            
            # Forecast format
            elif "list" in data:
                city = data["city"]["name"]
                today_forecast = data["list"][0]
                temp = today_forecast["main"]["temp"]
                condition = today_forecast["weather"][0]["description"]
                
                return f"Weather forecast for {city}: {temp:.0f}°C with {condition}"
        
        # For historical data or plain text
        return raw_data
        
    except Exception as e:
        logger.error(f"Formatting error: {e}")
        return raw_data

# --------------------
# AGENTS WITH FIXED PROMPTS
# --------------------
router_agent = create_react_agent(
    model=gemini_model,
    tools=[classify_query],
    prompt="""You are a query router. Use the classify_query tool to determine the query type and return ONLY the classification result: 'realtime', 'forecast', or 'historical'.""",
    name="router_agent"
)

weather_agent = create_react_agent(
    model=gemini_model,
    tools=[extract_city_from_query, openweather_fetch, format_weather_response],
    prompt="""You are a weather data agent. For weather queries:
1. First use extract_city_from_query to get the city name
2. Then use openweather_fetch with the city and appropriate mode ('weather' for current, 'forecast' for forecast)
3. Finally use format_weather_response to format the data into a user-friendly response
4. Return the formatted response directly, do not say "transferring back" or similar phrases.""",
    name="weather_agent"
)

rag_agent = create_react_agent(
    model=gemini_model,
    tools=[rag_search],
    prompt="""You are a historical weather agent. Use rag_search to find historical weather information and return the results directly. Do not say "transferring back".""",
    name="rag_agent"
)

# --------------------
# SIMPLIFIED SUPERVISOR
# --------------------
supervisor_prompt = """You are a weather system supervisor. Route queries to the appropriate agent:

- For current weather or forecasts: Use 'weather_agent'
- For historical weather or climate data: Use 'rag_agent'

The agents will handle the complete workflow and return final responses. Do not route to multiple agents - each agent handles everything needed for their query type.

IMPORTANT: 
- Choose ONE agent based on the query type
- Let the agent complete the full task
- Return the agent's response as the final answer
"""

supervisor = create_supervisor(
    model=gemini_model,
    agents=[weather_agent, rag_agent],
    prompt=supervisor_prompt,
    add_handoff_back_messages=False,  # This prevents "transferring back" messages
    output_mode="full_history",
).compile()

# --------------------
# IMPROVED RESPONSE EXTRACTION
# --------------------
def extract_final_response(result):
    """Extract the final meaningful response."""
    try:
        messages = result.get("messages", [])
        
        # Look for the last agent response with actual content
        for message in reversed(messages):
            if isinstance(message, AIMessage) and message.content:
                content = message.content.strip()
                
                # Skip system messages and routing messages
                skip_phrases = [
                    "transferring back",
                    "I'll help you",
                    "Let me",
                    "I need to",
                    "I will",
                    "routing to"
                ]
                
                if not any(phrase in content.lower() for phrase in skip_phrases) and len(content) > 10:
                    # If it's a weather response, return it
                    if any(word in content.lower() for word in ["weather", "temperature", "°c", "°f", "humidity", "wind"]):
                        return content
                    # If it's longer than 20 chars and doesn't seem like a routing message
                    elif len(content) > 20:
                        return content
        
        return "Sorry, I couldn't process your weather request. Please try again."
        
    except Exception as e:
        logger.error(f"Response extraction error: {e}")
        return f"Error processing response: {str(e)}"

# --------------------
# MAIN PROGRAM
# --------------------
if __name__ == "__main__":
    print("🌦 Weather Multi-Agent System (type 'exit' to quit)")
    print("Ask about current weather, forecasts, or historical climate data!\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
            
            print("🔄 Processing your request...")
            logger.info(f"Processing query: {user_input}")
            
            # Invoke supervisor
            result = supervisor.invoke({"messages": [HumanMessage(content=user_input)]})
            
            # Extract and display response
            response = extract_final_response(result)
            print(f"Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Agent: Sorry, I encountered an error: {str(e)}\n")