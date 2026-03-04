from ingest.simulator.simulator_ingest import SimulatorIngest
from ingest.db.repository_people import RepositoryPeople
from ingest.simulator.service_people import ServicePeople
from ingest.db.connection import init_db_connection

N_ACCOUNTS = 100
PERCENT_BOTS = 0.3
PERCENT_INFLUENCERS = 0.2

init_db_connection()

repository_people=RepositoryPeople()
service_people = ServicePeople(repository_people=repository_people)


simulator_ingest = SimulatorIngest(n_accounts=N_ACCOUNTS, p_influencers=PERCENT_INFLUENCERS, p_bots=PERCENT_BOTS,
                                   service_people=service_people)

simulator_ingest.ingest()
