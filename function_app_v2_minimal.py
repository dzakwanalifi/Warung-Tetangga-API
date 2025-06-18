import azure.functions as func
import logging
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Function App instance
app = func.FunctionApp()

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import FastAPI app
try:
    from app.main import app as fastapi_app
    logger.info("✅ FastAPI app imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import FastAPI app: {e}")
    fastapi_app = None

@app.function_name(name="HttpTrigger")
@app.route(route="{*route}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function that handles HTTP requests and forwards them to FastAPI"""
    
    if fastapi_app is None:
        return func.HttpResponse(
            '{"error": "FastAPI app not available"}',
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
    
    try:
        # Use AsgiMiddleware to handle the request with FastAPI
        from azure.functions import AsgiMiddleware
        return AsgiMiddleware(fastapi_app).handle(req)
        
    except Exception as e:
        logger.error(f"Error in http_trigger: {e}")
        return func.HttpResponse(
            f'{{"error": "Internal Server Error: {str(e)}"}}',
            status_code=500,
            headers={"Content-Type": "application/json"}
        ) 