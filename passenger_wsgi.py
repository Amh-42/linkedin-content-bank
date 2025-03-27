import os
import sys
import logging

# Configure logging to debug deployment issues
logging.basicConfig(
    filename='app_error.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the FastAPI application
    from app import app
    
    # Create WSGI app using Uvicorn's ASGI to WSGI adapter
    from uvicorn.middleware.wsgi import WSGIMiddleware
    application = WSGIMiddleware(app)
    
except Exception as e:
    logging.error(f"Error starting application: {e}", exc_info=True)
    # Create a simple WSGI application that shows the error
    def application(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        error_msg = f"Application failed to start: {str(e)}"
        return [error_msg.encode()] 