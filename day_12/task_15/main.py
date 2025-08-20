import asyncio
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List


# Enable verbose logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# AutoGen imports
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_core.tools import FunctionTool


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


# Custom tool: Mock nutrition computation (no external APIs, uses hardcoded data)
async def compute_nutrition(ingredients: List[Dict[str, str]]) -> str:
    """Compute nutritional breakdown for a list of ingredients with quantities."""
    # Hardcoded nutrition data per 100g (calories, protein g, carbs g, fats g)
    nutrition_db = {
        "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
        "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fats": 0.3},
        "broccoli": {"calories": 55, "protein": 3.7, "carbs": 11, "fats": 0.6},
        "beef": {"calories": 250, "protein": 26, "carbs": 0, "fats": 15},
        "salmon": {"calories": 208, "protein": 20, "carbs": 0, "fats": 13},
        "potato": {"calories": 77, "protein": 2, "carbs": 17, "fats": 0.1},
        "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4},
        "bread": {"calories": 265, "protein": 9, "carbs": 49, "fats": 3.2},
        "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fats": 11},
        "milk": {"calories": 42, "protein": 3.4, "carbs": 5, "fats": 1},
        # Add more ingredients as needed
    }
    
    total = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
    report = "Nutritional Breakdown:\n"
    
    for item in ingredients:
        name = item.get("name", "").lower()
        qty_str = item.get("quantity", "0g")
        qty = float(qty_str.replace("g", "")) / 100  # Assume grams, normalize to per 100g
        
        if name in nutrition_db:
            data = nutrition_db[name]
            total["calories"] += data["calories"] * qty
            total["protein"] += data["protein"] * qty
            total["carbs"] += data["carbs"] * qty
            total["fats"] += data["fats"] * qty
            report += f"- {name.capitalize()} ({qty_str}): {data['calories'] * qty:.1f} cal, {data['protein'] * qty:.1f}g protein, {data['carbs'] * qty:.1f}g carbs, {data['fats'] * qty:.1f}g fats\n"
        else:
            report += f"- {name.capitalize()} ({qty_str}): Unknown ingredient (add to DB for calculation)\n"
    
    report += f"\nTotals: {total['calories']:.1f} calories, {total['protein']:.1f}g protein, {total['carbs']:.1f}g carbs, {total['fats']:.1f}g fats"
    return report


# Wrap the function as a FunctionTool
compute_nutrition_tool = FunctionTool(
    compute_nutrition,
    description="Compute nutritional breakdown for a list of ingredients with quantities."
)


async def analyze_meal(meal_description: str, model_client):
    """Analyze a single meal and return the nutritional report."""
    
    # Input Processor Agent
    input_processor = AssistantAgent(
        name="input_processor",
        model_client=model_client,
        system_message=(
            "You are the input processor. Take the provided meal description and structure it into a list of dicts "
            "like [{'name': 'chicken', 'quantity': '200g'}] for analysis. Pass to the next agent. "
            "Do not terminate unless instructed."
        )
    )

    # Nutrition Calculation Agent
    nutrition_agent = AssistantAgent(
        name="nutrition_agent",
        model_client=model_client,
        system_message=(
            "You are a nutrition estimator. Based on the provided meal ingredients, estimate the nutritional breakdown "
            "(calories, proteins, carbs, fats). Output a preliminary report in text format. "
            "Pass to the validation agent for confirmation. If final, say 'TERMINATE'."
        )
    )

    # Validation Agent
    validation_agent = AssistantAgent(
        name="validation_agent",
        model_client=model_client,
        tools=[compute_nutrition_tool],
        system_message=(
            "You are a nutrition validator. Use the compute_nutrition tool to calculate accurate values from the ingredients. "
            "Compare with estimates if provided, and output the final validated report. "
            "If the report is complete and accurate, say 'TERMINATE' to end. Otherwise, pass back for revisions."
        )
    )

    # Termination condition
    termination = TextMentionTermination("TERMINATE")

    # Set up RoundRobinGroupChat
    team = RoundRobinGroupChat(
        [input_processor, nutrition_agent, validation_agent],
        termination_condition=termination
    )

    # Run the analysis
    result = await team.run(task=f"Analyze nutrition for this meal: {meal_description}")

    # Return the final report
    if result.messages:
        return result.messages[-1].content
    else:
        return "No report generated."


async def main():
    """Main function with continuous conversation loop."""
    
    print("=" * 60)
    print("🍽️  MEAL NUTRITION ANALYZER")
    print("=" * 60)
    print("Welcome! I can help you analyze the nutritional content of your meals.")
    print("Type 'exit' or 'quit' at any time to end the session.\n")
    
    # Initialize the model client once
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

    # Main conversation loop
    while True:
        try:
            # Get meal description from user
            print("\n" + "─" * 50)
            meal_description = input("📝 Enter your meal details (e.g., 'grilled chicken 200g, rice 150g, broccoli 100g')\n   or type 'exit'/'quit' to end: ").strip()
            
            # Check for exit condition
            if meal_description.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Thank you for using Meal Nutrition Analyzer! Goodbye!")
                break
            
            # Check for empty input
            if not meal_description:
                print("⚠️  Please enter a meal description or type 'exit' to quit.")
                continue
            
            print("\n🔄 Analyzing your meal... Please wait.")
            print("─" * 50)
            
            # Analyze the meal
            report = await analyze_meal(meal_description, model_client)
            
            # Display the report
            print("\n📊 NUTRITIONAL ANALYSIS COMPLETE")
            print("=" * 50)
            print(report)
            print("=" * 50)
            
            # Ask if user wants to continue
            while True:
                continue_choice = input("\n🤔 Would you like to analyze another meal? (y/yes/n/no/exit/quit): ").strip().lower()
                
                if continue_choice in ['exit', 'quit', 'q']:
                    print("\n👋 Thank you for using Meal Nutrition Analyzer! Goodbye!")
                    return  # Exit the main function
                elif continue_choice in ['n', 'no']:
                    print("\n👋 Thank you for using Meal Nutrition Analyzer! Goodbye!")
                    return  # Exit the main function
                elif continue_choice in ['y', 'yes', '']:
                    break  # Continue to next iteration
                else:
                    print("⚠️  Please enter 'y'/'yes' to continue, 'n'/'no' to exit, or 'exit'/'quit' to end.")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Session interrupted by user.")
            print("👋 Thank you for using Meal Nutrition Analyzer! Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try again or type 'exit' to quit.")


if __name__ == "__main__":
    asyncio.run(main())
