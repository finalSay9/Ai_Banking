from fastapi import APIRouter, status
from schemas.prediction import HealthResponse
from core.config import settings
from ml.predict import FraudPredictor
from core.logging import get_logger
import redis
import psutil
from datetime import datetime

logger = get_logger(__name__)
router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API health status"
)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns service status and model availability.
    """
    try:
        predictor = FraudPredictor()
        model_loaded = predictor.model_loaded
        
        return HealthResponse(
            status="healthy" if model_loaded else "degraded",
            version=settings.VERSION,
            model_loaded=model_loaded
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version=settings.VERSION,
            model_loaded=False
        )

@router.get(
    "/health/detailed",
    summary="Detailed health check",
    description="Detailed health status with dependencies"
)
async def detailed_health_check():
    """
    Detailed health check including dependencies.
    
    Checks model, Redis, and system resources.
    """
    health_status = {
        'status': 'healthy',
        'version': settings.VERSION,
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # Check ML model
    try:
        predictor = FraudPredictor()
        health_status['checks']['model'] = {
            'status': 'up' if predictor.model_loaded else 'down',
            'model_version': settings.MODEL_VERSION
        }
    except Exception as e:
        health_status['checks']['model'] = {
            'status': 'down',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Check Redis connection
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status['checks']['redis'] = {'status': 'up'}
    except Exception as e:
        health_status['checks']['redis'] = {
            'status': 'down',
            'error': str(e)
        }
        health_status['status'] = 'degraded'
    
    # Check system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        health_status['checks']['system'] = {
            'status': 'up',
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / (1024 * 1024)
        }
        
        # Warn if resources are low
        if cpu_percent > 90 or memory.percent > 90:
            health_status['status'] = 'degraded'
            
    except Exception as e:
        health_status['checks']['system'] = {
            'status': 'unknown',
            'error': str(e)
        }
    
    return health_status

@router.get(
    "/ready",
    summary="Readiness check",
    description="Check if service is ready to handle requests"
)
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    
    Returns 200 if service is ready, 503 if not.
    """
    try:
        predictor = FraudPredictor()
        if predictor.model_loaded:
            return {'status': 'ready'}
        else:
            return {'status': 'not ready', 'reason': 'model not loaded'}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {'status': 'not ready', 'reason': str(e)}

@router.get(
    "/liveness",
    summary="Liveness check",
    description="Check if service is alive"
)
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    
    Always returns 200 if the service is running.
    """
    return {'status': 'alive'}
