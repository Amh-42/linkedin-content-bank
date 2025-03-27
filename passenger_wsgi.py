import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI application
from app import app as application

# For Passenger WSGI compatibility
application = application 