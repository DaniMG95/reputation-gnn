from faker import Faker
import random
from enum import Enum
from ingest.schemas.person import PersonSchema
from abc import ABC, abstractmethod

class TypePerson(Enum):
    BOT = 'bot'
    PERSON = 'person'
    INFLUENCER = 'influencer'


class GeneratorNameInterface(ABC):

    def __init__(self):
        self.faker = Faker()

    @abstractmethod
    def generate_name(self):
        pass


class GeneratorNamePerson(GeneratorNameInterface):
    AGES = [str(i) for i in range(80, 100)] + ['0' + str(i) for i in range(0, 10)]

    def generate_name(self):
        name = self.faker.first_name()
        if random.choice([True, False]):
            name = name + random.choice(self.AGES)
        return name



class GeneratorNameBot(GeneratorNameInterface):

    def generate_name(self):
        name = self.faker.first_name()
        if random.choice([True, False]):
            name = name + str(random.randint(0, 1000))
        return name


class GeneratorNameFactory:

    @classmethod
    def get_generator(cls, type_person: TypePerson) -> GeneratorNameInterface:
        if type_person == TypePerson.BOT:
            return GeneratorNameBot()
        elif type_person in [TypePerson.PERSON, TypePerson.INFLUENCER]:
            return GeneratorNamePerson()
        else:
            raise ValueError(f"Not exist this type: {type_person}")


class GeneratorPeople:


    def __init__(self, type_person: TypePerson, n_people: int, range_posts: tuple, n_followers: int,
                 n_following: int):
        self.type_person = type_person
        self.n_people = n_people
        self.range_posts = range_posts
        self.n_followers = n_followers
        self.n_following = n_following
        self.index = 0
        self.generator_names = GeneratorNameFactory.get_generator(self.type_person)

    def __iter__(self):
        return self

    def __next__(self) -> PersonSchema:
        if self.index >= self.n_people:
            raise StopIteration
        name = self.generator_names.generate_name()
        posts = random.randint(self.range_posts[0], self.range_posts[1])
        self.index += 1
        return PersonSchema(name=name, posts=posts, n_followers=self.n_followers, n_following=self.n_following,
                      user_type=self.type_person.value)


