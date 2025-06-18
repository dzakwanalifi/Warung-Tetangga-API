# function_app.py

import azure.functions as func
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add the app directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Import FastAPI app
try:
    from app.main import app as fastapi_app
    logging.info("Successfully imported FastAPI app")
except Exception as e:
    logging.error(f"Failed to import FastAPI app: {e}")
    raise

# Create the Function App instance
app = func.FunctionApp()

@app.function_name(name="HttpTrigger")
@app.route(route="{*route}", auth_level=func.AuthLevel.ANONYMOUS)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger that forwards all requests to FastAPI
    """
    try:
        logging.info(f"Processing {req.method} request to {req.url}")
        asgi_middleware = func.AsgiMiddleware(fastapi_app)
        response = asgi_middleware.handle(req)
        logging.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logging.error(f"Error in HTTP trigger: {str(e)}")
        return func.HttpResponse(
            f"Internal server error: {str(e)}",
            status_code=500
        ) 