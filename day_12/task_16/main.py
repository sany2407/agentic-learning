from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.tools import FunctionTool
import sqlite3
import os
from dotenv import load_dotenv
import asyncio
import re

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")  

# Expanded content for facts.db (initialized with more sample data across multiple topics)
def init_fact_db():
    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS facts
                 (topic TEXT, fact TEXT)''')
    
    # Expanded sample data for various debate topics
    facts_data = [
        ('climate change', 'Global temperatures have risen 1.1°C since pre-industrial times.'),
        ('climate change', 'CO2 levels are at 420 ppm, highest in 800,000 years.'),
        ('climate change', 'Sea levels have risen by 20 cm since 1900 due to melting ice caps and thermal expansion.'),
        ('climate change', 'Arctic sea ice has declined at a rate of 13% per decade since 1979.'),
        ('climate change', 'Ocean acidity has increased by 30% since the industrial revolution.'),
        ('climate change', 'Global sea level rise is accelerating, currently at 3.3 mm per year.'),
        ('universal healthcare', 'Countries with universal healthcare like Canada spend 10.8% of GDP on health, vs. 16.9% in the US.'),
        ('universal healthcare', 'Life expectancy in the US is 78.6 years, lower than 82.3 in countries with universal systems.'),
        ('universal healthcare', 'Over 28 million Americans remain uninsured as of 2023.'),
        ('artificial intelligence', 'AI could add $15.7 trillion to the global economy by 2030.'),
        ('artificial intelligence', 'By 2025, 85 million jobs may be displaced by AI, but 97 million new ones created.'),
        ('artificial intelligence', 'AI systems can perpetuate biases if trained on skewed data.'),
        ('renewable energy', 'Solar power costs have dropped 89% since 2010.'),
        ('renewable energy', 'Wind energy can supply over 35% of global electricity by 2050.'),
        ('renewable energy', 'Fossil fuels still account for 80% of global energy production as of 2023.')
    ]
    
    for topic, fact in facts_data:
        c.execute("INSERT OR IGNORE INTO facts VALUES (?, ?)", (topic, fact))
    
    conn.commit()
    conn.close()

# Tool for querying facts (using FunctionTool)
def query_facts(topic: str) -> list:
    """Query facts from the local database for a given topic."""
    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    c.execute("SELECT fact FROM facts WHERE topic LIKE ?", (f'%{topic}%',))
    results = c.fetchall()
    conn.close()
    return [row[0] for row in results]

fact_tool = FunctionTool(query_facts, description="Retrieve facts from local DB for debate support.")

# LLM Client configuration
model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=api_key,
    model_info=ModelInfo(
        vision=False,
        function_calling=True,
        json_output=True,
        family="unknown",
        structured_output=True
    )
)

# Define agents
research_agent = AssistantAgent(
    name="ResearchAgent",
    description="A research agent for fetching facts.",
    system_message="""You research facts from the local database. 
    Use the query_facts tool to fetch relevant facts for the given topic.
    Summarize the most relevant facts that support or relate to the user's argument.
    Format your response as: 'RESEARCH COMPLETE: [list of relevant facts]'""",
    model_client=model_client,
    tools=[fact_tool],
)

argument_agent = AssistantAgent(
    name="ArgumentAgent",
    description="An argument generation agent.",
    system_message="""You generate strong, structured arguments based on the user's stance and provided facts.
    Build compelling arguments that support the user's position using the researched facts.
    Consider logical reasoning, evidence-based claims, and persuasive structure.
    Format your response as: 'ARGUMENTS GENERATED:' followed by bullet points of strong arguments.""",
    model_client=model_client,
)

rebuttal_agent = AssistantAgent(
    name="RebuttalAgent",
    description="A rebuttal generation agent.",
    system_message="""You generate rebuttals to counter potential opposing arguments.
    Think about what opponents might say against the user's position and prepare counter-arguments.
    Use facts and logical reasoning to strengthen rebuttals.
    Format your response as: 'REBUTTALS GENERATED:' followed by bullet points of counter-arguments.""",
    model_client=model_client,
)

evaluator_agent = AssistantAgent(
    name="EvaluatorAgent",
    description="An agent that evaluates argument strength.",
    system_message="""You evaluate the strength of debate arguments based on:
    1. Evidence quality and relevance (30%)
    2. Logical reasoning and structure (25%) 
    3. Persuasiveness and clarity (25%)
    4. Rebuttal preparedness (20%)
    
    Provide a score from 1-10 and brief explanation.
    Format: 'EVALUATION COMPLETE: Score: X/10 - [brief explanation]'
    End your message with 'DEBATE_ANALYSIS_DONE' to signal completion.""",
    model_client=model_client,
)

# Termination condition
text_mention_termination = TextMentionTermination("DEBATE_ANALYSIS_DONE")
max_messages_termination = MaxMessageTermination(max_messages=15)
termination = text_mention_termination | max_messages_termination

# Group Chat: Using RoundRobinGroupChat for better coordination
group_chat = RoundRobinGroupChat(
    [research_agent, argument_agent, rebuttal_agent, evaluator_agent],
    termination_condition=termination,
)

# StateFlow: Manages the debate preparation process
class StateFlow:
    def __init__(self):
        self.topic = None
        self.user_argument = None
        self.facts = []
        self.arguments = []
        self.rebuttals = []
        self.score = 0

    def parse_input(self, message):
        """Parse user input to extract topic and their argument/stance"""
        # Try different input formats
        if "topic:" in message.lower() and "argument:" in message.lower():
            # Format: topic: climate change, argument: sea levels are rising
            topic_match = re.search(r'topic:\s*([^,]+)', message.lower())
            arg_match = re.search(r'argument:\s*(.+)', message.lower())
            if topic_match and arg_match:
                self.topic = topic_match.group(1).strip()
                self.user_argument = arg_match.group(1).strip()
        elif "," in message:
            # Format: climate change, sea levels are rising due to climate change
            parts = message.split(",", 1)
            if len(parts) == 2:
                self.topic = parts[0].strip()
                self.user_argument = parts[1].strip()
        else:
            # Single input - treat as topic with generic stance
            self.topic = message.strip()
            self.user_argument = f"supporting {self.topic}"
        
        print(f"Parsed - Topic: '{self.topic}', User Argument: '{self.user_argument}'")

    def extract_results(self, messages):
        """Extract results from agent messages"""
        for msg in messages:
            content = msg.content
            if msg.source == "ResearchAgent" and "RESEARCH COMPLETE:" in content:
                facts_text = content.split("RESEARCH COMPLETE:")[1].strip()
                self.facts.append(facts_text)
            elif msg.source == "ArgumentAgent" and "ARGUMENTS GENERATED:" in content:
                args_text = content.split("ARGUMENTS GENERATED:")[1].strip()
                self.arguments.append(args_text)
            elif msg.source == "RebuttalAgent" and "REBUTTALS GENERATED:" in content:
                rebuttals_text = content.split("REBUTTALS GENERATED:")[1].strip()
                self.rebuttals.append(rebuttals_text)
            elif msg.source == "EvaluatorAgent" and "EVALUATION COMPLETE:" in content:
                eval_text = content.split("EVALUATION COMPLETE:")[1].strip()
                # Extract score
                score_match = re.search(r'Score:\s*(\d+)/10', eval_text)
                if score_match:
                    self.score = int(score_match.group(1))

    def display_results(self):
        """Display the final results"""
        print("\n" + "="*60)
        print("DEBATE PREPARATION RESULTS")
        print("="*60)
        
        print(f"\nTopic: {self.topic}")
        print(f"Your Argument: {self.user_argument}")
        
        if self.facts:
            print("\n📊 RESEARCHED FACTS:")
            for fact in self.facts:
                print(f"  {fact}")
        
        if self.arguments:
            print("\n💪 SUPPORTING ARGUMENTS:")
            for arg in self.arguments:
                print(f"  {arg}")
        
        if self.rebuttals:
            print("\n🛡️ PREPARED REBUTTALS:")
            for reb in self.rebuttals:
                print(f"  {reb}")
        
        print(f"\n🎯 ARGUMENT STRENGTH SCORE: {self.score}/10")
        print("="*60)

# Main function to run the debate
async def run_debate():
    init_fact_db()
    stateflow = StateFlow()
    
    # Get user input
    print("Welcome to the Automated Debate Coach!")
    print("Enter your debate topic and argument in one of these formats:")
    print("1. 'topic: climate change, argument: sea levels are rising'")
    print("2. 'climate change, sea levels are rising due to human activity'")
    print("3. Just the topic: 'climate change'\n")
    
    user_input = input("Enter your debate topic and argument: ")
    stateflow.parse_input(user_input)
    
    if not stateflow.topic:
        print("Invalid input. Please provide a topic.")
        return
    
    # Create the task for agents
    task = f"""
    Prepare a comprehensive debate analysis for:
    Topic: {stateflow.topic}
    User's Argument/Position: {stateflow.user_argument}
    
    Each agent should:
    1. ResearchAgent: Find relevant facts from the database
    2. ArgumentAgent: Generate strong supporting arguments 
    3. RebuttalAgent: Prepare counter-arguments to opposition
    4. EvaluatorAgent: Score the overall argument strength
    
    Work together to provide a complete debate preparation package.
    """
    
    print(f"\n🚀 Starting debate preparation for: {stateflow.topic}")
    print("Working with our team of specialist agents...\n")
    
    # Run the group chat
    chat_result = await group_chat.run(task=task)
    
    # Extract and display results
    stateflow.extract_results(chat_result.messages)
    stateflow.display_results()

if __name__ == "__main__":
    asyncio.run(run_debate())