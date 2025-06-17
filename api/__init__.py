import azure.functions as func
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)

# Import the FastAPI app
from .app.main import app

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Azure Functions entry point yang menghubungkan dengan FastAPI.
    Semua HTTP requests akan diteruskan ke aplikasi FastAPI.
    """
    logging.info(f'Python HTTP trigger function processed a request: {req.method} {req.url}')
    
    try:
        # Use Azure Functions ASGI adapter untuk FastAPI
        asgi_app = func.AsgiFunction(app)
        return await asgi_app.handle_async(req, context)
    except Exception as e:
        logging.error(f"Error in Azure Functions handler: {str(e)}")
        return func.HttpResponse(
            f"Internal server error: {str(e)}",
            status_code=500
        ) 