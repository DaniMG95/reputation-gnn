import random
from ingest.schemas.person import Person

from ingest.simulator.service_people import ServicePeople
from ingest.simulator.generator_person import GeneratorPeople, TypePerson

class SimulatorIngest:

    MEAN_POSTS = 1000
    MAX_POSTS_INFLUENCERS = 2000
    MEAN_POSTS_BOTS = 100
    PERCENTAGE_FOLLOWERS_INFLUENCERS = 0.7
    DEVIATION_FOLLOWERS_INFLUENCERS = 0.1
    PERCENTAGE_FOLLOWERS_PERSON = 0.3

    PERCENTAGE_PERSONS_FOLLOW_TO_BOTS = 0.2
    PERCENTAGE_FOLLOW_TO_BOTS = 0.1

    PERCENTAGE_FOLLOWING_BOTS = 0.80
    PERCENTAGE_BOTS_FOLLOW_BOTS = 0.7
    DEVIATION_FOLLOWING_BOTS = 0.10
    PERCENTAGE_FOLLOWERS_BOTS = 0.10



    def __init__(self, n_accounts, percent_bots: int, p_influencers: float, service_people: ServicePeople):
        self.n_accounts = n_accounts
        self.percent_bots = percent_bots
        self.p_influencers = p_influencers
        self.service_people = service_people


    def _create_relationships_bot(self):
        deviation_following_bots = int(self.n_accounts * self.DEVIATION_FOLLOWING_BOTS)
        followings_bots = int(self.n_accounts * self.PERCENTAGE_FOLLOWING_BOTS)
        deviation_followers_bots = int(self.n_accounts * self.DEVIATION_FOLLOWERS)
        followers_bots = int(self.n_accounts * self.PERCENTAGE_FOLLOWERS_BOTS)
        range_following_bots = (max(0, followings_bots - deviation_following_bots),
                                followings_bots + deviation_following_bots)
        range_followers_bots = (max(0, followers_bots - deviation_followers_bots),
                                followers_bots + deviation_followers_bots)
        pass

    def _update_persons_relationships(self):
        persons = self.repository_people.get_all_persons()
        for person in persons:
            updated_person = Person(name=person.name, posts=person.posts, n_following=len(person.following),
                                    n_followers=len(person.followers),
                                    label='person' if person.label in [TypePerson.PERSON.value,
                                                                       TypePerson.INFLUENCER.value] else 'bot')
            self.repository_people.update_person(person=updated_person)


    def ingest(self):
        n_bots = int(self.n_accounts * self.percent_bots)
        n_persons = self.n_accounts - n_bots
        n_influencers = int(n_persons * self.p_influencers)
        followers_person = int(self.n_accounts * self.PERCENTAGE_FOLLOWERS_PERSON)
        followers_influencers = int(self.n_accounts * self.PERCENTAGE_FOLLOWERS_INFLUENCERS)
        deviation_followers_influencers = int(self.n_accounts * self.DEVIATION_FOLLOWERS_INFLUENCERS)
        range_followers_influencers = (followers_influencers - deviation_followers_influencers,
                                       followers_influencers + deviation_followers_influencers)
        n_bots_followed = int(n_bots * self.PERCENTAGE_FOLLOW_TO_BOTS)
        n_persons_follow_bot = int(n_persons * self.PERCENTAGE_PERSONS_FOLLOW_TO_BOTS)


        self.service_people.clean_persons()
        self.service_people.create_simulate_people(n_bots=n_bots, n_influencers=n_influencers,
                                                   mean_posts_bots=self.MEAN_POSTS_BOTS,
                                                   n_persons=self.n_accounts, mean_posts_persons=self.MEAN_POSTS,
                                                   max_posts_influencers=self.MAX_POSTS_INFLUENCERS)

        self.service_people.create_relationships_real_persons(followers=followers_person,
                                                              range_followers_influencers=range_followers_influencers,
                                                              n_bots_followed=n_bots_followed,
                                                              n_persons_follow_bot=n_persons_follow_bot)


