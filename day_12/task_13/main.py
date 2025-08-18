import asyncio
import json
import time
import re
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# AutoGen Core imports for Gemini integration
from autogen_core.models import UserMessage, AssistantMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

@dataclass
class DebateMetrics:
    logic_score: int = 0
    evidence_score: int = 0
    clarity_score: int = 0
    relevance_score: int = 0
    persuasiveness_score: int = 0
    
    def total_score(self) -> int:
        return sum([self.logic_score, self.evidence_score, self.clarity_score, 
                   self.relevance_score, self.persuasiveness_score])
    
    def weighted_score(self) -> float:
        weights = {
            'logic_score': 0.30,
            'evidence_score': 0.25,
            'clarity_score': 0.20,
            'relevance_score': 0.15,
            'persuasiveness_score': 0.10
        }
        return sum(getattr(self, field) * weight for field, weight in weights.items())

class DebateSession:
    def __init__(self):
        self.scores = {"participant_a": 0, "participant_b": 0}
        self.detailed_scores = {"participant_a": [], "participant_b": []}
        self.arguments = {"participant_a": [], "participant_b": []}
        self.rounds = 0
        self.max_rounds = 3
        self.current_topic = ""
        self.fairness_violations = []
        self.feedback_log = []
        self.evaluation_history = []
        
    def add_argument(self, participant: str, argument: str, metrics: DebateMetrics):
        weighted_score = metrics.weighted_score()
        self.arguments[participant].append({
            "argument": argument,
            "metrics": metrics,
            "weighted_score": weighted_score,
            "total_score": metrics.total_score(),
            "round": self.rounds + 1
        })
        self.detailed_scores[participant].append(metrics)
        self.scores[participant] += weighted_score
        
    def add_feedback(self, participant: str, feedback: str):
        """Add feedback for a participant"""
        self.feedback_log.append({
            "participant": participant,
            "feedback": feedback,
            "round": self.rounds,
            "timestamp": time.time()
        })
        
    def add_fairness_violation(self, violation: str):
        """Add a fairness violation to the record"""
        self.fairness_violations.append({
            "violation": violation,
            "round": self.rounds,
            "timestamp": time.time()
        })
        
    def add_evaluation(self, round_num: int, participant: str, evaluation: str):
        self.evaluation_history.append({
            "round": round_num,
            "participant": participant,
            "evaluation": evaluation,
            "timestamp": time.time()
        })
        
    def get_status(self):
        return {
            "scores": self.scores,
            "detailed_scores": self.detailed_scores,
            "rounds": self.rounds,
            "topic": self.current_topic,
            "fairness_violations": self.fairness_violations,
            "feedback_log": self.feedback_log,
            "arguments_count": {
                "participant_a": len(self.arguments["participant_a"]),
                "participant_b": len(self.arguments["participant_b"])
            },
            "evaluation_history": self.evaluation_history
        }

# Global debate session
debate_session = DebateSession()

