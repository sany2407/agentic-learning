from crewai import Agent, Task, Crew, Process, LLM
from typing import List, Dict, Any
import json
import os
from datetime import datetime
from dotenv import load_dotenv


class EventEngagementCrew:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.llm = self._setup_llm()
        self.attendee_analyst = self._create_attendee_analyst()
        self.engagement_strategist = self._create_engagement_strategist()
    
    def _setup_llm(self) -> LLM:
        """Configure LLM using CrewAI's direct approach"""
        # Set your API key as environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        if api_key.startswith('your_'):
            raise ValueError("Please replace 'your_actual_api_key_here' with your real API key")
        
        print(f"✅ Using API key: {api_key[:10]}...{api_key[-4:]}")
        
        # Ensure underlying Gemini provider also sees the key if it expects GOOGLE_API_KEY
        os.environ['GOOGLE_API_KEY'] = api_key
        
        # Configure LLM with advanced parameters
        return LLM(
            model="gemini/gemini-1.5-flash",  # Using a stable model
            temperature=0.7,
            timeout=120,
            max_tokens=4000,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            seed=42
        )
    
    def _create_attendee_analyst(self) -> Agent:
        """Create the Attendee Analyst Agent"""
        return Agent(
            role="Attendee Analyst",
            goal="Identify engagement gaps and analyze attendee behavior patterns to provide data-driven insights",
            backstory="""You are an event data specialist with extensive experience in analyzing 
            attendee behavior, participation rates, and feedback metrics. You have a keen eye for 
            identifying patterns in engagement data and can spot areas where attendee participation 
            could be improved. Your analytical skills help event organizers understand what works 
            and what doesn't in their events.""",
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            llm=self.llm  # Use the configured LLM instance
        )
    
    def _create_engagement_strategist(self) -> Agent:
        """Create the Engagement Strategist Agent"""
        return Agent(
            role="Engagement Strategist",
            goal="Develop comprehensive engagement strategies to boost attendee participation based on analytical findings",
            backstory="""You are an experienced event planning consultant specializing in attendee 
            engagement and participation enhancement. You excel at translating data insights into 
            actionable strategies that increase attendee satisfaction and engagement. Your expertise 
            spans various event formats and you understand how to create compelling experiences that 
            keep attendees actively involved.""",
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            llm=self.llm  # Use the same configured LLM instance
        )
    
    def _create_attendee_analysis_task(self, events_data: List[Dict[str, Any]]) -> Task:
        """Create the Attendee Analysis Task"""
        return Task(
            description=f"""Analyze the attendee engagement data for the following events/sessions:
            {json.dumps(events_data, indent=2)}
            
            Your analysis should include:
            1. Participation rate analysis for each event/session
            2. Attendee feedback sentiment analysis
            3. Engagement pattern identification (peak engagement times, drop-off points)
            4. Demographic analysis of engaged vs. disengaged attendees
            5. Session format effectiveness comparison
            6. Identification of engagement gaps and problem areas
            
            Focus on quantitative metrics such as:
            - Attendance rates
            - Session completion rates
            - Q&A participation
            - Poll/survey response rates
            - Social media engagement
            - Post-event feedback scores
            
            Provide specific insights about what's working well and what needs improvement.""",
            
            expected_output="""A comprehensive analysis report containing:
            - Executive summary of engagement findings
            - Detailed metrics breakdown for each event/session
            - Identified engagement gaps and patterns
            - Comparative analysis across different session types
            - Key recommendations for the Engagement Strategist
            - Data-driven insights formatted in clear, actionable sections""",
            
            agent=self.attendee_analyst
        )
    
    def _create_engagement_strategy_task(self, events_data: List[Dict[str, Any]]) -> Task:
        """Create the Engagement Strategy Task"""
        return Task(
            description=f"""Based on the Attendee Analyst's findings, develop a comprehensive 
            engagement strategy for the events/sessions:
            {json.dumps(events_data, indent=2)}
            
            Your strategy should address:
            1. Pre-event engagement tactics to build anticipation
            2. During-event engagement techniques to maintain participation
            3. Post-event follow-up strategies to sustain engagement
            4. Technology solutions to enhance interaction
            5. Content optimization recommendations
            6. Session format improvements
            7. Gamification and incentive programs
            8. Community building initiatives
            
            Ensure your recommendations are:
            - Specific and actionable
            - Budget-conscious with ROI considerations
            - Tailored to the identified engagement gaps
            - Scalable across different event types
            - Measurable with clear KPIs""",
            
            expected_output="""A detailed engagement enhancement strategy including:
            - Strategic overview and objectives
            - Pre-event engagement plan with specific tactics
            - During-event engagement techniques and tools
            - Post-event retention and follow-up strategies
            - Technology recommendations and implementation timeline
            - Budget estimates and ROI projections
            - Success metrics and KPIs for measuring improvement
            - Implementation roadmap with priorities and timelines""",
            
            agent=self.engagement_strategist,
            context=[self._create_attendee_analysis_task(events_data)]
        )
    
    def analyze_and_strategize(self, events_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the complete analysis and strategy development process"""
        
        # Create tasks with the provided events data
        analysis_task = self._create_attendee_analysis_task(events_data)
        strategy_task = self._create_engagement_strategy_task(events_data)
        
        # Create and configure the crew
        crew = Crew(
            agents=[self.attendee_analyst, self.engagement_strategist],
            tasks=[analysis_task, strategy_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        return result


def save_results_to_markdown(results, events_data: List[Dict[str, Any]], filename: str = None):
    """Save the analysis and strategy results to a Markdown file"""
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"event_engagement_analysis_{timestamp}.md"
    
    # Prepare event summary for the header
    event_names = [event.get('event_name', 'Unknown Event') for event in events_data]
    total_events = len(events_data)
    
    # Create markdown content
    markdown_content = f"""# Event Attendee Engagement Analysis Report

**Generated on:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

**Events Analyzed:** {total_events}
- {chr(10).join([f"• {name}" for name in event_names])}

---

## 📊 Executive Summary

This report provides a comprehensive analysis of event attendee engagement patterns and actionable strategies to enhance participation across all analyzed events.

---

## 🔍 Detailed Analysis Results

{str(results).replace('\\n', '\n')}

---

## 📈 Event Data Summary

"""
    
    # Add event data summary
    for i, event in enumerate(events_data, 1):
        markdown_content += f"""### Event {i}: {event.get('event_name', 'Unknown Event')}

**Event Type:** {event.get('event_type', 'N/A')}  
**Event ID:** {event.get('event_id', 'N/A')}

#### Overall Metrics
- **Total Registered:** {event.get('overall_metrics', {}).get('total_registered', 'N/A')}
- **Total Attended:** {event.get('overall_metrics', {}).get('total_attended', 'N/A')}
- **Overall Satisfaction:** {event.get('overall_metrics', {}).get('overall_satisfaction', 'N/A')}/5.0
- **Net Promoter Score:** {event.get('overall_metrics', {}).get('net_promoter_score', 'N/A')}

#### Sessions
"""
        
        sessions = event.get('sessions', [])
        for j, session in enumerate(sessions, 1):
            markdown_content += f"""
**Session {j}: {session.get('session_name', 'Unknown Session')}**
- Type: {session.get('session_type', 'N/A')}
- Duration: {session.get('duration_minutes', 'N/A')} minutes
- Registered Attendees: {session.get('registered_attendees', 'N/A')}
- Actual Attendees: {session.get('actual_attendees', 'N/A')}
- Completion Rate: {session.get('completion_rate', 'N/A')}
- Q&A Participants: {session.get('q_and_a_participants', 'N/A')}
- Feedback Score: {session.get('feedback_score', 'N/A')}/5.0

**Engagement Metrics:**
- Poll Responses: {session.get('engagement_metrics', {}).get('poll_responses', 'N/A')}
- Chat Messages: {session.get('engagement_metrics', {}).get('chat_messages', 'N/A')}
- Social Shares: {session.get('engagement_metrics', {}).get('social_shares', 'N/A')}

"""
    
    markdown_content += f"""

---

## 🚀 Next Steps

1. **Review Analysis:** Carefully examine the identified engagement gaps and patterns
2. **Implement Strategies:** Begin with high-impact, low-cost recommendations
3. **Monitor Progress:** Track the suggested KPIs to measure improvement
4. **Iterate:** Continuously refine strategies based on new data

---

## 📋 Technical Details

**Analysis Tool:** CrewAI Event Engagement System  
**AI Model:** Google Gemini 1.5 Flash  
**Report Format:** Markdown  
**File:** `{filename}`

---

*This report was generated automatically using AI-powered analysis. Please review recommendations with your event planning team before implementation.*
"""
    
    # Write to file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"\n📄 Results saved to: {filename}")
        print(f"📁 Full path: {os.path.abspath(filename)}")
        return filename
        
    except Exception as e:
        print(f"❌ Error saving to markdown file: {str(e)}")
        return None


def verify_setup():
    """Verify that everything is set up correctly"""
    print("🔍 Verifying setup...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
        load_dotenv()
    else:
        print("⚠️  .env file not found, checking system environment variables")
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        print("Please set GEMINI_API_KEY in your .env file or as an environment variable")
        return False
    
    if api_key.startswith('your_'):
        print("❌ API key appears to be a placeholder")
        print("Please replace it with your actual Google Gemini API key")
        return False
    
    print(f"✅ API key loaded: {api_key[:10]}...{api_key[-4:]}")
    
    # Test CrewAI import
    try:
        from crewai import LLM
        print("✅ CrewAI imported successfully")
    except ImportError as e:
        print(f"❌ CrewAI import failed: {e}")
        return False
    
    return True


def load_events_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load events data from a JSON file"""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found. Using sample data instead.")
        return []
    except json.JSONDecodeError:
        print(f"Invalid JSON format in {file_path}. Using sample data instead.")
        return []


def run_with_file_input(file_path: str = "events_data.json"):
    """Run the crew system with data loaded from a file"""
    events_data = load_events_from_file(file_path)
    
    if not events_data:
        print("No valid events data found. Please check your file or use the sample data.")
        return
    
    engagement_crew = EventEngagementCrew()
    results = engagement_crew.analyze_and_strategize(events_data)
    
    # Save results to markdown
    save_results_to_markdown(results, events_data)
    
    return results


def main():
    # Verify setup before running
    if not verify_setup():
        print("\n📝 Setup Instructions:")
        print("1. Create a .env file in your project directory")
        print("2. Add your API key: GEMINI_API_KEY=your_actual_api_key_here")
        print("3. Get your API key from: https://aistudio.google.com/")
        return
    
    # Sample event data
    sample_events_data = [
        {
            "event_id": "EVENT_001",
            "event_name": "Annual Tech Conference 2024",
            "event_type": "Conference",
            "sessions": [
                {
                    "session_id": "SESS_001",
                    "session_name": "AI Innovation Keynote",
                    "session_type": "Keynote",
                    "duration_minutes": 60,
                    "registered_attendees": 500,
                    "actual_attendees": 420,
                    "completion_rate": 0.85,
                    "q_and_a_participants": 45,
                    "feedback_score": 4.2,
                    "engagement_metrics": {
                        "poll_responses": 280,
                        "chat_messages": 156,
                        "social_shares": 89
                    }
                },
                {
                    "session_id": "SESS_002",
                    "session_name": "Interactive Workshop: ML Basics",
                    "session_type": "Workshop",
                    "duration_minutes": 120,
                    "registered_attendees": 150,
                    "actual_attendees": 98,
                    "completion_rate": 0.72,
                    "q_and_a_participants": 32,
                    "feedback_score": 3.8,
                    "engagement_metrics": {
                        "poll_responses": 67,
                        "chat_messages": 234,
                        "social_shares": 23
                    }
                }
            ],
            "overall_metrics": {
                "total_registered": 2500,
                "total_attended": 1890,
                "overall_satisfaction": 4.0,
                "net_promoter_score": 65
            }
        },
        {
            "event_id": "EVENT_002",
            "event_name": "Monthly Product Demo",
            "event_type": "Webinar",
            "sessions": [
                {
                    "session_id": "SESS_003",
                    "session_name": "Product Feature Showcase",
                    "session_type": "Demo",
                    "duration_minutes": 45,
                    "registered_attendees": 300,
                    "actual_attendees": 180,
                    "completion_rate": 0.60,
                    "q_and_a_participants": 25,
                    "feedback_score": 3.5,
                    "engagement_metrics": {
                        "poll_responses": 89,
                        "chat_messages": 67,
                        "social_shares": 12
                    }
                }
            ],
            "overall_metrics": {
                "total_registered": 300,
                "total_attended": 180,
                "overall_satisfaction": 3.5,
                "net_promoter_score": 45
            }
        }
    ]
    
    print("🚀 Starting Event Attendee Engagement Analysis...")
    print("=" * 70)
    
    try:
        # Initialize the crew system
        engagement_crew = EventEngagementCrew()
        
        # Execute analysis and strategy development
        results = engagement_crew.analyze_and_strategize(sample_events_data)
        
        print("\n✅ Analysis and Strategy Development Completed!")
        print("=" * 70)
        print("\n📊 Results:")
        print(results)
        
        # Save results to markdown file
        markdown_file = save_results_to_markdown(results, sample_events_data)
        
        if markdown_file:
            print(f"\n🎉 Complete analysis report saved as: {markdown_file}")
            print("📖 Open the file to view the formatted report with:")
            print(f"   - Detailed analysis findings")
            print(f"   - Strategic recommendations")
            print(f"   - Event data summaries")
            print(f"   - Implementation roadmap")
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("- Ensure your API key is valid and not expired")
        print("- Check your internet connection")
        print("- Verify you have credits remaining in your Google Cloud account")


if __name__ == "__main__":
    main()
