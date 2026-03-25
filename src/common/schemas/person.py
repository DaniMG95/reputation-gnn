from dataclasses import dataclass, field
from enum import Enum

class TypePerson(str, Enum):
    BOT = 'bot'
    PERSON = 'person'
    INFLUENCER = 'influencer'


@dataclass
class PersonBase:
    name: str
    user_type: TypePerson
    posts: int
    n_followers: int
    n_following: int
    verified: bool

    def attributes(self) -> list[float]:
        return [self.n_followers, self.n_following, self.posts, self.verified]



@dataclass
class PersonSchema(PersonBase):
    followers: list["PersonBase"] = field(default_factory=list)
    following: list["PersonBase"] = field(default_factory=list)


@dataclass
class PersonPredict:
    name: str
    user_type: TypePerson
    confidence: float