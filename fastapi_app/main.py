from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import uvicorn
from core.config import settings
from core.logging import setup_logging, get_logger
from api.v1.router import api_router

# Setup logging
setup_logging(level="INFO" if not settings.DEBUG else "DEBUG")
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for startup and shutdown.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Model version: {settings.MODEL_VERSION}")
    
    # Verify model is loaded
    from ml.predict import FraudPredictor
    predictor = FraudPredictor()
    if predictor.model_loaded:
        logger.info("ML model loaded successfully")
    else:
        logger.warning("ML model not loaded - service may not function correctly")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Machine Learning service for real-time fraud detection in banking transactions",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "model_version": settings.MODEL_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Additional utility endpoints
@app.get("/api/version", tags=["Root"])
async def get_version():
    """Get API and model version."""
    return {
        "api_version": settings.VERSION,
        "model_version": settings.MODEL_VERSION
    }

@app.get("/api/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get basic metrics (extend for Prometheus)."""
    return {
        "status": "operational",
        "model_loaded": True,
        # Add more metrics as needed
    }

if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )
