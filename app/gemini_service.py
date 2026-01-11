from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GENAI_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Load menu data from JSON file
def load_menu_data():
    """
    Load menu data from ucsb_dining_data.json
    In production, this would fetch from MongoDB based on selected dining halls
    """
    # TODO: Replace with MongoDB query when ready
    # For now, load from JSON file for testing
    
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(current_dir)
    # Construct path to testData.json
    json_path = os.path.join(project_root, 'testData.json')
    
    with open(json_path, 'r') as f:
        return json.load(f)
    
    # COMMENTED OUT - Future MongoDB implementation:
    # def load_menu_data(dining_halls):
    #     """Fetch menu data from MongoDB for specific dining halls"""
    #     from .db import db
    #     menu_data = []
    #     for hall in dining_halls:
    #         hall_data = db.menus.find_one({"name": hall})
    #         if hall_data:
    #             menu_data.append(hall_data)
    #     return menu_data

def generate_meal_plan(request_data):
    """
    Generate a personalized meal plan using Gemini AI
    
    Args:
        request_data: Dictionary containing:
            - user_profile: Dict with age, weight, height, activity_level, goal, dietary_restrictions, target_calories
            - meals: List of meal selections with dining_hall and meal_type
            - meal_count: Number of meals
    
    Returns:
        Structured meal plan from Gemini
    """
    user_profile = request_data['user_profile']
    meals = request_data['meals']
    
    # Load menu data
    menu_data = load_menu_data()
    
    # Build comprehensive user context
    user_context = f"""
USER PROFILE:
- Age: {user_profile['age']} years
- Weight: {user_profile['weight']} kg
- Height: {user_profile['height']} cm
- Activity Level: {user_profile['activity_level']}
- Goal: {user_profile['goal']}
- Dietary Restrictions: {', '.join(user_profile['dietary_restrictions']) if user_profile['dietary_restrictions'] else 'None'}
- Target Daily Calories: {user_profile['target_calories']} kcal

MEAL PLAN REQUEST:
The user wants {request_data['meal_count']} meal(s) today:
"""
    
    for meal in meals:
        user_context += f"\n- Meal #{meal['number']}: {meal['meal_type']} at {meal['dining_hall']}"
    
    # Construct the comprehensive prompt
    prompt = f"""
You are an expert nutritionist and meal planning assistant for UCSB students.

{user_context}

AVAILABLE MENU DATA:
{json.dumps(menu_data, indent=2)}

TASK:
Create a personalized meal plan that:
1. Fits within the user's target daily calories ({user_profile['target_calories']} kcal)
2. Distributes calories appropriately across the {request_data['meal_count']} meal(s)
3. Respects all dietary restrictions: {', '.join(user_profile['dietary_restrictions']) if user_profile['dietary_restrictions'] else 'None'}
4. Aligns with the user's goal: {user_profile['goal']}
5. Provides balanced nutrition (adequate protein, healthy fats, complex carbs)

Restrictions Per Dining Hall: 
- If at Ortega, can only select one entree item per meal. 
- If at any other dining hall, can select multiple items to meet nutritional needs.

OUTPUT FORMAT (JSON ONLY - NO MARKDOWN, NO PREAMBLE):
{{
  "meal_plan": [
    {{
      "meal_number": 1,
      "dining_hall": "Dining Hall Name",
      "meal_type": "Breakfast/Lunch/Dinner",
      "recommended_items": [
        {{
          "name": "Item Name",
          "serving_size": "Serving Size",
          "calories": 340,
          "protein": 24,
          "carbs": 47,
          "fat": 12,
          "reason": "Why this item was chosen"
        }}
      ],
      "total_calories": 500,
      "total_protein": 35,
      "total_carbs": 60,
      "total_fat": 15,
      "nutritional_balance": "Brief assessment of this meal's nutrition"
    }}
  ],
  "daily_summary": {{
    "total_calories": 2000,
    "target_calories": {user_profile['target_calories']},
    "calories_remaining": 200,
    "total_protein": 120,
    "total_carbs": 250,
    "total_fat": 65,
    "meets_goals": true,
    "nutritionist_notes": "Overall assessment and tips"
  }},
  "dietary_compliance": {{
    "restrictions_honored": true,
    "notes": "How dietary restrictions were handled"
  }}
}}

IMPORTANT: 
- Return ONLY valid JSON, no markdown formatting or code blocks
- Ensure all recommended items exist in the provided menu data
- Match items to the correct dining hall and meal type
- Consider the user's goal when selecting portion sizes and items
"""

    # Call Gemini API
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        
        # Parse the response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        meal_plan = json.loads(response_text)
        
        return meal_plan
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return structured error
        return {
            "error": "Failed to parse Gemini response",
            "raw_response": response.text,
            "parse_error": str(e)
        }
    except Exception as e:
        return {
            "error": "Gemini API call failed",
            "details": str(e)
        }