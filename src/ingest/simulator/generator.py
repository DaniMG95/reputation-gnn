from faker import Faker
import random
from core.domain import TypePerson
from abc import ABC, abstractmethod


class GeneratorInterface(ABC):

    def __init__(self, prohibited_names: list[str] = None):
        self.faker = Faker()
        self._prohibited_names = prohibited_names if prohibited_names else []
        self._names = []

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def verified(self):
        pass

    @property
    def names(self):
        return self._names[:]


class GeneratorPerson(GeneratorInterface):

    def __init__(self, percentage_verified: float = 0.5, prohibited_names: list[str] = None):
        super().__init__(prohibited_names=prohibited_names)
        self.percentage_verified = percentage_verified

    AGES = [str(i) for i in range(80, 100)] + ['0' + str(i) for i in range(0, 10)]

    @property
    def name(self):
        while True:
            name = self.faker.first_name()
            if random.choice([True, False]):
                name = name + random.choice(self.AGES)
            if name not in self._prohibited_names and name not in self._names:
                self._names.append(name)
                return name

    @property
    def verified(self):
        return random.choice([True, False])


class GeneratorBot(GeneratorInterface):

    @property
    def name(self):
        while True:
            name = self.faker.first_name()
            if random.choice([True, False]):
                name = name + str(random.randint(0, 1000))
            if name not in self._prohibited_names and name not in self._names:
                self._names.append(name)
                return name

    @property
    def verified(self):
        return False


class GeneratorInfluencer(GeneratorPerson):
    def __init__(self, prohibited_names: list[str] = None):
        super().__init__(prohibited_names=prohibited_names)

    @property
    def verified(self):
        return True


class GeneratorFactory:

    @classmethod
    def get_generator(cls, type_person: TypePerson, prohibited_names: list[str] = None, *args, **kwargs
                      ) -> GeneratorInterface:
        if type_person == TypePerson.BOT:
            return GeneratorBot(prohibited_names=prohibited_names)
        elif type_person == TypePerson.PERSON:
            return GeneratorPerson(prohibited_names=prohibited_names, *args, **kwargs)
        elif type_person == TypePerson.INFLUENCER:
            return GeneratorInfluencer(prohibited_names=prohibited_names)
        else:
            raise ValueError(f"Not exist this type: {type_person}")
