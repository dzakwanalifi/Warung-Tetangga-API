import azure.functions as func
import logging
import sys
import os
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Function App instance
app = func.FunctionApp()

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import FastAPI app with better error handling
fastapi_app = None
import_error = None

try:
    # Set environment variable to prevent database creation during import
    os.environ["SKIP_DB_INIT"] = "true"
    
    from app.main import app as fastapi_app
    logger.info("✅ FastAPI app imported successfully")
except Exception as e:
    import_error = str(e)
    logger.error(f"❌ Failed to import FastAPI app: {e}")

@app.function_name(name="HttpTrigger")
@app.route(route="{*route}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function that handles HTTP requests and forwards them to FastAPI"""
    
    logger.info(f"🔄 Request: {req.method} {req.url}")
    logger.info(f"🔄 Route: {req.route_params.get('route', 'root')}")
    
    # If FastAPI app is not available, try to create a simple fallback
    if fastapi_app is None:
        # Return a simple FastAPI-like response for basic endpoints
        route = req.route_params.get('route', '')
        
        if route == '' or route == '/':
            return func.HttpResponse(
                json.dumps({"message": "Welcome to Warung Warga API v1.0.0 (Minimal Mode)"}),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )
        elif route == 'health':
            return func.HttpResponse(
                json.dumps({"status": "ok", "mode": "minimal"}),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )
        else:
            error_response = {
                "error": "FastAPI app not available",
                "import_error": import_error,
                "available_endpoints": ["/", "/health"],
                "request_info": {
                    "method": req.method,
                    "url": str(req.url),
                    "route": route
                }
            }
            return func.HttpResponse(
                json.dumps(error_response, indent=2),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
    
    try:
        # Use AsgiMiddleware to handle the request with FastAPI
        from azure.functions import AsgiMiddleware
        response = AsgiMiddleware(fastapi_app).handle(req)
        logger.info(f"✅ Response status: {response.status_code}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in http_trigger: {e}")
        error_response = {
            "error": "Internal Server Error",
            "details": str(e),
            "request_info": {
                "method": req.method,
                "url": str(req.url),
                "route": req.route_params.get('route', 'root')
            }
        }
        return func.HttpResponse(
            json.dumps(error_response, indent=2),
            status_code=500,
            headers={"Content-Type": "application/json"}
        ) 