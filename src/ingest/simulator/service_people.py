from common.db.interfaces import RepositoryPeopleInterface
from common.schemas.person import PersonSchema, TypePerson
from ingest.simulator.generator_person import GeneratorPeople
from ingest.simulator.generator import GeneratorFactory
import random
from common.logger import LoggerIngest
from tqdm import tqdm


class ServicePeople:
    def __init__(self, repository_people: RepositoryPeopleInterface):
        self.repository_people = repository_people
        self.logger = LoggerIngest(name="service_people")

    def create_relationships(self, person: PersonSchema, followers: list[PersonSchema] = None,
                             following: list[PersonSchema] = None):
        self.repository_people.create_relationships(person=person, followers=followers, following=following)

    def create_simulate_people(self, n_bots: int, n_persons: int, n_influencers: int, mean_posts_bots: int,
                               max_posts_influencers: int, mean_posts_persons: int):
        n_persons = n_persons - n_bots
        n_persons_not_influencers = n_persons - n_influencers
        names_used = []
        generator_type_bot = GeneratorFactory.get_generator(type_person=TypePerson.BOT)
        generator_bot = GeneratorPeople(type_person=TypePerson.BOT, n_people=n_bots,
                                        range_posts=(0, mean_posts_bots), n_followers=0, n_following=0,
                                        generator=generator_type_bot)
        for bot in tqdm(generator_bot, desc="Generating bots"):
            self.repository_people.create_person(person=bot)

        names_used = generator_type_bot.names[:]

        generator_type_influencer = GeneratorFactory.get_generator(type_person=TypePerson.INFLUENCER,
                                                                  prohibited_names=names_used)


        generator_influencers = GeneratorPeople(type_person=TypePerson.INFLUENCER, n_people=n_influencers,
                                                range_posts=(mean_posts_persons, max_posts_influencers),
                                                n_followers=0, n_following=0, generator=generator_type_influencer)
        for influencer in tqdm(generator_influencers, desc="Generating influencers"):
            self.repository_people.create_person(person=influencer)

        names_used += generator_type_influencer.names[:]
        generator_type_person = GeneratorFactory.get_generator(type_person=TypePerson.PERSON,
                                                              prohibited_names=names_used)

        generator_persons = GeneratorPeople(type_person=TypePerson.PERSON, n_people=n_persons_not_influencers,
                                            range_posts=(50, mean_posts_persons), n_followers=0, n_following=0,
                                            generator=generator_type_person)
        for person in tqdm(generator_persons, desc="Generating persons"):
            self.repository_people.create_person(person=person)

    def create_relationships_real_persons(self, followers: int, range_followers_influencers: tuple[int, int],
                                          n_persons_follow_bot: int, n_bots_followed: int):
        real_persons = self.repository_people.get_persons_by_type(user_type=TypePerson.PERSON)
        real_persons += self.repository_people.get_persons_by_type(user_type=TypePerson.INFLUENCER)
        persons_follow_bots = random.sample(real_persons, n_persons_follow_bot)
        bots = self.repository_people.get_persons_by_type(user_type=TypePerson.BOT)

        total_steps = len(real_persons) + n_persons_follow_bot

        with tqdm(total=total_steps, desc="Creating relationships for real persons") as pbar:
            for real_person in real_persons:
                persons = real_persons[:]
                persons.remove(real_person)
                if real_person.user_type == TypePerson.INFLUENCER:
                    n_followers = random.randint(range_followers_influencers[0], range_followers_influencers[1])
                else:
                    n_followers = random.randint(0, followers)
                followers_selected = random.sample(persons, n_followers)
                self.create_relationships(person=real_person, followers=followers_selected)
                pbar.update(1)

            for person_to_bots in persons_follow_bots:
                bots_followed = random.sample(bots, n_bots_followed)
                self.create_relationships(person_to_bots, followers=bots_followed)
                pbar.update(1)

    def create_relationships_bot(self, range_bots_following_persons: tuple[int, int], n_bots_following_bots: int):
        bots = self.repository_people.get_persons_by_type(user_type=TypePerson.BOT)
        real_persons = self.repository_people.get_persons_by_type(user_type=TypePerson.PERSON)
        real_persons += self.repository_people.get_persons_by_type(user_type=TypePerson.INFLUENCER)
        for bot in tqdm(bots, desc="Creating relationships for bots following persons and bots"):
            bots_selected = bots[:]
            bots_selected.remove(bot)
            real_persons_selected = real_persons[:]
            bots_selected = random.sample(bots_selected, n_bots_following_bots)
            real_persons_selected = random.sample(real_persons_selected, random.randint(range_bots_following_persons[0],
                                                                                        range_bots_following_persons[1]))
            self.create_relationships(person=bot, following=bots_selected + real_persons_selected)


    def clean_persons(self):
        self.repository_people.delete_all()

