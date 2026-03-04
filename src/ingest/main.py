from ingest.simulator.simulator_ingest import SimulatorIngest
from ingest.db.repository_people import RepositoryPeople
from ingest.simulator.service_people import ServicePeople

N_ACCOUNTS = 100
PERCENT_BOTS = 0.3
PERCENT_INFLUENCERS = 0.2

service_people = ServicePeople(repository_people=RepositoryPeople())


simulator_ingest = SimulatorIngest(n_accounts=N_ACCOUNTS, p_influencers=PERCENT_INFLUENCERS, p_bots=PERCENT_BOTS,
                                   service_people=service_people)

simulator_ingest.ingest()
