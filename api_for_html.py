# movieanytime.py
from flask import Flask, jsonify, redirect, session, request, render_template
import json
import requests
from flask_cors import CORS
# Hashing password


app = Flask(__name__)
CORS(app)
global_ip='127.0.0.1:5000'

# Routes for user registration

@app.route("/")
def register_now():
   return render_template('registration.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
   if request.method == "POST":
        jsonrequest = json.dumps(request.form)
        print("jsonreq:",jsonrequest)
        data_form=json.loads(jsonrequest)
        password = data_form.get("password")
        confirm_password = data_form.get("confirmPassword")

      # Check if password and confirmPassword match
        if password != confirm_password:
         error_details = "Password and Confirm Password do not match."
         return render_template('registration.html', message=error_details)
        
        r = requests.post(f'http://{global_ip}/signup', data=jsonrequest, headers= {'Content-Type': 'application/json'})
        print("r.text",r.text)
        data=json.loads(r.text)
        print("data in movie anytime",data)        
        if 'error' in data:            
            error_details = data['error_details']
            print("error details printing",error_details)
            return render_template('registration.html',message=error_details)  
        else:          
            return render_template('registration.html',message="Registration Successfull you can login")
import json
import requests
from flask import Flask, request, render_template


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