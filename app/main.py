from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from models.poem_models import PoemRequest, PoemResponse, HealthResponse
from services.poem_service import PoemService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="🎭 AI Poem Generator API",
    description="A powerful FastAPI backend for generating beautiful poems using OpenAI's GPT models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3001")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize poem service
poem_service = PoemService()

@app.get("/", response_model=dict)
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "🎭 Welcome to the AI Poem Generator API",
        "version": "1.0.0",
        "framework": "FastAPI + Python",
        "endpoints": {
            "health": "/health",
            "generate_poem": "POST /api/poems/generate",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "status": "🚀 Ready to generate beautiful poetry!"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check endpoint with OpenAI status"""
    service_info = poem_service.get_service_info()
    
    return HealthResponse(
        status="healthy",
        message="AI Poem Generator API is running smoothly",
        openai_configured=service_info["openai_configured"],
        version="1.0.0"
    )

@app.get("/api/service/status")
async def service_status():
    """Get detailed service status including OpenAI connectivity"""
    try:
        service_info = poem_service.get_service_info()
        
        # Test OpenAI connection if configured
        openai_status = None
        if service_info["openai_configured"]:
            openai_status = await poem_service.test_openai_connection()
        
        return {
            "service": "AI Poem Generator",
            "status": "operational",
            "timestamp": f"{datetime.now().isoformat()}",
            "configuration": service_info,
            "openai_connection": openai_status,
            "features": {
                "poem_generation": True,
                "multiple_styles": True,
                "multiple_lengths": True,
                "fallback_poems": True
            }
        }
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        return {
            "service": "AI Poem Generator",
            "status": "error",
            "error": str(e),
            "timestamp": f"{datetime.now().isoformat()}"
        }

@app.post("/api/poems/generate", response_model=PoemResponse)
@limiter.limit("15/minute")  # Increased rate limit: 15 requests per minute per IP
async def generate_poem(
    request: Request,
    poem_request: PoemRequest
):
    """
    Generate a poem based on the provided theme, style, and length.
    Uses OpenAI API when available, falls back to high-quality mock poems otherwise.
    """
    start_time = datetime.now()
    
    try:
        # Input validation
        if not poem_request.theme or not poem_request.theme.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid input",
                    "message": "Theme cannot be empty. Please provide a theme for your poem."
                }
            )
        
        # Log request
        client_ip = get_remote_address(request)
        logger.info(f"Poem request from {client_ip}: theme='{poem_request.theme}', style='{poem_request.style}', length='{poem_request.length}'")
        
        # Generate poem using the enhanced service
        poem_text = await poem_service.generate_poem(
            theme=poem_request.theme.strip(),
            style=poem_request.style,
            length=poem_request.length
        )
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Log successful generation
        logger.info(f"Successfully generated poem in {response_time:.2f}s (length: {len(poem_text)} chars)")
        
        return PoemResponse(
            success=True,
            poem=poem_text,
            theme=poem_request.theme.strip(),
            style=poem_request.style,
            length=poem_request.length,
            generation_method="openai" if poem_service.is_openai_available() else "fallback",
            response_time_seconds=round(response_time, 2)
        )
        
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Validation error",
                "message": str(e)
            }
        )
    except Exception as e:
        error_msg = str(e).lower()
        response_time = (datetime.now() - start_time).total_seconds()
        
        logger.error(f"Error generating poem after {response_time:.2f}s: {str(e)}")
        
        # Handle specific error types
        if "quota exceeded" in error_msg:
            raise HTTPException(
                status_code=503,
                detail={
                    "success": False,
                    "error": "Service temporarily unavailable",
                    "message": "OpenAI API quota exceeded. Using fallback poem generation.",
                    "fallback_available": True
                }
            )
        elif "rate limit" in error_msg:
            raise HTTPException(
                status_code=429,
                detail={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": "Too many requests to OpenAI API. Please try again in a moment.",
                    "retry_after": 60
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": "Generation failed",
                    "message": "An error occurred while generating your poem. Please try again.",
                    "fallback_available": True
                }
            )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting AI Poem Generator API on {host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"❤️  Health Check: http://{host}:{port}/health")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if os.getenv("ENV") == "development" else False
    )