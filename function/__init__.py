import azure.functions as func
import logging
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)

# Default fallback function for import errors
def fallback_main(error_msg: str):
    def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
        return func.HttpResponse(
            f"Failed to import FastAPI app: {error_msg}",
            status_code=500
        )
    return main

try:
    from azure.functions import AsgiMiddleware
    from function.app.main import app
    
    def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
        logging.info(f"Processing request: {req.method} {req.url}")
        
        try:
            # Parse the URL to get the path
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(req.url)
            
            # Extract path - this will now be the full path after the domain
            path = parsed_url.path
            
            # Ensure path starts with /
            if not path.startswith('/'):
                path = f'/{path}'
            
            # If path is empty, default to root
            if path == '' or path is None:
                path = '/'
                
            logging.info(f"Extracted path: {path}")
            
            # Extract query string
            query_string = parsed_url.query or ''
            
            # Build headers
            headers = []
            for key, value in req.headers.items():
                headers.append([key.lower().encode(), value.encode()])
            
            # Create ASGI scope
            scope = {
                'type': 'http',
                'method': req.method,
                'path': path,
                'query_string': query_string.encode(),
                'headers': headers,
                'server': ('localhost', 80),
                'scheme': 'https' if req.url.startswith('https') else 'http',
            }
            
            logging.info(f"ASGI scope: {scope}")
            
            # Use AsgiMiddleware to handle the request
            asgi_middleware = AsgiMiddleware(app)
            return asgi_middleware.handle(req, context)
            
        except Exception as request_error:
            logging.error(f"Request processing error: {str(request_error)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return func.HttpResponse(
                f"Request processing failed: {str(request_error)}",
                status_code=500
            )

except ImportError as import_error:
    logging.error(f"Failed to import FastAPI app: {str(import_error)}")
    main = fallback_main(str(import_error)) 