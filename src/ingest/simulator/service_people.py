from ingest.db.repository_people import RepositoryPeople
from ingest.schemas.person import PersonSchema
from ingest.simulator.generator_person import TypePerson, GeneratorPeople, GeneratorNameFactory
import random
from ingest.logger import LoggerIngest


class ServicePeople:
    def __init__(self, repository_people: RepositoryPeople):
        self.repository_people = repository_people
        self.logger = LoggerIngest(name="service_people")

    def create_relationships(self, person: PersonSchema, followers: list[PersonSchema] = None,
                             following: list[PersonSchema] = None):
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
        generator_names_bot = GeneratorNameFactory.get_generator(type_person=TypePerson.BOT)
        generator_bot = GeneratorPeople(type_person=TypePerson.BOT, n_people=n_bots,
                                        range_posts=(0, mean_posts_bots), n_followers=0, n_following=0,
                                        generator_names=generator_names_bot)
        for bot in generator_bot:
            self.repository_people.create_person(person=bot)

        generator_names_person = GeneratorNameFactory.get_generator(type_person=TypePerson.PERSON,
                                                                    prohibited_names=generator_names_bot.names)

        generator_influencers = GeneratorPeople(type_person=TypePerson.INFLUENCER, n_people=n_influencers,
                                                range_posts=(mean_posts_persons, max_posts_influencers),
                                                n_followers=0, n_following=0, generator_names=generator_names_person)
        generator_persons = GeneratorPeople(type_person=TypePerson.PERSON, n_people=n_persons_not_influencers,
                                            range_posts=(0, mean_posts_persons), n_followers=0, n_following=0,
                                            generator_names=generator_names_person)
        for generator in [generator_persons, generator_influencers]:
            for person in generator:
                self.repository_people.create_person(person=person)

    def create_relationships_real_persons(self, followers: int, range_followers_influencers: tuple[int, int],
                                          n_persons_follow_bot: int, n_bots_followed: int):
        real_persons = self.repository_people.get_persons_by_type(user_type=TypePerson.PERSON.value)
        real_persons += self.repository_people.get_persons_by_type(user_type=TypePerson.INFLUENCER.value)
        for real_person in real_persons:
            persons = real_persons[:]
            persons.remove(real_person)
            if real_person.user_type == TypePerson.INFLUENCER.value:
                n_followers = random.randint(range_followers_influencers[0], range_followers_influencers[1])
            else:
                n_followers = random.randint(0, followers)
            followers_selected = random.sample(persons, n_followers)
            self.create_relationships(person=real_person, followers=followers_selected)
        bots = self.repository_people.get_persons_by_type(user_type=TypePerson.BOT.value)
        persons_follow_bots = random.sample(real_persons, n_persons_follow_bot)
        for person_to_bots in persons_follow_bots:
            bots_followed = random.sample(bots, n_bots_followed)
            self.create_relationships(person_to_bots, followers=bots_followed)
        influencers = self.repository_people.get_persons_by_type(user_type=TypePerson.INFLUENCER.value)
        for influencer in influencers:
            influencer.user_type = TypePerson.PERSON.value
            self.repository_people.update_person(person=influencer)

    def create_relationships_bot(self, range_bots_following_persons: tuple[int, int], n_bots_following_bots: int):
        bots = self.repository_people.get_persons_by_type(user_type=TypePerson.BOT.value)
        real_persons = self.repository_people.get_persons_by_type(user_type=TypePerson.PERSON.value)
        real_persons += self.repository_people.get_persons_by_type(user_type=TypePerson.INFLUENCER.value)
        for bot in bots:
            bots_selected = bots[:]
            bots_selected.remove(bot)
            real_persons_selected = real_persons[:]
            bots_selected = random.sample(bots_selected, n_bots_following_bots)
            real_persons_selected = random.sample(real_persons_selected, random.randint(range_bots_following_persons[0],
                                                                                        range_bots_following_persons[1]))
            self.create_relationships(person=bot, following=bots_selected + real_persons_selected)


    def clean_persons(self):
        self.repository_people.delete_all()

