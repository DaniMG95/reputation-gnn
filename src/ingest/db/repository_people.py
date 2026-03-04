from neomodel import db
from ingest.db.models import Person as PersonDB
from ingest.schemas.person import Person

class RepositoryPeople:

    @staticmethod
    def delete_all():
        db.cypher_query('MATCH (n:Person) DETACH DELETE n')
        db.cypher_query("CALL apoc.schema.assert({}, {})")

    @staticmethod
    def create_person(person: Person):
        PersonDB(name=person.name, label=person.label, posts=person.posts, n_followers=person.n_followers,
               n_following=person.n_following).save()

    @staticmethod
    def create_relationships(person: Person, followers: list[Person] = None, following: list[Person] = None):
        person_db = PersonDB.nodes.get(name=person.name)
        if followers:
            for follower in followers:
                follower_db = PersonDB.nodes.get(name=follower.name)
                person_db.followers.connect(follower_db)
            person_db.n_followers = len(person_db.followers)
        if following:
            for follow in following:
                follow_db = PersonDB.nodes.get(name=follow.name)
                person_db.following.connect(follow_db)
            person_db.n_following = len(person_db.following)
        person_db.save()

    @staticmethod
    def _transform_to_schem(person_db: PersonDB) -> Person:
        person = Person(name=person_db.name, label=person_db.label, posts=person_db.posts,
                        n_followers=person_db.n_followers, n_following=person_db.n_following)
        person.followers = [Person(name=follower.name, label=follower.label, posts=follower.posts,
                                   n_followers=follower.n_followers, n_following=follower.n_following)
                            for follower in person_db.followers]
        person.following = [Person(name=follow.name, label=follow.label, posts=follow.posts,
                                   n_followers=follow.n_followers, n_following=follow.n_following)
                            for follow in person_db.following]
        return person


    @classmethod
    def get_person(cls, name: str) -> Person:
        person_db = PersonDB.nodes.get(name=name)
        return cls._transform_to_schem(person_db)

    @classmethod
    def get_persons_by_type(cls, label: str) -> list[Person]:
        persons_db = PersonDB.nodes.filter(label=label)
        return [cls.get_person(person_db.name)
                for person_db in persons_db]

    @classmethod
    def get_all_persons(cls) -> list[Person]:
        persons_db = PersonDB.nodes.all()
        return [cls._transform_to_schem(person_db)
                for person_db in persons_db]

    @classmethod
    def update_person(cls, person: Person):
        person_db = PersonDB.nodes.get(name=person.name)
        person_db.posts = person.posts
        person_db.n_followers = person.n_followers
        person_db.n_following = person.n_following
        person_db.save()