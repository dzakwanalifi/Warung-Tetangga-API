import logging
import azure.functions as func
from azure.functions import AsgiMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Import from the main file (now contains the fixed production version)
    from app.main import app as fastapi_app
    logger.info("✅ FastAPI app imported successfully from main")
    logger.info(f"✅ App routes count: {len(fastapi_app.routes)}")
    logger.info(f"✅ App router count: {len([r for r in fastapi_app.routes if hasattr(r, 'path') and r.path.startswith(('/auth', '/users', '/lapak', '/borongan', '/payments'))])}")
except Exception as e:
    logger.error(f"❌ Failed to import FastAPI app: {e}")
    import traceback
    logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    raise

# Create the function app
app = func.FunctionApp()

@app.function_name(name="HttpTrigger")
@app.route(route="{*route}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function yang menangani HTTP requests dan meneruskannya ke FastAPI"""
    try:
        logger.info(f"Request: {req.method} {req.url}")
        
        # Gunakan AsgiMiddleware untuk menangani request dengan FastAPI
        response = AsgiMiddleware(fastapi_app).handle(req)
        
        logger.info(f"Response status: {response.status_code}")
        return response
        
    except Exception as e:
        logger.error(f"Error in http_trigger: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return func.HttpResponse(
            f"Internal Server Error: {str(e)}",
            status_code=500
        ) 