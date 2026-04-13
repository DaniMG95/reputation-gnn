from app.domain.repository_interfaces import PersonRepositoryCacheInterface
from common.db.interfaces import RepositoryPeopleInterface
from brain.architectures.interfaces import ModelBotDetectorInterface
from app.schemas.health import HealthCheckResponse, StatusTypes, ComponentStatus
from common.logger import Logger


class HealthService:
    def __init__(self, repository_people: RepositoryPeopleInterface, cache_connector: PersonRepositoryCacheInterface,
                 model_predictor: ModelBotDetectorInterface):
        self.repository_people = repository_people
        self.cache_connector = cache_connector
        self.model_predictor = model_predictor
        self.logger = Logger(self.__class__.__name__)

    def check_health(self) -> HealthCheckResponse:
        self.logger.debug("Performing health check...")
        checks_connections = [self.cache_connector, self.repository_people]
        is_healthy = True
        status = StatusTypes.healthy

        components = []
        self.logger.debug("Checking connections to dependencies...")
        for check in checks_connections:
            try:
                if check.ping():
                    components.append(ComponentStatus(name=check.name, status=StatusTypes.healthy))
                else:
                    components.append(ComponentStatus(name=check.name, status=StatusTypes.unhealthy))
                    self.logger.warning(f"Dependency {check.name} is unhealthy.")
                    is_healthy = False

            except Exception as e:
                raise Exception(f"Health check failed: {str(e)}")
        if self.model_predictor is not None and self.model_predictor.is_model_available():
            components.append(ComponentStatus(name="Model", status=StatusTypes.healthy))
        else:
            components.append(ComponentStatus(name="Model", status=StatusTypes.unhealthy))
            self.logger.warning(f"Dependency Model is unhealthy.")

        if not is_healthy:
            status = StatusTypes.unhealthy
        health_status = HealthCheckResponse(status=status, components=components)
        return health_status
