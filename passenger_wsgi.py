import importlib.util
import os
import sys

# Add the application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import Uvicorn to act as a bridge between WSGI and ASGI
import uvicorn

# Create a WSGI application that runs Uvicorn in process
from app import app

def application(environ, start_response):
    # Create a simple WSGI app that returns a message
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b"This application is running with FastAPI. Please access it through the configured domain."]

# When run directly, this runs the FastAPI app with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 