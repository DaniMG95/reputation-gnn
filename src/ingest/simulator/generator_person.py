import random
from core.domain import PersonWithRelations, TypePerson
from ingest.simulator.generator import GeneratorInterface


class GeneratorPeople:


    def __init__(self, type_person: TypePerson, n_people: int, range_posts: tuple, n_followers: int,
                 n_following: int, generator: GeneratorInterface):
        self.type_person = type_person
        self.n_people = n_people
        self.range_posts = range_posts
        self.n_followers = n_followers
        self.n_following = n_following
        self.index = 0
        self.generator = generator

    def __iter__(self):
        return self

    def __next__(self) -> PersonWithRelations:
        if self.index >= self.n_people:
            raise StopIteration
        posts = random.randint(self.range_posts[0], self.range_posts[1])
        self.index += 1
        return PersonWithRelations(name=self.generator.name, posts=posts, n_followers=self.n_followers,
                                   n_following=self.n_following, user_type=self.type_person,
                                   verified=self.generator.verified)


