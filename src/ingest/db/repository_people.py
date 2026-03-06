from neomodel import db
from ingest.db.models import Person
from ingest.schemas.person import PersonSchema

class RepositoryPeople:

    @staticmethod
    def delete_all():
        db.cypher_query('MATCH (n:Person) DETACH DELETE n')

    @staticmethod
    def create_person(person: PersonSchema):
        Person(name=person.name, user_type=person.user_type, posts=person.posts, n_followers=person.n_followers,
               n_following=person.n_following).save()

    @staticmethod
    def _update_follows(person: PersonSchema):
        person_db = Person.nodes.get(name=person.name)
        person_db.n_following = len(person_db.following)
        person_db.n_followers = len(person_db.followers)
        person_db.save()

    def create_relationships(self, person: PersonSchema, followers: list[PersonSchema] = None,
                             following: list[PersonSchema] = None):
        person_db = Person.nodes.get(name=person.name)
        if followers:
            for follower in followers:
                follower_db = Person.nodes.get(name=follower.name)
                person_db.followers.connect(follower_db)
                self._update_follows(person=follower_db)
        if following:
            for follow in following:
                follow_db = Person.nodes.get(name=follow.name)
                person_db.following.connect(follow_db)
                self._update_follows(person=follow_db)
        person_db.n_following = len(person_db.following)
        person_db.n_followers = len(person_db.followers)
        person_db.save()

    @staticmethod
    def _transform_to_schema(person_db: Person) -> PersonSchema:
        person = PersonSchema(name=person_db.name, user_type=person_db.user_type, posts=person_db.posts,
                        n_followers=person_db.n_followers, n_following=person_db.n_following)
        person.followers = [PersonSchema(name=follower.name, user_type=follower.user_type, posts=follower.posts,
                                   n_followers=follower.n_followers, n_following=follower.n_following)
                            for follower in person_db.followers]
        person.following = [PersonSchema(name=follow.name, user_type=follow.user_type, posts=follow.posts,
                                   n_followers=follow.n_followers, n_following=follow.n_following)
                            for follow in person_db.following]
        return person


    @classmethod
    def get_person(cls, name: str) -> PersonSchema:
        person_db = Person.nodes.get(name=name)
        return cls._transform_to_schema(person_db)

    @classmethod
    def get_persons_by_type(cls, user_type: str) -> list[PersonSchema]:
        persons_db = Person.nodes.filter(user_type=user_type)
        return [cls._transform_to_schema(person_db)
                for person_db in persons_db]

    @classmethod
    def get_all_persons(cls) -> list[PersonSchema]:
        persons_db = Person.nodes.all()
        return [cls._transform_to_schema(person_db)
                for person_db in persons_db]

    @classmethod
    def update_person(cls, person: PersonSchema):
        person_db = Person.nodes.get(name=person.name)
        person_db.posts = person.posts
        person_db.n_followers = person.n_followers
        person_db.n_following = person.n_following
        person_db.user_type = person.user_type
        person_db.save()