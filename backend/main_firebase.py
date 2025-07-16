#!/usr/bin/env python3
"""
Firebase Cloud Functions Entry Point
====================================

This file adapts the FastAPI application for Firebase Cloud Functions deployment.
"""

from firebase_functions import https_fn
from firebase_functions import options
import main

# Set up CORS options for the function
cors_options = options.CorsOptions(
    cors_origins=["https://scrape.mypp.site", "https://mypp.site"],
    cors_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    cors_allow_credentials=True,
)

@https_fn.on_request(cors=cors_options, memory=options.MemoryOption.MB_512)
def api(req: https_fn.Request) -> https_fn.Response:
    """
    Cloud Function entry point for the FastAPI application.
    
    This function handles all API requests and routes them through the FastAPI app.
    """
    try:
        # Import and run the FastAPI app
        from main import app
        
        # Convert Firebase request to ASGI
        # This is handled by functions-framework
        return app(req.environ, lambda *args: None)
        
    except Exception as e:
        print(f"Error in Firebase function: {e}")
        return https_fn.Response(
            response=f"Internal server error: {str(e)}",
            status=500,
            headers={"Content-Type": "text/plain"}
        )
