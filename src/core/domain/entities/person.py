from dataclasses import dataclass, field
from core.domain.enums.type_person import TypePerson


@dataclass
class Person:
    name: str
    user_type: TypePerson
    posts: int
    n_followers: int
    n_following: int
    verified: bool


@dataclass
class PersonWithRelations(Person):
    followers: list["Person"] = field(default_factory=list)
    following: list["Person"] = field(default_factory=list)

