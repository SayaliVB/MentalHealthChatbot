
from connection import connection
import psycopg2
import psycopg2.extras
from flask import jsonify
from flask_bcrypt import Bcrypt
  
conn = None
# Initialize Flask-Bcrypt (even without Flask app, we can use it like this)
bcrypt = Bcrypt()
# read connection parameters
params = connection()

def registeruser(firstname, lastname, email, password):
    data = {}

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        with psycopg2.connect(**params) as conn:
            cur = conn.cursor()

            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
            existing_user = cur.fetchone()
            if existing_user:
                return jsonify({"success": False, "message": "Email already registered."})

            # Insert new user
            cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM users;")
            new_id = cur.fetchone()[0]

            query = "INSERT INTO users (id, firstname, lastname, email, password_hash) VALUES (%s, %s, %s, %s, %s);"
            cur.execute(query, (new_id, firstname, lastname, email, hashed_password))

            conn.commit()

            data['success'] = True
            data['message'] = 'User registration successful'

    except Exception as error:
        print("Error in registeruser:", error)
        data['success'] = False
        data['message'] = "Error in user registration"
        data['error'] = str(error)

    return jsonify(data)

def checkLoginCredentials(email, password):
    """Verifies login credentials using Flask-Bcrypt."""
    conn = None
    try:
        params = connection()
        with psycopg2.connect(**params) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                query = "SELECT password_hash, id, firstname FROM users WHERE email = %s"
                cur.execute(query, (email,))
                user = cur.fetchone()

                if user:
                    stored_hash = user['password_hash']
                    id = user['id']
                    firstname = user["firstname"]
                    if bcrypt.check_password_hash(stored_hash, password):
                        return jsonify({"success": "Login successful", "id": id, "firstname": firstname }), 200
                    else:
                        return jsonify({"error": "Incorrect password"}), 401
                else:
                    return jsonify({"error": "No account found with this email"}), 404

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"error": "Database error", "error_details": str(error)}), 500

    finally:
        if conn:
            conn.close()


def getChatSummary(userid):
    try:
        with psycopg2.connect(**params) as conn:
            cur = conn.cursor()

            # Check if email already exists
            cur.execute("SELECT session_summary FROM chat_sessions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1", (userid,))
            summary = cur.fetchone()
            if summary:
                return jsonify({"success": "Chat summary found", "session_summary": summary[0] }), 200
            else:
                return jsonify({"error": "No previous chat summary"}), 404

    except Exception as error:
        print("Error in get session summary:", error)
        return jsonify({"error": "Database error", "error_details": str(error)}), 500

def storeChatSummary(userid, summary):
    try:
        with psycopg2.connect(**params) as conn:
            cur = conn.cursor()

            # Check if email already exists
            cur.execute("INSERT INTO chat_sessions (user_id, session_summary) VALUES (%s, %s)", (userid,summary))
            conn.commit()

            return jsonify({"success": "Chat summary stored successfully" }), 200
            

    except Exception as error:
        print("Error in get session summary:", error)
        return jsonify({"error": "Database error", "error_details": str(error)}), 500

# to register a user 
# def registeruser(firstname,lastname, email, password):
#     data = {}  # Use a dictionary to store the response data
#     # Hash the password before storing
#     hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#     try:
#         # Establish connection and create a cursor
#         with psycopg2.connect(**params) as conn:
#             # Create a cursor
#             cur = conn.cursor()

#             # Write query
#             query = '''INSERT INTO users (id,firstname,lastname, email,password_hash) VALUES (%s,%s, %s, %s,%s);'''
#             cur.execute('''select max(id) from users;''')
#             max_id = cur.fetchone()[0]
#             print(max_id)
#             if (max_id != None):
#             # Execute the query
#                 cur.execute(query, (max_id+1,firstname,lastname, email,hashed_password))
#             else:
#                 cur.execute(query, (1,firstname,lastname, email,hashed_password))
                
#             conn.commit()

#             # Set success response data
#             '''
#             {
#             "success": true,
#             "message": "User registration successful"
#             }

#             '''           

#             data['success'] = True
#             data['message'] = 'User registration successful'

#     except (Exception, psycopg2.DatabaseError) as error:
#         print("Error in registeruser()")
#         print(error)
#         data['success'] = False
#         data['error'] = 'Error in user registration'
#         data['error_details'] = str(error)
#         '''
#         error response
#             {
#             "success": false,
#             "error": "Error in user registration",
#             "error_details": "duplicate key value violates unique constraint"
#             }

#         '''   
#         print("jsonifydata",jsonify(data))
#     return jsonify(data)

# #checks username and password for login; returns username and membership details
# def checkLoginCredentials(email, password):
#     """Verifies login credentials using Flask-Bcrypt."""
    
#     conn = None
#     try:
#         # Establish database connection
#         params = connection()
#         with psycopg2.connect(**params) as conn:
#             with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

#                 # Fetch stored hash for the given email
#                 query = "SELECT password_hash FROM users WHERE email = %s"
#                 cur.execute(query, (email,))
#                 user = cur.fetchone()

#                 if user:
#                     stored_hash = user['password_hash']  
#                     print("Stored Hash from DB:", stored_hash)
#                     print("Entered Password:", password)

#                     # Verify password using Flask-Bcrypt
#                     if bcrypt.check_password_hash(stored_hash, password):
#                         print("succesfull pasword match")
#                         return jsonify({"success": "Login successful"})
#                     else:
#                         print("succesfull notpasword match")
#                         return jsonify({"error": "Incorrect password"})

#                 else:
#                     return jsonify({"error": "No account found with this email"})

#     except (Exception, psycopg2.DatabaseError) as error:
#         return jsonify({"error": "Database error", "error_details": str(error)})

#     finally:
#         if conn:
#             conn.close()