class GeminiModelManager:
    """Manager for Gemini model clients using AutoGen's OpenAI-compatible API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.clients = {}
        
    async def get_client(self, model_name: str = "gemini-1.5-flash-8b") -> OpenAIChatCompletionClient:
        """Get or create a Gemini model client"""
        if model_name not in self.clients:
            if model_name == "gemini-2.0-flash-lite":
                # For newer models with enhanced capabilities
                self.clients[model_name] = OpenAIChatCompletionClient(
                    model=model_name,
                    model_info=ModelInfo(
                        vision=True,
                        function_calling=True,
                        json_output=True,
                        family="gemini",
                        structured_output=True
                    ),
                    api_key=self.api_key,
                )
            else:
                # For standard Gemini models
                self.clients[model_name] = OpenAIChatCompletionClient(
                    model=model_name,
                    api_key=self.api_key,
                )
        
        return self.clients[model_name]
    
    async def close_all(self):
        """Close all model clients"""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()

class DebateAgent:
    """Base class for all debate agents using Gemini models"""
    
    def __init__(self, name: str, system_message: str, model_manager: GeminiModelManager, 
                 model_name: str = "gemini-1.5-flash-8b"):
        self.name = name
        self.system_message = system_message
        self.model_manager = model_manager
        self.model_name = model_name
        self.conversation_history = []
        
    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process a message and return the agent's response"""
        try:
            client = await self.model_manager.get_client(self.model_name)
            
            # Build message list with system message and user input
            messages = [
                UserMessage(content=f"SYSTEM: {self.system_message}", source="system"),
                UserMessage(content=message, source="user")
            ]
            
            # Add conversation history if needed
            if context and "history" in context:
                for hist_msg in context["history"][-3:]:  # Last 3 messages for context
                    messages.append(UserMessage(content=hist_msg, source="user"))
            
            response = await client.create(messages)
            
            # Extract response content
            response_content = ""
            if hasattr(response, 'content') and response.content:
                if isinstance(response.content, list):
                    response_content = " ".join(item.text if hasattr(item, 'text') else str(item) 
                                             for item in response.content)
                else:
                    response_content = str(response.content)
            elif hasattr(response, 'choices') and response.choices:
                response_content = response.choices[0].message.content
            else:
                response_content = str(response)
            
            # Add to conversation history
            self.conversation_history.append({
                "input": message,
                "output": response_content,
                "timestamp": time.time()
            })
            
            return response_content
            
        except Exception as e:
            error_msg = f"Error in {self.name}: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

class TopicGeneratorAgent(DebateAgent):
    def __init__(self, model_manager: GeminiModelManager):
        system_message = """You are an expert Topic Generator for formal debates. Generate balanced, engaging debate topics that allow for legitimate arguments on both sides.

When generating a topic, provide:
- **Topic Statement**: Clear, specific debate resolution
- **Context**: 2-3 sentences explaining relevance and importance
- **Pro Arguments**: 3 key points supporting the affirmative position
- **Con Arguments**: 3 key points supporting the negative position
- **Debate Structure**: Suggested format and timing

Ensure topics are:
- Current and relevant to modern society
- Balanced with legitimate perspectives on both sides
- Specific enough to allow focused arguments
- Based on factual foundations rather than pure opinion

Format your response with clear headers and bullet points for easy reading."""
        
        super().__init__("TopicGenerator", system_message, model_manager)

class ArgumentEvaluatorAgent(DebateAgent):
    def __init__(self, model_manager: GeminiModelManager):
        system_message = """You are a professional Argument Evaluator for formal debates. Provide objective, detailed analysis using these criteria:

**Evaluation Criteria (Score 1-10 each):**

1. **Logic & Reasoning (30% weight)**: Logical flow, absence of fallacies, sound reasoning
2. **Evidence & Facts (25% weight)**: Source quality, relevance, accuracy of supporting material
3. **Clarity & Presentation (20% weight)**: Clear communication, organization, appropriate language
4. **Topic Relevance (15% weight)**: Direct addressing of debate topic, staying on subject
5. **Persuasiveness (10% weight)**: Compelling presentation, balanced emotional appeal

**Required Format:**
- Logic & Reasoning: [Score]/10 - [Detailed justification]
- Evidence & Facts: [Score]/10 - [Detailed justification]
- Clarity & Presentation: [Score]/10 - [Detailed justification]
- Topic Relevance: [Score]/10 - [Detailed justification]
- Persuasiveness: [Score]/10 - [Detailed justification]
- **Total Score**: [Sum]/50
- **Strengths**: [Key positive aspects]
- **Areas for Improvement**: [Specific suggestions]

Be objective, fair, and constructive. Focus on argument quality, not position preference."""
        
        super().__init__("ArgumentEvaluator", system_message, model_manager)

