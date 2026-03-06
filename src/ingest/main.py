from ingest.simulator.simulator_ingest import SimulatorIngest
from ingest.db.repository_people import RepositoryPeople
from ingest.simulator.service_people import ServicePeople
from ingest.db.connection import init_db_connection
from ingest.logger import LoggerIngest
import argparse

def main():
    LoggerIngest.setup_logging()
    logger_ingest = LoggerIngest(name="main")

    parser = argparse.ArgumentParser(description='Ingest data into the graph database.')
    parser.add_argument('--n_accounts', type=int, default=10, help='Number of accounts to create')
    parser.add_argument('--p_bots', type=float, default=0.3, help='Percentage of bot accounts')
    parser.add_argument('--p_influencers', type=float, default=0.2,
                        help='Percentage of influencer accounts')
    args = parser.parse_args()
    init_db_connection()

    repository_people=RepositoryPeople()
    service_people = ServicePeople(repository_people=repository_people)


    simulator_ingest = SimulatorIngest(n_accounts=args.n_accounts, p_influencers=args.p_influencers, p_bots=args.p_bots,
                                       service_people=service_people)

    logger_ingest.info("Starting the ingestion process")
    simulator_ingest.ingest()
    logger_ingest.info("Ingestion process completed")

if __name__ == "__main__":
    main()