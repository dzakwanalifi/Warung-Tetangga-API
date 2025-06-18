# function_app.py

import logging
import azure.functions as func
from app.main import app as fastapi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Buat instance Function App menggunakan Azure Functions v2 programming model
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# HTTP trigger function yang menangani semua request dan meneruskannya ke FastAPI
@app.route(route="{*route}")
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function yang menangani semua request dan meneruskannya ke FastAPI.
    
    Args:
        req: HTTP request dari Azure Functions
        
    Returns:
        HTTP response yang sudah diproses oleh FastAPI
    """
    logger.info(f"Processing request: {req.method} {req.url}")
    
    try:
        # Gunakan AsgiMiddleware untuk menjalankan FastAPI app
        asgi_middleware = func.AsgiMiddleware(fastapi_app)
        response = asgi_middleware.handle(req)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        ) 