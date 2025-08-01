from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from dotenv import load_dotenv



# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'Jhooti2004*'  
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Mock databases for users
users = {
    "testuser@example.com": {
        "username": "testuser",
        "password": generate_password_hash("7969", method="pbkdf2:sha256"),
    }
}

headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

# Helper functions for interacting with OpenAI
def get_ingredients(dish):
    """
    Fetch ingredients required to prepare a dish using OpenAI.
    """
    prompt = f"List the ingredients required to prepare {dish}."
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a straightforward assisstant that provide answers in the format you are asked."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    response = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=15)
    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        return [line.strip("- ").strip() for line in content.split("\n") if line]
    else:
        raise Exception(f"Failed to fetch ingredients: {response.text}")

# Feedback endpoint
@app.route('/feedback', methods=['POST'])
def handle_feedback():
    """
    Handle user feedback for a recommended dish.
    """
    data = request.json
    user_id = data['user_id']
    recommendation = data['recommendation']
    feedback_reason = data.get('feedback_reason', '')

    # Get the user's profile
    user_profile = profiles.get(user_id)
    if not user_profile:
        return jsonify({"error": "User not found"}), 404

    # Process feedback
    
    if feedback_reason == "Recently Eaten":
        user_profile['recently_eaten'][recommendation] = datetime.now()
    elif feedback_reason == "I just don't like it":
        current_score = user_profile['compatibility_scores'].get(recommendation, 1.0)
        user_profile['compatibility_scores'][recommendation] = max(0, current_score - 0.2)

    # Save the updated profiles to a file (if using persistent storage)
    save_data(profile.json, profiles)  # Replace `PROFILES_FILE` with the actual JSON file name

    return jsonify({"message": "Feedback recorded"}), 200

def filter_recently_eaten(user_profile):
    """
    Filter out dishes that were eaten recently from the user's recommendation pool.
    """
    recent_limit = timedelta(days=3)
    now = datetime.now()

    # Remove dishes that were eaten more than `recent_limit` ago
    user_profile['recently_eaten'] = {
        dish: date for dish, date in user_profile['recently_eaten'].items()
        if now - date <= recent_limit
    }

    # Filter out recently eaten dishes from compatibility scores
    return [
        dish for dish in user_profile['compatibility_scores'].keys()
        if dish not in user_profile['recently_eaten']
    ]




def get_restaurant_suggestion(dish):
    """
    Fetch restaurant suggestions for a dish using OpenAI.
    """
    user_profile = session.get('profile')
    prompt = (
        f"Directly give an unordered list (not a numbered list) of restaurants so give multiple options near UW-Madison which serve {dish}. based on budget prferences  {user_profile['budget']}. don't add any extra information"
        
    )
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that provides restaurant suggestions."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    response = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=15)
    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        return content
    else:
        raise Exception(f"Failed to fetch restaurant details: {response.text}")


# Register endpoint
@app.route("/signup", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if email in users:
        return jsonify({"error": "User already exists"}), 409

    users[email] = {
        "username": username,
        "password": generate_password_hash(password, method="pbkdf2:sha256"),
    }
    return jsonify({"message": "User registered successfully"}), 201


# Login endpoint
@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return jsonify({"message": "Welcome to the NOMination API. Use POST for login."}), 200
    elif request.method == "POST":
        data = request.json
        email = data.get("email")
        password = data.get("password")

        user = users.get(email)
        if user and check_password_hash(user["password"], password):
            session['user'] = email  # Store user email in session
            return jsonify({"message": "Login successful"}), 200
        return jsonify({"error": "Invalid credentials"}), 401


# Profile setup/update endpoint
@app.route("/profilesetup", methods=["POST"])
def create_or_update_profile():
    data = request.json
    session['profile'] = {
        "cuisines": data.get("cuisines", []),
        "dietary_restrictions": data.get("dietaryRestrictions", []),
        "allergies": data.get("allergies", ""),
        "skill_level": data.get("cookingSkill", "beginner"),
        "weight_goal": data.get("healthGoal", "maintaining"),
        "budget": data.get("budget", ""),
    }
    return jsonify({"message": "Profile created/updated successfully"}), 201


# Recommendation endpoint
@app.route("/generatedresponse", methods=["GET"])
def handle_generated_response():
    """
    Generate a recommendation based on the user's profile.
    """
    user_profile = session.get('profile')
    if not user_profile:
        return jsonify({"error": "No profile found"}), 404

    preferences_prompt = (
        f"Based on these preferences: cuisines {user_profile['cuisines']}, "
        f"cooking skill {user_profile['skill_level']}, "
        f"health goal {user_profile['weight_goal']}, "
        f"budget {user_profile['budget']}, "
        f"dietary restrictions {user_profile['dietary_restrictions']}, "
        f"recommend a dish giving only the dish's name and no additional information"
    )

    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that provides meal suggestions."},
                {"role": "user", "content": preferences_prompt},
            ],
            "temperature": 0.7,
        }

        response = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            recommendation = result["choices"][0]["message"]["content"].strip()
            session['last_recommendation'] = recommendation  # Store in session
            return jsonify({"recommendation": recommendation}), 200
        else:
            return jsonify({"error": f"Failed to generate recommendation: {response.text}"}), response.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to OpenAI timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500


# Cooking route
@app.route("/cooking", methods=["POST"])
def cooking():
    """
    Fetch ingredients for the recommended dish.
    """
    recommendation = session.get('last_recommendation')
    if not recommendation:
        return jsonify({"error": "No recommendation found"}), 404

    try:
        ingredients = get_ingredients(recommendation)
        return jsonify({"ingredients": ingredients}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch ingredients: {str(e)}"}), 500

# Take-Out route
@app.route("/takeout", methods=["POST"])
def takeout():
    """
    Fetch nearby restaurant suggestions for the recommended dish.
    """
    recommendation = session.get('last_recommendation')
    if not recommendation:
        return jsonify({"error": "No recommendation found"}), 404

    try:
        restaurant_info = get_restaurant_suggestion(recommendation)
        return jsonify({"restaurants": restaurant_info}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch restaurant suggestions: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5001)
