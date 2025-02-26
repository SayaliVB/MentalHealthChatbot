from flask import Flask, request
import dbconnector as dbc
from flask_cors import CORS
from flask import Flask, jsonify

app = Flask(__name__)
CORS(app)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        result = request.get_json()
        firstname = result.get('firstname')
        lastname = result.get('lastname')
        email = result.get('email')
        password = result.get('password')

        if not firstname or not lastname or not email or not password:
            return jsonify({"success": False, "message": "All fields are required."}), 400

        response = dbc.registeruser(firstname, lastname, email, password)

        return response
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred.", "error": str(e)}), 500

@app.route('/verify_login', methods=['POST'])
def signin():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request format"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check credentials using database function
    response_data = dbc.checkLoginCredentials(email, password)
    if response_data[1] == 200:
        data = response_data[0].get_json()
        print(type(data))
        print(data)

    # firstname

    return response_data  # Return JSON response directly

# @app.route('/signup', methods=['POST'])
# def register():
#     result = request.get_json()
#     firstname = result['firstname']
#     lastname = result['lastname']
#     email = result['email']
#     password = result['password']
#     response= dbc.registeruser(firstname, lastname, email,password)
#     print("response:",response)
#     data=response.get_json()
#     print("data in main.py",data)
#     return data

# @app.route("/verify_login",methods=["POST"])
# def signin():
#     '''
#     headers = request.headers
#     bearer = headers.get('Authorization')    # Bearer YourTokenHere
#     if(bearer is None):
#         return "No authorisation token", 401
    
#     token = bearer.split()[1]  # YourTokenHere

#     if token != "xyz-secret-key":
#         return "Unauthorised user", 401
#     '''
#     requestdata = request.get_json()

#     username = requestdata["email"]
#     password = requestdata["password"]

#     #use database connector object to connect to database and retrieve data
#     responsedata = dbc.checkLoginCredentials(username, password)
#     #print(responsedata)
#     responsedata_json = responsedata.get_json()  # Extract JSON data from Response

#     if "error" in responsedata_json:
#         return responsedata, 400
#     return responsedata, 200

if __name__ == '__main__':
    #this is for local use
    app.run(host='127.0.0.1',port=5000)