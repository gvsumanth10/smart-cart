import google.generativeai as genai
from app.core.config import settings
import json

# Configure the Gemini client with API Key
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash"
)

def get_ingredients_from_dish(dish_query: str)-> list:
    """
    Get ingredients from a dish query using Gemini API."""
    
    # List of valid categories in our database

    valid_categories = {
    "main_categories": [
        'Atta, Rice, Oil & Dals',
        'Baby Food',
        'Biscuits',
        'Breakfast & Sauces',
        'Cold Drinks & Juices',
        'Dairy, Bread & Eggs',
        'Frozen Food & Ice Creams',
        'Fruits & Vegetables',
        'Homegrown Brands',
        'Masala & Dry Fruits',
        'Meats, Fish & Eggs',
        'Munchies',
        'Sweet Cravings',
        'Tea, Coffee & More'
    ],
    "sub_categories" : [
        "Powders & Pastes",
        "Fresh Vegetables",
        "Batter & Mixes",
        "Value Added Hydration",
        "Wafers",
        "Breakfast Cereals",
        "Dry Fruits & Nuts Munchies",
        "Muesli & Oats",
        "Glucose & Marie",
        "Ghee",
        "Dehydrated & Dried",
        "Rice & More",
        "Flowers & Leaves",
        "Premium Coffee",
        "Indian Mithai",
        "Chips & Crisps",
        "Combos",
        "Drink Mixes",
        "Dates & Seeds",
        "Tea & Coffee",
        "Organic",
        "Tea",
        "Butter",
        "Digestives",
        "Oil",
        "Cheese",
        "Marinades & Kebabs",
        "Fruit Juices & Drinks",
        "Drinks & Juices",
        "Baking Mixes & Ingredients",
        "Rusk & Khari",
        "Fish & Sea Food",
        "Noodles & Vermicelli",
        "Dessert Mixes",
        "Raw Meats",
        "Cold Cuts",
        "Roti & Paratha",
        "Atta",
        "Batters & Mixes",
        "Coffee",
        "Honey & Spreads",
        "Adult Nutrition",
        "Cookies",
        "Frozen Veggies & Pulp",
        "Premium Chocolates",
        "Ketchup & Sauces",
        "Sausages, Salami & Ham",
        "Millets & Other Flours",
        "Energy Bars",
        "Premium Tea",
        "Ready To Eat",
        "Leafy, Herbs & Seasonings",
        "Egg",
        "Cuts & Sprouts",
        "Dals & Pulses",
        "Crackers",
        "Fresh Fruits",
        "Non-Alcoholic & Energy Drink",
        "Pastries & Cakes",
        "Peanut Butter",
        "Green & Herbal Tea",
        "Yogurt & Shrikhand",
        "Instant Drink Mixes",
        "Momos & More",
        "Papads, Pickles & Chutney",
        "Whole Spices & Seasonings",
        "Paneer & Cream",
        "Instant & Packaged Food",
        "Mutton",
        "Soda & Mixers",
        "Seasonal Picks",
        "Exotics & Premium",
        "Frozen Meat",
        "Nachos",
        "Eggs",
        "Breads & Buns",
        "Ready To Cook",
        "Candies, Gums & Mints",
        "Chocolates",
        "Popcorn",
        "Kids' Nutrition",
        "Creamfills",
        "Milk Drinks",
        "Curd & Probiotic Drink",
        "Veg Snacks",
        "Baby Food",
        "Non Veg Snacks",
        "Besan, Sooji & Maida",
        "Salt, Sugar & Jaggery",
        "Plant Based Meat",
        "Organics & Hydroponics",
        "Soft Drinks",
        "Assorted Snacks",
        "Gourmet Store",
        "Plants & Gardening",
        "Vegan Drinks",
        "Pasta & Soups",
        "Dry Fruits & Nuts",
        "Cold Coffee & Iced Tea",
        "Milk",
        "Canned & Dry Fish, Pickles",
        "Namkeens",
        "Chicken"
    ]}

    # Prompt for the Gemini API to force LLM to return ingredients in a clean JSON object
    prompt = f"""
    Analyze the user's request: "{dish_query}".
    
    Generate a list of essential ingredients. For each ingredient, you MUST choose the most relevant categories from the provided valid lists.
    VALID Main Categories: {valid_categories['main_categories']}
    VALID Sub-Categories: {valid_categories['sub_categories']}

    Identify the dish name and generate a list of essential ingredients required to prepare it.
    Return the response ONLY as a valid JSON object.
    The JSON object must have a single key 'ingredients', which is an array of objects.
    Each object in the array must have two keys: 'ingredient_name' (string), 'quantity' (string, e.g., '250g', '1 large', '2 tsp'), synonyms, main_category_hints and sub_category_hints.
    Do not include instructions, cooking steps, or any other text outside of the JSON object.

    The JSON must have a key 'ingredients', an array of objects.
    Each object must have FIVE keys:
    1. 'ingredient_name' (string): The primary name.
    2. 'quantity' (string): The required quantity.
    3. 'synonyms' (array of strings): Alternative names (e.g., "Vengayam" for "Onion").
    4. 'main_category_hints' (array of strings): A prioritized list of likely main shopping categories.
    5. 'sub_category_hints' (array of strings): A prioritized list of likely sub-categories.
    6. 'search_term' (array of strings): A prioritized list of database search terms. The first term should be the most specific. A concise search term for a database query. For compound items like "Ginger-Garlic Paste", if not commonly sold together, break them down into separate ingredients in the list.

    IMPORTANT: Exclude common household staples like "Water", "Sugar" and "Salt" unless they are a primary, non-obvious component of the dish.

    Example for 'Paneer Butter Masala for 2':
    {{
      "ingredients": [
        {{ 
            "ingredient_name": "Paneer", 
            "quantity": "250g",
            "synonyms": ["Indian Cottage Cheese"],
            "main_category_hints": ["Dairy, Bread & Eggs", "Frozen Food & Ice Creams"],
            "sub_category_hints": ["Paneer & Cream", "Frozen Veggies & Snacks"],
            "search_term_hints": ["\"Paneer\"", "Paneer Cubes"]
        }},
        {{ 
            "ingredient_name": "Butter", 
            "quantity": "3 tbsp",
            "synonyms": [],
            "main_category_hints": ["Dairy, Bread & Eggs"],
            "sub_category_hints": ["Butter"],
            "search_term_hints": ["Butter -peanut", "Salted Butter"]
        }},
        {{ 
            "ingredient_name": "Ginger Paste", 
            "quantity": "1 tbsp",
            "synonyms": [],
            "main_category_hints": ["Masala & Dry Fruits"],
            "sub_category_hints": ["Powders & Pastes", "Whole Spices & Seasonings"],
            "search_term_hints": ["\"Ginger Paste\""]
        }},
        {{ 
            "ingredient_name": "Garlic Paste", 
            "quantity": "1 tbsp",
            "synonyms": [],
            "main_category_hints": ["Masala & Dry Fruits"],
            "sub_category_hints": ["Powders & Pastes", "Whole Spices & Seasonings"],
            "search_term_hints": ["\"Garlic Paste\""]
        }}
      ]

    }}
    """


    


    try:
        response = model.generate_content(prompt)
        # Parse the response to extract the JSON object
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        ingredients_data = json.loads(json_response)
        return ingredients_data.get("ingredients", [])
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while processing the request: {e}")

    