class ScoreKeeperAgent(DebateAgent):
    def __init__(self, model_manager: GeminiModelManager):
        system_message = """You are the official Score Keeper for formal debates. Maintain accurate, transparent scoring records.

**Responsibilities:**
- Track individual argument scores by round
- Maintain cumulative participant scores  
- Calculate weighted scores based on evaluation criteria
- Provide statistical analysis and trends

**Reporting Format:**
- Current round scores with detailed breakdown
- Cumulative scores and current standings
- Round-by-round performance comparison
- Performance trends and insights
- Statistical summaries (averages, best/worst categories)

Present all information clearly with proper formatting. Highlight significant score changes or patterns. Ensure complete transparency in all calculations."""
        
        super().__init__("ScoreKeeper", system_message, model_manager)

class FairnessMonitorAgent(DebateAgent):
    def __init__(self, model_manager: GeminiModelManager):
        system_message = """You are the Fairness Monitor ensuring equitable treatment throughout the debate process.

**Monitoring Areas:**
- Participation equity (equal opportunities, balanced evaluation)
- Bias detection (evaluator bias, unfair advantages, prejudicial treatment)
- Conduct standards (respectful discourse, professional communication)
- Process integrity (consistent rule application, transparent procedures)

**Response Protocol:**
- Flag potential fairness issues immediately
- Provide diplomatic warnings for minor violations
- Recommend corrections for bias or inequality
- Document all fairness concerns with specific examples

**Reporting Format:**
- **Fairness Status**: [Overall assessment]
- **Issues Detected**: [Specific concerns with evidence]
- **Recommendations**: [Actionable suggestions for improvement]
- **Monitoring Notes**: [Ongoing observations]

Maintain vigilance while being diplomatic. Focus on creating equal conditions for all participants."""
        
        super().__init__("FairnessMonitor", system_message, model_manager)

class FeedbackProviderAgent(DebateAgent):
    def __init__(self, model_manager: GeminiModelManager):
        system_message = """You are the Feedback Provider giving constructive guidance to help participants improve their debate skills.

**Feedback Categories:**
- **Argument Construction**: Structure, logic flow, evidence integration
- **Presentation Skills**: Communication effectiveness, persuasive techniques
- **Strategic Improvements**: Counter-argument handling, time management, point prioritization
- **Content Development**: Research quality, source credibility, relevance optimization

**Feedback Principles:**
- Be specific and actionable with concrete examples
- Balance criticism with praise and encouragement
- Focus on skill development and growth opportunities
- Provide practical suggestions for improvement

**Format:**
- **Strengths**: [What the participant did well]
- **Growth Areas**: [Specific areas needing improvement]
- **Actionable Recommendations**: [Concrete steps for enhancement]
- **Practice Suggestions**: [Specific exercises or techniques to try]

Maintain a supportive, encouraging tone while providing honest, constructive guidance."""
        
        super().__init__("FeedbackProvider", system_message, model_manager)

class CoordinatorAgent(DebateAgent):
    def __init__(self, model_manager: GeminiModelManager):
        system_message = """You are the Debate Coordinator orchestrating the entire automated debate process.

**Coordination Responsibilities:**
- Initialize and manage debate sessions
- Coordinate agent interactions and timing
- Ensure proper sequence of debate phases
- Compile comprehensive final analysis

**Process Management:**
1. Topic generation and setup
2. Agent preparation and initialization  
3. Round-by-round argument evaluation coordination
4. Continuous monitoring and quality assurance
5. Final compilation and presentation

**Communication Style:**
- Clear, directive, and systematic
- Comprehensive yet concise
- Professional and authoritative
- Ensure all aspects are properly addressed

**Final Deliverables:**
- Structured debate progression summary
- Integrated agent outputs and analysis
- Comprehensive results with winner declaration
- Quality-assured conclusions and recommendations

Maintain oversight while allowing specialized agents to perform their functions effectively."""
        
        super().__init__("Coordinator", system_message, model_manager)

