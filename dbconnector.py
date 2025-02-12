
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
def registeruser(firstname,lastname, email, password):
    data = {}  # Use a dictionary to store the response data
    # Hash the password before storing
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        # Establish connection and create a cursor
        with psycopg2.connect(**params) as conn:
            # Create a cursor
            cur = conn.cursor()

            # Write query
            query = '''INSERT INTO users (id,firstname,lastname, email,password_hash) VALUES (%s,%s, %s, %s,%s);'''
            cur.execute('''select max(id) from users;''')
            max_id = cur.fetchone()[0]
            print(max_id)
            if (max_id != None):
            # Execute the query
                cur.execute(query, (max_id+1,firstname,lastname, email,hashed_password))
            else:
                cur.execute(query, (1,firstname,lastname, email,hashed_password))
                
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
#                     stored_hash = user['password_hash']  # Retrieved hash from DB

#                     print("Stored Hash from DB:", stored_hash)
#                     print("Entered Password:", password)

#                     # ✅ Verify password using Flask-Bcrypt
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