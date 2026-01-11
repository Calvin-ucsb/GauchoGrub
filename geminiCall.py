from google import genai
import json

# ---------------------------------------------------------
# 1. SETUP
# Replace 'TopSecretAPIKey' with your actual key from AI Studio
# ---------------------------------------------------------
client = genai.Client(api_key="AIzaSyDPG8G6gUJSZ5J1qewGsBtm85bAplBA3CE")

# ---------------------------------------------------------
# 2. THE CONTEXT (Your Menu Data)
# We define this as a standard Python dictionary/list, 
# and we will convert it to a string later for Gemini.
# ---------------------------------------------------------
menu_data = [
  {
    "name": "Takeout at Ortega Commons",
    "unit_id": 1,
    "meals": [
      {
        "name": "Ortega's Daily Menu",
        "meal_id": None,
        "items": [
          {
            "name": "Korean Chicken & Rice",
            "serving_size": "Plate (389g)",
            "calories": 340.0,
            "protein": 24.0,
            "total_carbohydrates": 47.0,
            "total_fat": 12.0
          },
          {
            "name": "Bacon Breakfast Burrito",
            "serving_size": "Burrito (420g)",
            "calories": 1100.0,
            "protein": 43.0,
            "total_carbohydrates": 78.0,
            "total_fat": 67.0
          },
          {
            "name": "Creamy Pesto Pasta with Chicken",
            "serving_size": "12 OZ (342g)",
            "calories": 610.0,
            "protein": 31.0,
            "total_carbohydrates": 72.0,
            "total_fat": 27.0
          },
          {
            "name": "Macaroni & Cheese (v)",
            "serving_size": "16 OZ (482g)",
            "calories": 1040.0,
            "protein": 46.0,
            "total_carbohydrates": 109.0,
            "total_fat": 45.0
          },
          {
            "name": "Chicken Caesar Salad",
            "serving_size": "Salad (283g)",
            "calories": 570.0,
            "protein": 45.0,
            "total_carbohydrates": 21.0,
            "total_fat": 38.0
          }
        ]
      }
    ]
  }
]
# ---------------------------------------------------------
# 3. THE USER INPUT
# This simulates what a user might type into your app.
# ---------------------------------------------------------
user_input = "I'm looking for a high protein dinner, but I want to keep it under 600 calories."


# ---------------------------------------------------------
# 4. CONSTRUCT THE PROMPT
# We combine instructions, the data (as a string), and the user request.
# ---------------------------------------------------------
prompt = f"""
You are an intelligent nutrition assistant. 
Analyze the provided MENU JSON data and suggest the best meal option based on the USER REQUEST.

MENU DATA:
{json.dumps(menu_data)}

USER REQUEST:
{user_input}

Output Format:
1. Recommended Meal Name
2. Why it fits the criteria (mention specific stats)
"""

# ---------------------------------------------------------
# 5. CALL THE API
# We use 'gemini-1.5-flash' as it is fast and free-tier friendly.
# ---------------------------------------------------------
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    
    print("--- Gemini's Recommendation ---")
    print(response.text)

except Exception as e:
    print(f"Error calling API: {e}")