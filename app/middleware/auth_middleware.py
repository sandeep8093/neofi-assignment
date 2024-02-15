from functools import wraps
import jwt
from flask import request
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '../../../.env')
load_dotenv(dotenv_path)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract token from the Authorization header
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        # Return 401 if token is missing
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401

        try:
            # Verify and decode the token
            data = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms="HS256")
            current_user = data
            # Check if the decoded user is None 
            if current_user is None :
                return {
                    "message": "Invalid or logged out Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401

        except jwt.ExpiredSignatureError:
            return {
                "message": "Token has expired",
                "data": None,
                "error": "Unauthorized"
            }, 401

        except jwt.InvalidTokenError as e:
            return {
                "message": "Invalid Authentication token",
                "data": None,
                "error": str(e)
            }, 401

        except Exception as e:
            print(e)
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        # Call the decorated function with the current_user
        return f(current_user, *args, **kwargs)

    return decorated
