from ingest.db.repository_people import RepositoryPeople
from ingest.schemas.person import Person
from ingest.simulator.generator_person import TypePerson, GeneratorPeople
import random


class ServicePeople:
    def __init__(self, repository_people: RepositoryPeople):
        self.repository_people = repository_people

    def create_relationships(self, person: Person, followers: list[Person] = None, following: list[Person] = None):
        self.repository_people.create_relationships(person=person, followers=followers, following=following)
        if followers:
            for follower in followers:
                self.repository_people.create_relationships(follower, following=[person])
        if following:
            for follow in following:
                self.repository_people.create_relationships(follow, followers=[person])

    def create_simulate_people(self, n_bots: int, n_persons: int, n_influencers: int, mean_posts_bots: int,
                               max_posts_influencers: int, mean_posts_persons: int):
        n_persons = n_persons - n_bots
        n_persons_not_influencers = n_persons - n_influencers
        generator_bot = GeneratorPeople(type_person=TypePerson.BOT, n_people=n_bots,
                                        range_posts=(0, mean_posts_bots), n_followers=0, n_following=0)
        generator_influencers = GeneratorPeople(type_person=TypePerson.INFLUENCER, n_people=n_influencers,
                                                range_posts=(mean_posts_persons, max_posts_influencers),
                                                n_followers=0, n_following=0)
        generator_persons = GeneratorPeople(type_person=TypePerson.PERSON, n_people=n_persons_not_influencers,
                                            range_posts=(0, mean_posts_persons), n_followers=0, n_following=0)
        for generator in [generator_bot, generator_persons, generator_influencers]:
            for person in generator:
                self.repository_people.create_person(person=person)

    def create_relationships_real_persons(self, followers: int, range_followers_influencers: tuple[int, int],
                                          n_persons_follow_bot: int, n_bots_followed: int):
        real_persons = self.repository_people.get_persons_by_type(label=TypePerson.PERSON.value)
        real_persons += self.repository_people.get_persons_by_type(label=TypePerson.INFLUENCER.value)
        for real_person in real_persons:
            persons = real_persons[:]
            persons.remove(real_person)
            if real_person.label == TypePerson.INFLUENCER.value:
                n_followers = random.randint(range_followers_influencers[0], range_followers_influencers[1])
            else:
                n_followers = random.randint(0, followers)
            followers = random.sample(persons, n_followers)
            self.repository_people.create_relationships(person=real_person, followers=followers)
            for follower in followers:
                self.repository_people.create_relationships(person=follower, following=[real_person])
        bots = self.repository_people.get_persons_by_type(label=TypePerson.BOT.value)
        persons_follow_bots = random.sample(real_persons, n_persons_follow_bot)
        for person_to_bots in persons_follow_bots:
            bots_followed = random.sample(bots, n_bots_followed)
            self.repository_people.create_relationships(person_to_bots, followers=[f])

    def clean_persons(self):
        self.repository_people.delete_all()

