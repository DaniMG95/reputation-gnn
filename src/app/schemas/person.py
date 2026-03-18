from pydantic import BaseModel
from pydantic.fields import Field
from common.schemas.person import PersonSchema, TypePerson


class PredictRequestPerson(BaseModel, PersonSchema):
    followers_db: list[str] = Field(default_factory=list)
    following_db: list[str] = Field(default_factory=list)

class CreatePersonRequest(BaseModel):
    name: str
    user_type: TypePerson
    posts: int
    n_followers: int
    n_following: int
    verified: bool
    followers: list[str] = Field(default_factory=list)
    following: list[str] = Field(default_factory=list)
