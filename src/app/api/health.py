from fastapi import APIRouter, Request, HTTPException
from common.db.interfaces import RepositoryPeopleInterface
from app.service.health_service import HealthService
from app.schemas.health import HealthCheckResponse, StatusTypes


api_router = APIRouter(prefix="/health", tags=["health"])


@api_router.get("/", response_model=HealthCheckResponse)
async def health_check(request: Request):
    redis_client = request.app.state.redis
    repository_people: RepositoryPeopleInterface = request.app.state.repository_people_redis
    model_predictor = getattr(request.app.state, "model", None)

    health_service = HealthService(repository_people=repository_people, cache_connector=redis_client,
                                   model_predictor=model_predictor)

    try:
        health_status = health_service.check_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if health_status.status == StatusTypes.unhealthy:
        raise HTTPException(status_code=503, detail=health_status.model_dump())

    return health_status
