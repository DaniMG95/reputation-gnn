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
    followers: list["PersonSchema"] = field(default_factory=list)
    following: list["PersonSchema"] = field(default_factory=list)