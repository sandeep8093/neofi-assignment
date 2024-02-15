from flask import Flask
from flask_cors import CORS, cross_origin
from itsdangerous import URLSafeTimedSerializer


app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
app.secret_key = "secretkey"
app.debug = True
login_serializer = URLSafeTimedSerializer(app.secret_key)

from app.routes import routes