from dataclasses import dataclass, field
from enum import Enum

class TypePerson(str, Enum):
    BOT = 'bot'
    PERSON = 'person'
    INFLUENCER = 'influencer'

    @staticmethod
    def transform_to_user_type(user_type_int: int) -> "TypePerson":
        return TypePerson.BOT if user_type_int == 0 else TypePerson.PERSON

    @staticmethod
    def transform_to_int(user_type: "TypePerson") -> int:
        return 0 if user_type == TypePerson.BOT else 1


@dataclass
class PersonBase:
    name: str
    user_type: TypePerson
    posts: int
    n_followers: int
    n_following: int
    verified: bool

    @property
    def attributes(self) -> list[float]:
        return [self.n_followers, self.n_following, self.posts, self.verified]

    @classmethod
    def from_schema(cls, person_schema: "PersonSchema") -> "PersonBase":
        return cls(name=person_schema.name, user_type=person_schema.user_type, posts=person_schema.posts,
                   n_followers=person_schema.n_followers, n_following=person_schema.n_following,
                   verified=person_schema.verified)

    @property
    def user_type_int(self) -> int:
        return TypePerson.transform_to_int(self.user_type)


@dataclass
class PersonSchema(PersonBase):
    followers: list["PersonBase"] = field(default_factory=list)
    following: list["PersonBase"] = field(default_factory=list)


@dataclass
class PersonPredict:
    name: str
    user_type: TypePerson
    confidence: float