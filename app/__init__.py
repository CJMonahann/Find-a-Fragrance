from flask import Flask

app = Flask(__name__)

# Add models
from app import routes