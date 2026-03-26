from pydantic import BaseModel
from pydantic.fields import Field
from common.schemas.person import PersonSchema, TypePerson, PersonBase


class PersonPredict(BaseModel):
    name: str
    user_type: TypePerson
    confidence: float


class PredictRequestPerson(BaseModel, PersonSchema):
    followers_db: list[str] = Field(default_factory=list)
    following_db: list[str] = Field(default_factory=list)

class CreatePersonRequest(BaseModel):
    name: str
    user_type: TypePerson
    posts: int
    verified: bool
    followers: list[str] = Field(default_factory=list)
    following: list[str] = Field(default_factory=list)

class UpdatePersonRequest(BaseModel):
    user_type: TypePerson
    posts: int
    verified: bool
    followers: list[str] = Field(default_factory=list)
    following: list[str] = Field(default_factory=list)

class PersonResponseBase(BaseModel):
    name: str
    user_type: TypePerson
    posts: int
    n_followers: int
    n_following: int
    verified: bool

    @classmethod
    def from_person_schema(cls, person: PersonBase) -> "PersonResponseBase":
        return cls(
            name=person.name,
            user_type=person.user_type,
            posts=person.posts,
            n_followers=person.n_followers,
            n_following=person.n_following,
            verified=person.verified
        )


class PersonResponse(PersonResponseBase):
    followers: list["PersonResponseBase"] = Field(default_factory=list)
    following: list["PersonResponseBase"] = Field(default_factory=list)

    @classmethod
    def from_person_schema(cls, person: PersonSchema) -> "PersonResponse":
        return cls(
            name=person.name,
            user_type=person.user_type,
            posts=person.posts,
            n_followers=person.n_followers,
            n_following=person.n_following,
            verified=person.verified,
            followers=[PersonResponseBase.from_person_schema(follower) for follower in person.followers],
            following=[PersonResponseBase.from_person_schema(following) for following in person.following]
        )

class PaginationPersonResponse(BaseModel):
    total: int
    offset: int
    limit: int
    people: list[PersonResponse]