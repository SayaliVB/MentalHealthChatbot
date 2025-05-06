from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import dbconnector as dbc
from chatbot_logic import create_chat_summary, crisis_tool_response, get_bot_response  # <-- your main bot logic
import os
app = Flask(__name__)
CORS(app)

# === Signup Route ===
@app.route('/signup', methods=['POST'])
def register():
    try:
        result = request.get_json()
        email = result.get('email')
        password = result.get('password')
        

        if not email or not password:
            return jsonify({"success": False, "message": "All fields are required."}), 400

        response = dbc.registeruser(email, password)
        return response

    except Exception as e:
        return jsonify({"success": False, "message": "Signup failed", "error": str(e)}), 500

# === Profile Route ===
@app.route('/profile', methods=['POST'])
def profile():
    try:
        result = request.get_json()
        userid = result.get('userid')
        firstname = result.get('firstname')
        lastname = result.get('lastname')
        age = result.get('age')
        gender = result.get('gender')
        culture = result.get('culture')
        history = result.get('history')

        if not userid:
            return jsonify({"success": False, "message": "Userid not found"}), 404

        if not firstname or not lastname or not gender or not age:
            return jsonify({"success": False, "message": "All fields are required."}), 400

        response = dbc.completeprofile(userid, firstname, lastname, age, gender, culture, history)
        return response

    except Exception as e:
        return jsonify({"success": False, "message": "Profile update failed", "error": str(e)}), 500



# === Login Route ===
@app.route("/verify_login", methods=["POST"])
def signin():
    try:
        requestdata = request.get_json()
        email = requestdata.get("email")
        password = requestdata.get("password")

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        # response = dbc.checkLoginCredentials(email, password)
        # response_json = response[0].get_json()
        # if response[1] != 200:
        #     return jsonify(response_json), response[1]

        # return jsonify({
        #     "success": True,
        #     "user": response_json
        # }), 200
        response = dbc.checkLoginCredentials(email, password)
        response_json = response.get_json()

        # Error format check
        if "error" in response_json:
            return jsonify(response_json), 401

        # Success
        return jsonify({
            "success": True,
            "user": response_json.get("user")
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Login failed", "error": str(e)}), 500
    
@app.route('/get_chat_summary', methods=['POST'])
def get_chat_summary():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request format"}), 400

    userid = data.get("user_id")

    if not userid:
        return jsonify({"error": "User information required"}), 400

    # Check credentials using database function
    response_data = dbc.getChatSummary(userid)
    if response_data[1] == 200:
        data = response_data[0].get_json()

    # firstname

    return response_data  # Return JSON response directly

@app.route('/store_chat_summary', methods=['POST'])
def store_chat_summary():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request format"}), 400

    userid = data.get("userid", None)
    print("In session summary route")
    print("userid", userid)
    chat_history = data.get("chatHistory", None)
    session_summary = create_chat_summary(chat_history)
    print("Session summary:", session_summary)
    crisis_events = data.get("crisisEvents", [])
    print("Crisis Events:", crisis_events)

    if not userid or not session_summary:
        return jsonify({"error": "User information and session summary required"}), 400

    # Check credentials using database function
    response_data = dbc.storeChatSummary(userid, session_summary)
    if response_data[1] == 200:
        # data = response_data[0].get_json()
        response_json = response_data[0].get_json()
        session_id = response_json.get("session_id")

        print("✅ Session ID fetched:", session_id)
        if crisis_events and session_id:
            dbc.storeCrisisEvents(userid, session_id, crisis_events)

    # firstname

    return response_data  # Return JSON response directly


@app.route("/api/nearby-doctors")
def get_nearby_doctors():
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    api_key = os.getenv("VITE_GOOGLE_MAPS_API_KEY")
    print("Backend loaded API key:", api_key)

    if not api_key:
        return jsonify({"error": "Missing Google API Key"}), 500

    url = (
    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    f"location={lat},{lng}&radius=8000&type=health&keyword=hospital|doctor|clinic&key={api_key}"
)

    print("Requesting:", url)

    try:
        res = requests.get(url)
        print("Places API Response:", res.json())
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Chat Route ===
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("question", "").strip()
        history = data.get("history", "")
        user_name = data.get("userName", "User")
        culture = data.get("culture", "Unknown")
        lat = data.get("lat")
        lng = data.get("lng")
        user_id = data.get("user_id")
        print("inside api_for_db User ID:", user_id)

        if not user_input:
            return jsonify({"success": False, "message": "Question is required."}), 400

        if user_input.lower() == "find nearest therapists" and lat and lng:
            from tools.nearest_therapist_tool import NearestTherapistLocatorTool
            tool = NearestTherapistLocatorTool()
            location_str = f"{lat},{lng}"
            tool_output = tool.run(location_str)

            return jsonify({
                "success": True,
                "response": tool_output,
                "isCrisis": False
            })

        # Fallback: Use full agent-based chatbot logic
        response = get_bot_response(user_input, history, user_name, culture, user_id)
        is_crisis_triggered = (response == crisis_tool_response())

        return jsonify({
            "success": True,
            "response": response,
            "isCrisis": is_crisis_triggered
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Chat failed",
            "error": str(e)
        }), 500

# === Optional: Health Check ===
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
