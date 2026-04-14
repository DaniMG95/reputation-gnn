from fastapi import APIRouter, Request, HTTPException
from core.persistence.interfaces.repository_interfaces import RepositoryPeopleInterface
from app.service.health_service import HealthService
from app.schemas.health import HealthCheckResponse, StatusTypes
from core.observability.logger import Logger

api_router = APIRouter(prefix="/health", tags=["health"])
logger = Logger("HealthAPI")

@api_router.get("/", response_model=HealthCheckResponse)
async def health_check(request: Request):
    logger.info("Received health check request")
    redis_client = request.app.state.redis
    repository_people: RepositoryPeopleInterface = request.app.state.repository_people_redis
    predict_service  = getattr(request.app.state, "predict_service", None)
    model_predictor = predict_service.model if predict_service else None

    health_service = HealthService(repository_people=repository_people, cache_connector=redis_client,
                                   model_predictor=model_predictor)

    try:
        health_status = health_service.check_health()
    except Exception as e:
        logger.warning("Health check failed: " + str(e))
        raise HTTPException(status_code=500, detail=str(e))
    if health_status.status == StatusTypes.unhealthy:
        logger.warning("Health check indicates unhealthy status: " + str(health_status))
        raise HTTPException(status_code=503, detail=health_status.model_dump())
    logger.info("Health check successful: " + str(health_status))
    return health_status
