# main.py
from chatbot_logic import get_bot_response
from flask import Flask, request, jsonify
import dbconnector as dbc
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

load_dotenv()
VITE_GOOGLE_MAPS_API_KEY= os.getenv("VITE_GOOGLE_MAPS_API_KEY")

app = Flask(__name__)

CORS(app)
@app.route('/signup', methods=['POST'])
def register():
    result = request.get_json()
    firstname = result['firstname']
    lastname = result['lastname']
    email = result['email']
    password = result['password']
    response= dbc.registeruser(firstname, lastname, email,password)
    print("response:",response)
    data=response.get_json()
    print("data in main.py",data)
    return data

@app.route("/verify_login", methods=["POST"])
def signin():
    requestdata = request.get_json()
    print("Login request received:", requestdata) 
    username = requestdata["email"]
    password = requestdata["password"]

    responsedata = dbc.checkLoginCredentials(username, password)
    print("Database response:", responsedata)
    responsedata_json = responsedata.get_json()

    if "error" in responsedata_json:
        return responsedata, 400

    
    return jsonify({
        "success": True,
        "user": responsedata_json["user"]
    }), 200



@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("question", "")
        history = data.get("history", "")  

        response = get_bot_response(user_input, history)
        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})




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






if __name__ == '__main__':
    #this is for local use
    app.run(host='127.0.0.1',port=5000)