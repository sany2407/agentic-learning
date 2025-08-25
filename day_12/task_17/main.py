import asyncio
import json
import re
from typing import Dict, List, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


class WorkingCampaignTracker:
    """
    Working Marketing Campaign Tracker - Minimal version that should work
    """
    
    def __init__(self, gemini_api_key: str, model: str = "gemini-1.5-flash"):
        """Initialize with Gemini API key"""
        self.model_client = OpenAIChatCompletionClient(
            model=model,
            api_key=gemini_api_key,
        )
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup campaign processing tools"""
        
        async def analyze_campaign(campaign_text: str) -> str:
            """Analyze a single campaign and extract metrics"""
            try:
                metrics = {}
                
                # Extract numbers using regex
                patterns = {
                    'sent': r'(\d+)\s*sent',
                    'opened': r'(\d+)\s*opened?',
                    'clicked': r'(\d+)\s*clicked?',
                    'views': r'(\d+)\s*views?',
                    'conversions': r'(\d+)\s*conversions?',
                    'shares': r'(\d+)\s*shares?',
                    'spend': r'\$(\d+(?:\.\d{2})?)'
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, campaign_text, re.IGNORECASE)
                    if match:
                        value = float(match.group(1)) if key == 'spend' else int(match.group(1))
                        metrics[key] = value
                
                # Determine channel
                text_lower = campaign_text.lower()
                if "email" in text_lower:
                    channel = "Email"
                elif any(word in text_lower for word in ["instagram", "facebook", "linkedin", "twitter"]):
                    channel = "Social Media"
                elif "blog" in text_lower or "content" in text_lower:
                    channel = "Content Marketing"
                else:
                    channel = "Other"
                
                # Calculate KPIs
                kpis = {}
                
                # CTR
                if 'clicked' in metrics and 'sent' in metrics and metrics['sent'] > 0:
                    kpis['CTR'] = round((metrics['clicked'] / metrics['sent']) * 100, 2)
                elif 'clicked' in metrics and 'views' in metrics and metrics['views'] > 0:
                    kpis['CTR'] = round((metrics['clicked'] / metrics['views']) * 100, 2)
                
                # Open Rate
                if 'opened' in metrics and 'sent' in metrics and metrics['sent'] > 0:
                    kpis['Open Rate'] = round((metrics['opened'] / metrics['sent']) * 100, 2)
                
                # Conversion Rate
                total_traffic = metrics.get('clicked', metrics.get('views', 0))
                if 'conversions' in metrics and total_traffic > 0:
                    kpis['Conversion Rate'] = round((metrics['conversions'] / total_traffic) * 100, 2)
                
                # ROI (assuming $25 per conversion)
                if 'spend' in metrics and 'conversions' in metrics and metrics['spend'] > 0:
                    revenue = metrics['conversions'] * 25
                    roi = ((revenue - metrics['spend']) / metrics['spend']) * 100
                    kpis['ROI'] = round(roi, 2)
                
                # Cost per conversion
                if 'spend' in metrics and 'conversions' in metrics and metrics['conversions'] > 0:
                    kpis['Cost per Conversion'] = round(metrics['spend'] / metrics['conversions'], 2)
                
                result = {
                    "campaign": campaign_text,
                    "channel": channel,
                    "metrics": metrics,
                    "kpis": kpis
                }
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                return f"Error analyzing campaign: {str(e)}"
        
        self.campaign_tool = analyze_campaign
    
    async def analyze_campaigns_simple(self, campaigns: List[str]) -> Dict[str, Any]:
        """Simple analysis using a single agent"""
        
        # Create analyzer agent
        analyzer = AssistantAgent(
            name="CampaignAnalyzer",
            model_client=self.model_client,
            tools=[self.campaign_tool],
            system_message="""
            You are a Marketing Campaign Analyzer. For each campaign provided:
            
            1. Use the analyze_campaign tool to extract metrics and calculate KPIs
            2. Identify the marketing channel (Email, Social Media, Content Marketing, etc.)
            3. Calculate performance metrics like CTR, conversion rates, ROI
            4. Provide insights on campaign performance
            5. Make recommendations for optimization
            
            Always use the tool first, then provide a summary analysis of all campaigns.
            Focus on actionable insights and comparative performance across channels.
            """,
            reflect_on_tool_use=True
        )
        
        # Format the task
        task = "Please analyze these marketing campaigns step by step:\n\n"
        task += "\n".join([f"{i+1}. {campaign}" for i, campaign in enumerate(campaigns)])
        task += "\n\nFor each campaign, use the analyze_campaign tool, then provide a comprehensive summary with insights and recommendations."
        
        try:
            # Run the analysis
            result = await analyzer.run(task=task)
            
            # Extract and structure the results
            return self._extract_analysis_results(result, campaigns)
            
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def analyze_with_streaming(self, campaigns: List[str]):
        """Analyze campaigns with streaming console output"""
        
        analyzer = AssistantAgent(
            name="CampaignAnalyzer",
            model_client=self.model_client,
            tools=[self.campaign_tool],
            system_message="""
            You are a Marketing Campaign Analyzer. Analyze each campaign thoroughly:
            
            1. Extract all metrics (sent, opened, clicked, views, conversions, spend)
            2. Calculate KPIs (CTR, conversion rates, ROI, cost per conversion)
            3. Identify the best and worst performing campaigns
            4. Provide optimization recommendations
            
            Be detailed in your analysis and provide actionable insights.
            """,
            reflect_on_tool_use=True
        )
        
        task = "Analyze these marketing campaigns in detail:\n\n"
        task += "\n".join([f"• {campaign}" for campaign in campaigns])
        task += "\n\nUse the analyze_campaign tool for each one and provide comprehensive insights."
        
        # Stream the analysis
        await Console(analyzer.run_stream(task=task))
    
    def _extract_analysis_results(self, result, original_campaigns) -> Dict[str, Any]:
        """Extract structured results from the analysis"""
        
        analysis = {
            "status": "completed",
            "total_campaigns": len(original_campaigns),
            "campaigns": [],
            "summary": "",
            "top_performer": None,
            "recommendations": []
        }
        
        # Try to extract JSON data from the result
        result_text = str(result)
        
        # Find JSON objects in the response
        json_objects = []
        lines = result_text.split('\n')
        current_json = ""
        in_json = False
        
        for line in lines:
            if '{' in line and '"campaign"' in line:
                in_json = True
                current_json = line
            elif in_json:
                current_json += "\n" + line
                if '}' in line and current_json.count('{') == current_json.count('}'):
                    try:
                        json_obj = json.loads(current_json.strip())
                        json_objects.append(json_obj)
                        in_json = False
                        current_json = ""
                    except:
                        pass
        
        analysis["campaigns"] = json_objects
        
        # Find best performer by ROI
        best_roi = -float('inf')
        for camp in json_objects:
            kpis = camp.get('kpis', {})
            roi = kpis.get('ROI', -float('inf'))
            if roi > best_roi:
                best_roi = roi
                analysis["top_performer"] = {
                    "channel": camp.get('channel'),
                    "roi": roi
                }
        
        # Extract recommendations from the text
        rec_indicators = ['recommend', 'should', 'improve', 'optimize', 'consider']
        for line in result_text.split('\n'):
            if any(indicator in line.lower() for indicator in rec_indicators):
                clean_line = line.strip()
                if len(clean_line) > 20:
                    analysis["recommendations"].append(clean_line)
        
        return analysis
    
    def format_results(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis results for display"""
        
        if analysis.get("status") == "failed":
            return f"❌ Analysis failed: {analysis.get('error')}"
        
        output = []
        output.append("📊 MARKETING CAMPAIGN ANALYSIS REPORT")
        output.append("=" * 55)
        
        output.append(f"\n📈 Total Campaigns Analyzed: {analysis['total_campaigns']}")
        
        # Campaign details
        if analysis.get("campaigns"):
            output.append("\n🔍 CAMPAIGN BREAKDOWN:")
            
            for i, campaign in enumerate(analysis["campaigns"], 1):
                output.append(f"\n  Campaign {i}: {campaign.get('channel', 'Unknown')} Channel")
                
                # Show metrics
                metrics = campaign.get('metrics', {})
                if metrics:
                    output.append("    📊 Raw Metrics:")
                    for key, value in metrics.items():
                        if key == 'spend':
                            output.append(f"      {key.capitalize()}: ${value}")
                        else:
                            output.append(f"      {key.capitalize()}: {value:,}")
                
                # Show KPIs
                kpis = campaign.get('kpis', {})
                if kpis:
                    output.append("    🎯 Key Performance Indicators:")
                    for key, value in kpis.items():
                        if key in ['CTR', 'Open Rate', 'Conversion Rate', 'ROI']:
                            output.append(f"      {key}: {value}%")
                        else:
                            output.append(f"      {key}: ${value}")
        
        # Top performer
        if analysis.get("top_performer"):
            top = analysis["top_performer"]
            output.append(f"\n🏆 TOP PERFORMER:")
            output.append(f"    Channel: {top['channel']}")
            output.append(f"    ROI: {top['roi']}%")
        
        # Recommendations
        if analysis.get("recommendations"):
            output.append(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
            for rec in analysis["recommendations"][:5]:  # Show top 5
                output.append(f"  • {rec}")
        
        return "\n".join(output)
    
    async def close(self):
        """Close connections"""
        await self.model_client.close()



# Demo Application
class CampaignDemo:
    def __init__(self, api_key: str):
        self.tracker = WorkingCampaignTracker(api_key)
    
    async def run_sample_analysis(self):
        """Run analysis with sample campaigns"""
        
        sample_campaigns = [
            "Email campaign: 2000 sent, 400 opened, 60 clicked, 8 conversions",
            "Instagram ad: 1500 views, 90 clicked, $120 spent, 12 conversions", 
            "Facebook ad: 3000 views, 150 clicked, $200 spent, 18 conversions",
            "Blog post: 5000 views, 200 shares, 80 clicked, 5 conversions",
            "LinkedIn sponsored post: 800 views, 55 clicked, $95 spent, 7 conversions"
        ]
        
        print("🚀 MARKETING CAMPAIGN ANALYSIS")
        print("=" * 50)
        
        print("📝 Sample Campaigns:")
        for i, campaign in enumerate(sample_campaigns, 1):
            print(f"  {i}. {campaign}")
        
        print("\n⏳ Running analysis...")
        
        try:
            # Method 1: Get structured results
            results = await self.tracker.analyze_campaigns_simple(sample_campaigns)
            print("\n" + self.tracker.format_results(results))
            
            print("\n" + "="*50)
            print("🔄 STREAMING ANALYSIS:")
            print("="*50)
            
            # Method 2: Stream analysis to console
            await self.tracker.analyze_with_streaming(sample_campaigns)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.tracker.close()
    
    async def run_custom_analysis(self, campaigns: List[str]):
        """Run analysis with custom campaigns"""
        try:
            print(f"⏳ Analyzing {len(campaigns)} campaigns...")
            results = await self.tracker.analyze_campaigns_simple(campaigns)
            print("\n" + self.tracker.format_results(results))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.tracker.close()



async def main():
    """Main function"""
    
    # Set your gemini API key here
    API_KEY = "your-api-key"  # Replace with actual key
    
    print("🎯 WORKING MARKETING CAMPAIGN TRACKER")
    print("=" * 50)
    print("Simplified version using single agent with tools")
    print()
    
    demo = CampaignDemo(API_KEY)
    
    print("Choose an option:")
    print("1. Run sample campaign analysis")
    print("2. Enter custom campaigns")
    print("3. Exit")
    
    choice = input("\nYour choice (1-3): ").strip()
    
    if choice == "1":
        await demo.run_sample_analysis()
    
    elif choice == "2":
        print("\nEnter campaign details (type 'done' when finished):")
        campaigns = []
        
        while True:
            campaign = input("Campaign: ").strip()
            if campaign.lower() == 'done':
                break
            if campaign:
                campaigns.append(campaign)
        
        if campaigns:
            await demo.run_custom_analysis(campaigns)
        else:
            print("❌ No campaigns entered!")
    
    elif choice == "3":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice!")



if __name__ == "__main__":
    asyncio.run(main())



# Installation:
# pip install -U "autogen-agentchat" "autogen-ext[googleai]"


# Usage Examples:
"""
Valid campaign formats:
• "Email newsletter: 5000 sent, 1200 opened, 89 clicked, 12 conversions"
• "Google Ads: 10000 views, 234 clicked, $500 spent, 15 conversions"  
• "Instagram story: 2500 views, 125 clicked, $75 spent, 8 conversions"
• "Blog article: 800 views, 45 shares, 23 clicked, 2 conversions"
• "Facebook video ad: 3000 views, 180 clicked, $200 spent, 18 conversions"
"""