class AutomatedDebateModerator:
    """Main class coordinating the entire debate moderation system"""
    
    def __init__(self, gemini_api_key: str):
        self.model_manager = GeminiModelManager(gemini_api_key)
        
        # Initialize all agents
        self.topic_generator = TopicGeneratorAgent(self.model_manager)
        self.argument_evaluator = ArgumentEvaluatorAgent(self.model_manager)
        self.score_keeper = ScoreKeeperAgent(self.model_manager)
        self.fairness_monitor = FairnessMonitorAgent(self.model_manager)
        self.feedback_provider = FeedbackProviderAgent(self.model_manager)
        self.coordinator = CoordinatorAgent(self.model_manager)
        
        self.agents = {
            "topic_generator": self.topic_generator,
            "argument_evaluator": self.argument_evaluator,
            "score_keeper": self.score_keeper,
            "fairness_monitor": self.fairness_monitor,
            "feedback_provider": self.feedback_provider,
            "coordinator": self.coordinator
        }
    
    async def run_debate(self, topic_request: str = "Should artificial intelligence be regulated by government agencies?"):
        """Run complete automated debate session"""
        print("🎯 AUTOMATED DEBATE MODERATOR SYSTEM (Gemini)")
        print("=" * 60)
        
        try:
            # Reset debate session for new debate
            global debate_session
            debate_session = DebateSession()
            
            # Phase 1: Topic Generation
            await self._phase_1_topic_generation(topic_request)
            
            # Phase 2: Debate Evaluation
            await self._phase_2_debate_evaluation()
            
            # Phase 3: Final Analysis
            await self._phase_3_final_analysis()
            
            return "✅ Debate completed successfully!"
            
        except Exception as e:
            print(f"❌ Debate execution error: {e}")
            import traceback
            traceback.print_exc()
            return "❌ Debate failed"
        
        finally:
            await self.model_manager.close_all()
    
    async def _phase_1_topic_generation(self, topic_request: str):
        """Phase 1: Generate and setup debate topic"""
        print("\n📝 PHASE 1: TOPIC GENERATION AND SETUP")
        print("-" * 40)
        
        # Generate topic
        topic_prompt = f"Generate a comprehensive debate topic based on: '{topic_request}'"
        topic_response = await self.topic_generator.process_message(topic_prompt)
        
        print("✅ Topic Generated:")
        print(topic_response[:200] + "..." if len(topic_response) > 200 else topic_response)
        
        # Update debate session
        debate_session.current_topic = topic_request
        
        # Coordinator setup
        setup_prompt = f"""
        Coordinate the debate setup for topic: '{topic_request}'
        
        Generated topic details: {topic_response}
        
        Confirm all agents are prepared for evaluation:
        - ArgumentEvaluator: Ready for scoring
        - ScoreKeeper: Initialized for tracking
        - FairnessMonitor: Monitoring protocols active
        - FeedbackProvider: Feedback framework prepared
        """
        
        coordinator_response = await self.coordinator.process_message(setup_prompt)
        print(f"\n🔧 Setup Status: {coordinator_response[:100]}...")
    
    async def _phase_2_debate_evaluation(self):
        """Phase 2: Evaluate debate arguments"""
        print("\n🗣️  PHASE 2: DEBATE EVALUATION ROUNDS")
        print("-" * 40)
        
        # Sample debate arguments for demonstration
        debate_arguments = [
            {
                "participant": "participant_a",
                "position": "Pro-Regulation",
                "argument": """I strongly advocate for government regulation of artificial intelligence for several critical reasons. First, AI systems are becoming powerful enough to impact millions of lives through decisions in hiring, lending, healthcare, and criminal justice - areas where bias and errors can cause irreparable harm. Without oversight, we risk perpetuating and amplifying existing societal inequalities.

Second, the rapid pace of AI development has outstripped our ability to understand long-term consequences. Companies are deploying AI systems without adequate testing for safety, fairness, or reliability. Government regulation would establish minimum standards for testing, transparency, and accountability before deployment.

Third, market forces alone are insufficient to ensure AI safety. Companies face competitive pressure to deploy AI quickly, potentially cutting corners on safety measures. Regulation would level the playing field and ensure all companies meet basic safety and ethical standards."""
            },
            {
                "participant": "participant_b",
                "position": "Anti-Regulation",
                "argument": """While I understand concerns about AI safety, government regulation of artificial intelligence would be counterproductive and potentially harmful to innovation and progress. First, AI technology is evolving so rapidly that government regulations would become obsolete before they could be implemented. Bureaucratic processes are too slow to keep pace with technological advancement.

Second, overly broad regulation could stifle innovation and drive AI development overseas to countries with more permissive frameworks. The United States and Europe risk losing their competitive edge in AI if they burden their tech companies with excessive regulatory compliance costs while countries like China pursue more aggressive AI development strategies.

Third, industry self-regulation and market-based solutions are proving more effective and adaptive. Companies have strong incentives to develop safe, reliable AI systems because failures damage their reputation and bottom line."""
            },
            {
                "participant": "participant_a", 
                "position": "Pro-Regulation",
                "argument": """My opponent raises concerns about regulatory speed and innovation, but these arguments actually support smart, adaptive regulation rather than no regulation. We don't avoid regulating automobiles because technology advances quickly - instead, we have adaptive safety standards that evolve with technology.

Regarding international competition, the race-to-the-bottom approach is dangerous. China's less regulated AI development has led to concerning applications like mass surveillance and social credit systems. Strong regulatory frameworks can become competitive advantages - the EU's GDPR became a global standard that gives European companies credibility.

Finally, while market incentives exist for some aspects of AI safety, they fail where harms are diffuse or long-term. Companies may not internalize costs of algorithmic bias, privacy violations, or job displacement. Historical examples show that self-regulation often fails to prevent significant societal harms."""
            },
            {
                "participant": "participant_b",
                "position": "Anti-Regulation", 
                "argument": """The automobile analogy illustrates the problem with premature AI regulation. Early automobile regulations focused on requiring a person to walk in front of cars with a red flag - completely missing the point of automotive innovation. Similarly, current AI regulation proposals often focus on narrow, technical compliance measures that miss the bigger picture.

The GDPR example, while creating standardization, has also imposed significant costs on smaller companies and startups, potentially consolidating market power among large tech giants who can afford compliance infrastructure. This demonstrates how well-intentioned regulation can harm competition and innovation.

Most importantly, AI is not a single technology but a broad category of approaches. Regulating 'AI' is like trying to regulate 'mathematics' or 'software' - it's too broad. Instead, we should focus on regulating specific applications in existing domains like healthcare and finance, where we already have frameworks that can be adapted."""
            }
        ]
        
        # Evaluate each argument
        for i, arg_data in enumerate(debate_arguments):
            round_num = i + 1
            debate_session.rounds = round_num
            
            print(f"\n--- ROUND {round_num}: {arg_data['participant'].title()} ({arg_data['position']}) ---")
            
            # Get argument evaluation
            eval_prompt = f"""
            Evaluate this Round {round_num} argument:
            
            Participant: {arg_data['participant']}
            Position: {arg_data['position']}
            
            Argument:
            {arg_data['argument']}
            
            Provide detailed scoring for all five criteria with specific justifications.
            """
            
            evaluation = await self.argument_evaluator.process_message(eval_prompt)
            print(f"📊 Evaluation: {evaluation[:150]}...")
            
            # Parse scores and record
            metrics = self._parse_evaluation_scores(evaluation)
            debate_session.add_argument(arg_data['participant'], arg_data['argument'], metrics)
            debate_session.add_evaluation(round_num, arg_data['participant'], evaluation)
            
            # Get score keeper update
            score_prompt = f"""
            Record scores for Round {round_num}:
            Participant: {arg_data['participant']}
            Scores: Logic: {metrics.logic_score}, Evidence: {metrics.evidence_score}, 
                   Clarity: {metrics.clarity_score}, Relevance: {metrics.relevance_score}, 
                   Persuasiveness: {metrics.persuasiveness_score}
            Total: {metrics.total_score()}, Weighted: {metrics.weighted_score():.2f}
            
            Provide current standings and analysis.
            """
            
            score_update = await self.score_keeper.process_message(score_prompt)
            print(f"🏆 Scores: {score_update[:100]}...")
            
            # Fairness monitoring
            fairness_prompt = f"""
            Monitor Round {round_num} for fairness:
            - Evaluation bias check
            - Participation equity assessment
            - Any concerns with process or treatment
            
            Report fairness status.
            """
            
            fairness_report = await self.fairness_monitor.process_message(fairness_prompt)
            if "concern" in fairness_report.lower() or "issue" in fairness_report.lower():
                print(f"⚠️  Fairness: {fairness_report[:100]}...")
                debate_session.add_fairness_violation(f"Round {round_num}: {fairness_report[:200]}")
            
            # Provide feedback
            feedback_prompt = f"""
            Provide constructive feedback for {arg_data['participant']} on Round {round_num}:
            
            Argument strengths, areas for improvement, and specific recommendations.
            Focus on skill development and actionable advice.
            """
            
            feedback = await self.feedback_provider.process_message(feedback_prompt)
            debate_session.add_feedback(arg_data['participant'], feedback)
            print(f"💬 Feedback provided for {arg_data['participant']}")
            
            await asyncio.sleep(0.5)  # Brief pause between rounds
    
    async def _phase_3_final_analysis(self):
        """Phase 3: Final analysis and results"""
        print("\n🏆 PHASE 3: FINAL ANALYSIS AND RESULTS")
        print("-" * 40)
        
        # Final coordinator analysis
        status = debate_session.get_status()
        final_prompt = f"""
        Compile final debate analysis:
        
        Topic: {status['topic']}
        Total Rounds: {status['rounds']}
        
        Final Scores:
        - Participant A: {status['scores']['participant_a']:.2f} points
        - Participant B: {status['scores']['participant_b']:.2f} points
        
        Provide:
        - Winner declaration with analysis
        - Key strengths and weaknesses of each participant
        - Overall debate quality assessment
        - Recommendations for future debates
        """
        
        final_analysis = await self.coordinator.process_message(final_prompt)
        print(f"\n📋 Final Analysis:")
        print(final_analysis)
        
        # Display formatted results
        self._display_comprehensive_results()
    
    def _parse_evaluation_scores(self, evaluation_text: str) -> DebateMetrics:
        """Parse evaluation text to extract numerical scores"""
        metrics = DebateMetrics()
        evaluation_lower = evaluation_text.lower()
        
        # Patterns to match scores
        patterns = {
            'logic_score': r'logic.*?(\d+)/10',
            'evidence_score': r'evidence.*?(\d+)/10', 
            'clarity_score': r'clarity.*?(\d+)/10',
            'relevance_score': r'relevance.*?(\d+)/10',
            'persuasiveness_score': r'persuasiveness.*?(\d+)/10'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, evaluation_lower)
            if match:
                score = min(10, max(1, int(match.group(1))))
                setattr(metrics, field, score)
            else:
                # Default reasonable score if not found
                setattr(metrics, field, 7)
        
        return metrics
    
    def _display_comprehensive_results(self):
        """Display formatted comprehensive results"""
        print("\n" + "="*70)
        print("🎯 COMPREHENSIVE DEBATE RESULTS")
        print("="*70)
        
        status = debate_session.get_status()
        
        # Basic info
        print(f"\n📝 **Debate Topic:** {status['topic']}")
        print(f"🔄 **Total Rounds:** {status['rounds']}")
        
        # Final scores
        print(f"\n🏆 **FINAL SCORES:**")
        print("-" * 30)
        for participant, score in status['scores'].items():
            participant_name = participant.replace('_', ' ').title()
            print(f"{participant_name}: {score:.2f} points")
        
        # Winner determination
        if status['scores']['participant_a'] > status['scores']['participant_b']:
            winner = "Participant A"
            margin = status['scores']['participant_a'] - status['scores']['participant_b']
        elif status['scores']['participant_b'] > status['scores']['participant_a']:
            winner = "Participant B"
            margin = status['scores']['participant_b'] - status['scores']['participant_a']
        else:
            winner = "Tie"
            margin = 0
        
        print(f"\n🏅 **WINNER:** {winner}")
        if margin > 0:
            print(f"**Victory Margin:** {margin:.2f} points")
        
        # Score breakdown by category
        print(f"\n📊 **DETAILED PERFORMANCE ANALYSIS:**")
        print("-" * 40)
        
        for participant in ['participant_a', 'participant_b']:
            if status['detailed_scores'][participant]:
                participant_name = participant.replace('_', ' ').title()
                print(f"\n**{participant_name}:**")
                
                scores = status['detailed_scores'][participant]
                categories = {
                    'Logic & Reasoning': [s.logic_score for s in scores],
                    'Evidence & Facts': [s.evidence_score for s in scores], 
                    'Clarity & Presentation': [s.clarity_score for s in scores],
                    'Topic Relevance': [s.relevance_score for s in scores],
                    'Persuasiveness': [s.persuasiveness_score for s in scores]
                }
                
                for category, score_list in categories.items():
                    if score_list:
                        avg = sum(score_list) / len(score_list)
                        print(f"  {category}: {avg:.1f}/10")
        
        # Display feedback summary
        if status['feedback_log']:
            print(f"\n💬 **FEEDBACK SUMMARY:**")
            print("-" * 30)
            for feedback in status['feedback_log']:
                participant_name = feedback['participant'].replace('_', ' ').title()
                print(f"{participant_name} (Round {feedback['round']}): {feedback['feedback'][:100]}...")
        
        # Fairness report
        if status['fairness_violations']:
            print(f"\n⚠️  **FAIRNESS VIOLATIONS:** {len(status['fairness_violations'])}")
            for violation in status['fairness_violations']:
                print(f"  - Round {violation['round']}: {violation['violation']}")
        else:
            print(f"\n✅ **FAIRNESS:** No violations detected")
        
        print("\n" + "="*70)

