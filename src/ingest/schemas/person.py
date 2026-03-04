from dataclasses import dataclass, field

@dataclass
class PersonSchema:
    name: str
    user_type: str
    posts: int
    n_followers: int
    n_following: int
    followers: list["PersonSchema"] = field(default_factory=list)
    following: list["PersonSchema"] = field(default_factory=list)