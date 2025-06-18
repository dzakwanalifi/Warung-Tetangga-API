import azure.functions as func
import logging
import sys
import os

# Create the Function App instance
app = func.FunctionApp()

@app.function_name(name="HttpTrigger")
@app.route(route="{*route}", auth_level=func.AuthLevel.ANONYMOUS)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    Debug version to test imports step by step
    """
    try:
        # Add the app directory to the Python path
        sys.path.append(os.path.dirname(__file__))
        
        # Test basic import
        try:
            import fastapi
            step1 = "✅ FastAPI imported"
        except Exception as e:
            step1 = f"❌ FastAPI failed: {e}"
        
        # Test app import
        try:
            from app.main import app as fastapi_app
            step2 = "✅ App imported"
        except Exception as e:
            step2 = f"❌ App failed: {e}"
        
        return func.HttpResponse(
            f'{{"step1": "{step1}", "step2": "{step2}"}}',
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            headers={"Content-Type": "application/json"}
        ) 