# Utility classes for enhanced functionality
class DebateAnalytics:
    @staticmethod
    def calculate_performance_trends(debate_session: DebateSession):
        """Calculate performance trends over rounds"""
        trends = {}
        
        for participant in ['participant_a', 'participant_b']:
            if debate_session.arguments[participant]:
                scores_by_round = [arg['weighted_score'] for arg in debate_session.arguments[participant]]
                trends[participant] = {
                    'scores': scores_by_round,
                    'trend': 'improving' if len(scores_by_round) > 1 and scores_by_round[-1] > scores_by_round[0] else 'declining' if len(scores_by_round) > 1 and scores_by_round[-1] < scores_by_round else 'stable',
                    'average': sum(scores_by_round) / len(scores_by_round) if scores_by_round else 0
                }
        
        return trends
    
    @staticmethod
    def generate_improvement_suggestions(participant_scores: List[DebateMetrics]) -> List[str]:
        """Generate specific improvement suggestions based on score patterns"""
        suggestions = []
        
        if not participant_scores:
            return ["Continue practicing debate fundamentals"]
        
        # Calculate average scores by category
        avg_logic = sum(m.logic_score for m in participant_scores) / len(participant_scores)
        avg_evidence = sum(m.evidence_score for m in participant_scores) / len(participant_scores)
        avg_clarity = sum(m.clarity_score for m in participant_scores) / len(participant_scores)
        avg_relevance = sum(m.relevance_score for m in participant_scores) / len(participant_scores)
        avg_persuasiveness = sum(m.persuasiveness_score for m in participant_scores) / len(participant_scores)
        
        # Generate targeted suggestions
        if avg_logic < 7:
            suggestions.append("Focus on improving logical structure and avoiding fallacies")
        if avg_evidence < 7:
            suggestions.append("Strengthen arguments with more credible sources and evidence")
        if avg_clarity < 7:
            suggestions.append("Work on clearer communication and better organization")
        if avg_relevance < 7:
            suggestions.append("Ensure all points directly address the debate topic")
        if avg_persuasiveness < 7:
            suggestions.append("Develop more compelling and emotionally resonant arguments")
        
        if not suggestions:
            suggestions.append("Excellent performance! Continue refining advanced debate techniques")
        
        return suggestions

