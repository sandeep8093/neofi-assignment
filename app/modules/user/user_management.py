import bcrypt
import jwt
from app.model.db import ConnectDB
from dotenv import load_dotenv
import os

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '../../../../.env')
load_dotenv(dotenv_path)

class UserService:

    def __init__(self, email='', password='', user_name=''):
        self.email = email
        self.password = password
        self.user_name = user_name

    def register(self, data):
        try:
            # Established MongoDB connection
            connection = ConnectDB()
            mongodb_connection = connection.connect_db()
            users = mongodb_connection.neofi["users"]

            # Checking if email and password are provided
            if data["email"] and data["password"]:
                # Checkind if the email is already registered
                already_registered = users.find_one({"email": data['email']})
                if already_registered:
                    return {'message': 'Already registered with this email'}
                else:
                    # Hashed the password and insert the user data
                    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
                    data['password'] = hashed_password.decode('utf-8')
                    data['jwt_token'] = ' '
                    users.insert_one(data)
                    return {'status': 'Successfully Registered', 'data': data}
            else:
                return {"message": "Please fill the required fields for the user"}
        except Exception as e:
            return {'error': f'Failed to register user: {str(e)}'}

    def login(self, data):
        try:
            # Established MongoDB connection
            connection = ConnectDB()
            mongodb_connection = connection.connect_db()
            users = mongodb_connection.neofi["users"]
            email = data["email"]
            password = data["password"]
            my_secret = os.getenv("JWT_SECRET_KEY")

            # Finding the user with the provided email
            registered_user = users.find_one({"email": email})
            print(registered_user)
            if registered_user is None:
                return {"message": "Email is not registered"}
            else:
                # Checking if the provided password matches the hashed password in the database
                if bcrypt.checkpw(password.encode('utf-8'), registered_user['password'].encode('utf-8')):
                    payload = {
                        "id": str(registered_user['_id']),
                        "email": registered_user['email'],
                    }

                    # Generated JWT token and update the user's token in the database
                    token = jwt.encode(
                        payload,
                        my_secret, algorithm="HS256"
                    )
                    newvalues = {"$set": {"jwt_token": token}}
                    users.update_one(registered_user, newvalues)
                    print(token)
                    return {"status": "success", "data": payload, "token": token}
                else:
                    return {"message": "Wrong password"}
        except Exception as e:
            return {'error': f'Failed to login: {str(e)}'}
