from ingest.simulator.service_people import ServicePeople
from core.observability.logger import Logger
from ingest.config import settings

class SimulatorIngest:

    def __init__(self, n_accounts: int, p_bots: float, p_influencers: float, service_people: ServicePeople):
        if p_bots + p_influencers > 1:
            raise Exception("The sum of p_bots and p_influencers must be less than or equal to 1")
        self.n_accounts = n_accounts
        self.p_bots = p_bots
        self.p_influencers = p_influencers
        self.service_people = service_people
        self.logger = Logger(name="simulator_ingest")


    def ingest(self):
        n_bots = int(self.n_accounts * self.p_bots)
        n_persons = self.n_accounts - n_bots
        n_influencers = int(n_persons * self.p_influencers)
        followers_person = int(n_persons * settings.percentage_followers_person)
        followers_influencers = int(n_persons * settings.percentage_followers_influencers)
        deviation_followers_influencers = int(n_persons * settings.deviation_followers_influencers)
        range_followers_influencers = (followers_influencers - deviation_followers_influencers,
                                       followers_influencers + deviation_followers_influencers)
        n_bots_followed = int(n_bots * settings.percentage_follow_to_bots)
        n_persons_follow_bot = int(n_persons * settings.percentage_follow_to_bots)
        deviation_bots_following_persons = int(n_persons * settings.deviation_bots_following_persons)
        n_bots_following_persons = int(n_persons * settings.percentage_bots_following_persons)
        range_bots_following_persons = (max(0, n_bots_following_persons - deviation_bots_following_persons),
                                        n_bots_following_persons + deviation_bots_following_persons)
        n_bots_following_bots = int(n_bots * settings.percentage_bots_follow_bots)

        self.logger.info("Cleaning existing data")
        self.service_people.clean_persons()
        self.logger.info("Config parameters: \n")
        self.logger.info("Number of accounts: %d, \n"
                         "Number of bots: %d, \n"
                         "Number of influencers: %d \n"
                         "Number of persons: %d \n"
                         "Number followers per person: %d \n"
                         "Range followers per influencer: %d - %d \n"
                         "There are %d persons that follow %d bots\n"
                         "Range of persons followed a bot: %d - %d \n"
                         "Number of bots following bots: %d \n",
                         self.n_accounts, n_bots, n_influencers, self.n_accounts - (n_bots + n_influencers),
                         followers_person, range_followers_influencers[0], range_followers_influencers[1],
                         n_persons_follow_bot, n_bots_followed, range_bots_following_persons[0],
                         range_bots_following_persons[1], n_bots_following_bots)
        self.logger.info("Creating simulated people")
        self.service_people.create_simulate_people(n_bots=n_bots, n_influencers=n_influencers,
                                                   mean_posts_bots=settings.mean_posts_bots,
                                                   n_persons=self.n_accounts, mean_posts_persons=settings.mean_posts,
                                                   max_posts_influencers=settings.max_posts_influencers)
        self.logger.info("Creating relationships between people")
        self.service_people.create_relationships_real_persons(followers=followers_person,
                                                              range_followers_influencers=range_followers_influencers,
                                                              n_bots_followed=n_bots_followed,
                                                              n_persons_follow_bot=n_persons_follow_bot)
        self.logger.info("Creating relationships between bots and persons")
        self.service_people.create_relationships_bot(range_bots_following_persons=range_bots_following_persons,
                                                     n_bots_following_bots=n_bots_following_bots)