# Usage functions
async def run_sample_debate():
    """Run a sample debate with Gemini models"""
    # You need to set your Gemini API key
    api_key = os.getenv('GEMINI_API_KEY') or "YOUR_GEMINI_API_KEY_HERE"
    
    if api_key == "YOUR_GEMINI_API_KEY_HERE":
        print("⚠️  Please set your GEMINI_API_KEY environment variable")
        return "Configuration required"
    
    # Initialize debate moderator
    moderator = AutomatedDebateModerator(api_key)
    
    # Sample debate topics
    topics = [
        "Should artificial intelligence be regulated by government agencies?",
        "Is remote work more beneficial than in-office work for productivity?",
        "Should social media platforms be held liable for user-generated content?",
        "Is nuclear energy essential for combating climate change?"
    ]
    
    # Run debate
    print("🚀 Starting Automated Debate with Gemini Models...")
    result = await moderator.run_debate(topics[0])
    
    # Generate additional analytics
    trends = DebateAnalytics.calculate_performance_trends(debate_session)
    print(f"\n📈 **PERFORMANCE TRENDS:**")
    for participant, trend_data in trends.items():
        participant_name = participant.replace('_', ' ').title()
        print(f"{participant_name}: {trend_data['trend'].title()} (Avg: {trend_data['average']:.1f})")
    
    return result

