import subprocess
from flask import Flask, jsonify, redirect, session, request, render_template
import json
import requests
from flask_cors import CORS
# Hashing password

app = Flask(__name__)
CORS(app)
global_ip='127.0.0.1:5000'
app.secret_key = 'fwe_5HvBK=9HvoqSD87om'

# Routes for user registration

@app.route("/")
def register_now():
   return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        data_form = request.json  # Use request.json to parse JSON directly
        password = data_form.get("password")
        confirm_password = data_form.get("confirmPassword")

        if password != confirm_password:
            return jsonify({"success": False, "message": "Passwords do not match."})

        response = requests.post(f'http://{global_ip}/signup', json=data_form, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return jsonify({"success": True, "message": "Registration successful! You can now login."})
            else:
                return jsonify({"success": False, "message": data.get("error_details", "Unknown error.")})
        else:
            return jsonify({"success": False, "message": "Failed to connect to backend."})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')  # Render login page

    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request format"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        response_data = requests.post(f'http://{global_ip}/verify_login', json=data, headers={'Content-Type': 'application/json'})
        if response_data.status_code == 200:
            json_data = json.loads(response_data.text)
            session["userid"] = json_data["id"]
            session["useremail"]= email
            session["username"] = json_data["firstname"]
            session.modified = True

        if session.get('username'):
            print(session["username"])


        return response_data.json(), response_data.status_code


# Function to start Streamlit app
def run_streamlit():
    streamlit_script = "faiss_app_culture.py"
    subprocess.Popen(
        ["streamlit", "run", streamlit_script, "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True  # Prevents opening a new tab
    )

# Route to redirect to Streamlit
@app.route('/open-streamlit')
def open_streamlit():
    # Ensure Streamlit is running before redirecting
    run_streamlit()
    print(session.items())
    if session.get('username'):
        print(session["username"])
    user = session.get("username", "Guest")  # Get session variable
    userid = session.get("userid", 0)  # Get session variable
    streamlit_url = f"http://localhost:8501?user={user}&userid={userid}"  # Pass session data
    return render_template("streamlit_embed.html", streamlit_url=streamlit_url)

    # return render_template("streamlit_embed.html")  # Load page with iframe


# @app.route('/register', methods=['POST', 'GET'])
# def register():
#    if request.method == "POST":
#         jsonrequest = json.dumps(request.form)
#         print("jsonreq:",jsonrequest)
#         data_form=json.loads(jsonrequest)
#         password = data_form.get("password")
#         confirm_password = data_form.get("confirmPassword")

#       # Check if password and confirmPassword match
#         if password != confirm_password:
#          error_details = "Password and Confirm Password do not match."
#          return render_template('register.html', message=error_details)
        
#         requests.post(f'http://{global_ip}/signup', data=jsonrequest, headers= {'Content-Type': 'application/json'})
#         print("r.text",r.text)
#         data=json.loads(r.text)
#         print("data in movie anytime",data)        
#         if 'error' in data:            
#             error_details = data['error_details']
#             print("error details printing",error_details)
#             return render_template('registration.html',message=error_details)  
#         else:          
#             return render_template('registration.html',message="Registration Successfull you can login")

# # Login Route
# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == "POST":
#         # Convert form data to JSON
#         jsonrequest = json.dumps(request.form)
#                 # Send request to API for authentication
#         r = requests.post(f'http://{global_ip}/verify_login', data=jsonrequest, headers={'Content-Type': 'application/json'})
#         print("r.text:", r.text)

#         data = json.loads(r.text)
#         print("data in login:", data)

#         if 'error' in data:
#             error_details = data['error']
#             print("Error details:", error_details)
#             return render_template('login.html', message=error_details)  
#         else:
#             return render_template('login.html', message="Login Successful!")

#     return render_template('login.html')  # Show login page on GET request


if __name__ == '__main__':   
   app.run(host='127.0.0.1',port=5001,debug=True)