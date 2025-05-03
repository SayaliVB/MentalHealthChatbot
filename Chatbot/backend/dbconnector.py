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
# to register a user 
def registeruser(email, password):
    data = {}  # Use a dictionary to store the response data
    # Hash the password before storing
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        # Establish connection and create a cursor
        with psycopg2.connect(**params) as conn:
            # Create a cursor
            cur = conn.cursor()

            # Write query
            query = '''INSERT INTO users (id, email,password_hash) VALUES (%s, %s,%s);'''
            cur.execute('''select max(id) from users;''')
            max_id = cur.fetchone()[0]
            if (max_id != None):
            # Execute the query
                max_id +=1
                cur.execute(query, (max_id, email,hashed_password))
            else:
                cur.execute(query, (1, email,hashed_password))
                
            conn.commit()

            # Set success response data
            '''
            {
            "success": true,
            "message": "User registration successful"
            }

            '''           

            data['success'] = True
            data['message'] = 'User registration successful'
            data['userid'] = max_id

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error in registeruser()")
        print(error)
        data['success'] = False
        data['error'] = 'Error in user registration'
        data['error_details'] = str(error)
        '''
        error response
            {
            "success": false,
            "error": "Error in user registration",
            "error_details": "duplicate key value violates unique constraint"
            }

        '''   
        print("jsonifydata",jsonify(data))
    return jsonify(data)

def completeprofile(userid, firstname, lastname, age, gender, culture, history):
    data = {}  # Use a dictionary to store the response data
    # Hash the password before storing
    try:
        # Establish connection and create a cursor
        with psycopg2.connect(**params) as conn:
            # Create a cursor
            cur = conn.cursor()

            # Write query
            query = '''UPDATE users SET firstname = %s,lastname = %s, age = %s, gender = %s, culture = %s, history = %s
            WHERE id = %s;'''
            cur.execute(query, (firstname,lastname, age, gender, culture, history, userid))
               
            conn.commit()

            # Set success response data
            '''
            {
            "success": true,
            "message": "Profile saved successfully"
            }

            '''           

            data['success'] = True
            data['message'] = 'Profile saved successfully'

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error in completeprofile()")
        print(error)
        data['success'] = False
        data['error'] = 'Error in saving profile'
        data['error_details'] = str(error)
        '''
        error response
            {
            "success": false,
            "error": "Error in saving profile",
            "error_details": "duplicate key value violates unique constraint"
            }

        '''   
        print("jsonifydata",jsonify(data))
    return jsonify(data)

def checkLoginCredentials(email, password):
    """Verifies login credentials using Flask-Bcrypt."""
    try:
        params = connection()
        with psycopg2.connect(**params) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                query = "SELECT id, firstname, email, password_hash, culture FROM users WHERE email = %s"
                cur.execute(query, (email,))
                user = cur.fetchone()

                if user:
                    stored_hash = user['password_hash']
                    if bcrypt.check_password_hash(stored_hash, password):
                        user.pop("password_hash", None)  # Remove sensitive field
                        return jsonify({
                            "success": True,
                            "user": {
                                "id": user["id"],
                                "firstname": user["firstname"],
                                "email": user["email"],
                                "culture": user["culture"]
                            }
                        })
                    else:
                        return jsonify({ "error": "Incorrect password" })
                else:
                    return jsonify({ "error": "No account found with this email" })

    except Exception as error:
        return jsonify({ "error": "Database error", "error_details": str(error) })

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
            cur.execute("INSERT INTO chat_sessions (user_id, session_summary) VALUES (%s, %s) RETURNING id", (userid,summary))
            session_id = cur.fetchone()[0]
            conn.commit()

            return jsonify({"success": "Chat summary stored successfully","session_id": session_id }), 200
            

    except Exception as error:
        print("Error in get session summary:", error)
        return jsonify({"error": "Database error", "error_details": str(error)}), 500
# store crisis response in database
def storeCrisisEvents(user_id, session_id, crisis_list):
    try:
        with psycopg2.connect(**params) as conn:
            cur = conn.cursor()

            for event in crisis_list:
                cur.execute("""
                    INSERT INTO crisis_management (
                        user_id,
                        session_id,
                        crisis_triggered,
                        response_given,
                        therapist_contacted
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, session_id,True,  # Always true if it's added to this list
                    event['response'],
                    event['therapist_contacted']
                ))

            conn.commit()
            print(f"Stored {len(crisis_list)} crisis events for session {session_id}")

    except Exception as e:
        print("❌ Error storing crisis events:", e)