async def run_custom_debate(topic: str):
    """Run a debate with a custom topic"""
    api_key = os.getenv('GEMINI_API_KEY') or "YOUR_GEMINI_API_KEY_HERE"
    
    if api_key == "YOUR_GEMINI_API_KEY_HERE":
        print("⚠️  Please set your GEMINI_API_KEY environment variable")
        return "Configuration required"
    
    moderator = AutomatedDebateModerator(api_key)
    print(f"🚀 Starting Custom Debate: {topic}")
    result = await moderator.run_debate(topic)
    return result

def setup_gemini_environment():
    """Display setup instructions"""
    print("""
    # Setup Instructions for Gemini Automated Debate System
    
    ## 1. Install Required Packages
    pip install autogen-agentchat autogen-ext[openai] 
    
    ## 2. Set Environment Variable
    export GEMINI_API_KEY="your_gemini_api_key_here"
    
    ## 3. Alternative: Use .env file
    Create .env file with:
    GEMINI_API_KEY=your_gemini_api_key_here
    
    ## 4. Run the System
    import asyncio
    result = asyncio.run(run_sample_debate())
    
    ## 5. Run Custom Debate
    result = asyncio.run(run_custom_debate("Your custom debate topic"))
    """)

# Main execution
if __name__ == "__main__":
    print("🎯 Gemini Automated Debate Moderator System")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Gemini API key not found. Please configure your environment.")
        setup_gemini_environment()
    else:
        # Run the system
        try:
            # Example usage - you can choose which function to run
            
            # Option 1: Run sample debate
            #result = asyncio.run(run_sample_debate())
            #print(f"\n✅ Final Result: {result}")
            
            # Option 2: Run custom debate (uncomment to use)
            custom_topic = "Should universal basic income be implemented globally?"
            result = asyncio.run(run_custom_debate(custom_topic))
            print(f"\n✅ Final Result: {result}")
            
        except Exception as e:
            print(f"❌ System error: {e}")
            import traceback
            traceback.print_exc()
