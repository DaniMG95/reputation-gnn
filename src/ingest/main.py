from ingest.simulator.simulator_ingest import SimulatorIngest
from core.persistence.neo4j.repositories.repository_people_neo4j import RepositoryPeopleNeo4j
from neomodel import db
from ingest.simulator.service_people import ServicePeople
from core.persistence.neo4j.connection import init_db_connection
from core.observability.logger import Logger
from ingest.config import settings

def main():
    Logger.setup_logging(app_name=settings.app_logger.app_name)
    logger_ingest = Logger(name="main")

    init_db_connection(url=settings.neo4j.uri_neo4j)

    repository_people=RepositoryPeopleNeo4j(db=db)
    service_people = ServicePeople(repository_people=repository_people)


    simulator_ingest = SimulatorIngest(n_accounts=settings.n_accounts, p_influencers=settings.p_influencers,
                                       p_bots=settings.p_bots, service_people=service_people)

    logger_ingest.info("Starting the ingestion process")
    simulator_ingest.ingest()
    logger_ingest.info("Ingestion process completed")

if __name__ == "__main__":
    main()