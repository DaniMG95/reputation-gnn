from ingest.simulator.service_people import ServicePeople
from common.logger import LoggerIngest

class SimulatorIngest:

    MEAN_POSTS = 1000
    MAX_POSTS_INFLUENCERS = 2000
    MEAN_POSTS_BOTS = 100
    PERCENTAGE_FOLLOWERS_INFLUENCERS = 0.7
    DEVIATION_FOLLOWERS_INFLUENCERS = 0.1
    PERCENTAGE_FOLLOWERS_PERSON = 0.3

    PERCENTAGE_PERSONS_FOLLOW_TO_BOTS = 0.2
    PERCENTAGE_FOLLOW_TO_BOTS = 0.1

    PERCENTAGE_BOTS_FOLLOWING_PERSONS = 0.80
    DEVIATION_BOTS_FOLLOWING_PERSONS = 0.10
    PERCENTAGE_BOTS_FOLLOW_BOTS = 0.7



    def __init__(self, n_accounts: int, p_bots: float, p_influencers: float, service_people: ServicePeople):
        if p_bots + p_influencers > 1:
            raise Exception("The sum of p_bots and p_influencers must be less than or equal to 1")
        self.n_accounts = n_accounts
        self.p_bots = p_bots
        self.p_influencers = p_influencers
        self.service_people = service_people
        self.logger = LoggerIngest(name="simulator_ingest")


    def ingest(self):
        n_bots = int(self.n_accounts * self.p_bots)
        n_persons = self.n_accounts - n_bots
        n_influencers = int(n_persons * self.p_influencers)
        followers_person = int(n_persons * self.PERCENTAGE_FOLLOWERS_PERSON)
        followers_influencers = int(n_persons * self.PERCENTAGE_FOLLOWERS_INFLUENCERS)
        deviation_followers_influencers = int(n_persons * self.DEVIATION_FOLLOWERS_INFLUENCERS)
        range_followers_influencers = (followers_influencers - deviation_followers_influencers,
                                       followers_influencers + deviation_followers_influencers)
        n_bots_followed = int(n_bots * self.PERCENTAGE_FOLLOW_TO_BOTS)
        n_persons_follow_bot = int(n_persons * self.PERCENTAGE_PERSONS_FOLLOW_TO_BOTS)
        deviation_bots_following_persons = int(n_persons * self.DEVIATION_BOTS_FOLLOWING_PERSONS)
        n_bots_following_persons = int(n_persons * self.PERCENTAGE_BOTS_FOLLOWING_PERSONS)
        range_bots_following_persons = (max(0, n_bots_following_persons - deviation_bots_following_persons),
                                        n_bots_following_persons + deviation_bots_following_persons)
        n_bots_following_bots = int(n_bots * self.PERCENTAGE_BOTS_FOLLOW_BOTS)

        self.logger.info("Cleaning existing data")
        self.service_people.clean_persons()
        self.logger.info("Creating simulated people")
        self.service_people.create_simulate_people(n_bots=n_bots, n_influencers=n_influencers,
                                                   mean_posts_bots=self.MEAN_POSTS_BOTS,
                                                   n_persons=self.n_accounts, mean_posts_persons=self.MEAN_POSTS,
                                                   max_posts_influencers=self.MAX_POSTS_INFLUENCERS)
        self.logger.info("Creating relationships between people")
        self.service_people.create_relationships_real_persons(followers=followers_person,
                                                              range_followers_influencers=range_followers_influencers,
                                                              n_bots_followed=n_bots_followed,
                                                              n_persons_follow_bot=n_persons_follow_bot)
        self.logger.info("Creating relationships between bots and persons")
        self.service_people.create_relationships_bot(range_bots_following_persons=range_bots_following_persons,
                                                     n_bots_following_bots=n_bots_following_bots)


