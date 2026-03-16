from dataclasses import dataclass, field
from enum import Enum

class TypePerson(str, Enum):
    BOT = 'bot'
    PERSON = 'person'
    INFLUENCER = 'influencer'


@dataclass
class PersonSchema:
    name: str
    user_type: TypePerson
    posts: int
    n_followers: int
    n_following: int
    verified: bool
    followers: list["PersonSchema"] = field(default_factory=list)
    following: list["PersonSchema"] = field(default_factory=list)

    @property
    def attributes(self) -> list[float]:
        return [self.n_followers, self.n_following, self.posts, self.verified]

@dataclass
class PersonPredict:
    name: str
    user_type: TypePerson
    confidence: float