from ingest.simulator.simulator_ingest import SimulatorIngest
from ingest.db.repository_people import RepositoryPeople
from ingest.simulator.service_people import ServicePeople
from ingest.db.connection import init_db_connection
from logger import LoggerIngest

LoggerIngest.setup_logging()
logger_ingest = LoggerIngest(name="main")

N_ACCOUNTS = 50
PERCENT_BOTS = 0.3
PERCENT_INFLUENCERS = 0.2

init_db_connection()

repository_people=RepositoryPeople()
service_people = ServicePeople(repository_people=repository_people)


simulator_ingest = SimulatorIngest(n_accounts=N_ACCOUNTS, p_influencers=PERCENT_INFLUENCERS, p_bots=PERCENT_BOTS,
                                   service_people=service_people)

logger_ingest.info("Starting the ingestion process")
simulator_ingest.ingest()
logger_ingest.info("Ingestion process completed")
