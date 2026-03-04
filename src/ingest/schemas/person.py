from dataclasses import dataclass, field

@dataclass
class Person:
    name: str
    label: str
    posts: int
    n_followers: int
    n_following: int
    followers: list["Person"] = field(default_factory=list)
    following: list["Person"] = field(default_factory=list)