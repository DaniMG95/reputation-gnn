from common.db.models import Person
from common.schemas.person import PersonSchema, TypePerson
from common.db.interfaces import RepositoryPeopleInterface
from common.logger import LoggerIngest

class RepositoryPeopleNeo4j(RepositoryPeopleInterface):

    def __init__(self, db):
        self.db = db
        self.logger = LoggerIngest(name="common.RepositoryPeopleNeo4j")

    def delete_all(self):
        self.db.cypher_query('MATCH (n:Person) DETACH DELETE n')

    def create_person(self, person: PersonSchema):
        Person(name=person.name, user_type=person.user_type.value, posts=person.posts, n_followers=person.n_followers,
               n_following=person.n_following, verified=person.verified).save()

    @staticmethod
    def _update_follows(person: PersonSchema):
        person_db = Person.nodes.get(name=person.name)
        person_db.n_following = len(person_db.following)
        person_db.n_followers = len(person_db.followers)
        person_db.save()

    def create_relationships(self, person: PersonSchema, followers: list[str] = None,
                             following: list[str] = None):
        person_db = Person.nodes.get(name=person.name)
        if followers:
            for follower in followers:
                follower_db = Person.nodes.get(name=follower)
                if follower_db:
                    person_db.followers.connect(follower_db)
                    self._update_follows(person=follower_db)
                else:
                    self.logger.warning("Follower with name '{follower.name}' not found in database. Skipping connection.")
        if following:
            for follow in following:
                follow_db = Person.nodes.get(name=follow)
                if follow_db:
                    person_db.following.connect(follow_db)
                    self._update_follows(person=follow_db)
                else:
                    self.logger.warning("Following with name '{follow.name}' not found in database. Skipping connection.")
        person_db.n_following = len(person_db.following)
        person_db.n_followers = len(person_db.followers)
        person_db.save()

    @staticmethod
    def _transform_to_schema(person_db: Person) -> PersonSchema:
        person = PersonSchema(name=person_db.name, user_type=TypePerson(person_db.user_type), posts=person_db.posts,
                              n_followers=person_db.n_followers, n_following=person_db.n_following,
                              verified=person_db.verified)
        person.followers = [PersonSchema(name=follower.name, user_type=TypePerson(follower.user_type),
                                         posts=follower.posts, n_followers=follower.n_followers,
                                         n_following=follower.n_following, verified=follower.verified)
                            for follower in person_db.followers]
        person.following = [PersonSchema(name=follow.name, user_type=TypePerson(follow.user_type), posts=follow.posts,
                                         n_followers=follow.n_followers, n_following=follow.n_following,
                                         verified=follow.verified)
                            for follow in person_db.following]
        return person


    def get_person(self, name: str) -> PersonSchema | None:
        try:
            person_db = Person.nodes.get(name=name)
        except Person.DoesNotExist:
            return None
        return self._transform_to_schema(person_db)

    def get_persons_by_type(self, user_type: TypePerson) -> list[PersonSchema]:
        persons_db = Person.nodes.filter(user_type=user_type.value)
        return [self._transform_to_schema(person_db)
                for person_db in persons_db]

    def get_all_persons(self) -> list[PersonSchema]:
        persons_db = Person.nodes.all()
        return [self._transform_to_schema(person_db)
                for person_db in persons_db]

    def update_person(self, person: PersonSchema):
        person_db = Person.nodes.get(name=person.name)
        person_db.posts = person.posts
        person_db.n_followers = person.n_followers
        person_db.n_following = person.n_following
        person_db.user_type = person.user_type.value
        person_db.verified = person.verified
        person_db.save()

    def get_persons_by_names(self, names: list[str]) -> list[PersonSchema]:
        return [person for name in names if (person := self.get_person(name)) is not None]

    def get_neighborhoods(self, names: list[str], hops: int = 1) -> list[PersonSchema]:
        query = f"""
                MATCH (p:Person)
                WHERE p.name IN $names_list
                MATCH (p)-[:FOLLOWS*0..{hops}]-(neighbors)
                RETURN DISTINCT neighbors
                """
        results, _ = self.db.cypher_query(query, {'names_list': names})
        return [self._transform_to_schema(Person.inflate(row[0])) for row in results]

    def get_random_nodes(self, n: int) -> list[PersonSchema]:
        query = f"""
        MATCH (p:Person)
        RETURN p, rand() as r
        ORDER BY r
        LIMIT {n}
        """
        results, _ = self.db.cypher_query(query)
        if results:
            return [self._transform_to_schema(Person.inflate(row[0])) for row in results]
        return []

    def delete_person(self, name: str):
        person_db = Person.nodes.get(name=name)
        if person_db:
            person_db.delete()
        else:
            raise ValueError(f"Person with name '{name}' not found in database.")

    def ping(self) -> bool:
        try:
            self.db.cypher_query("RETURN 1")
            return True
        except Exception as e:
            self.logger.error(f"Error pinging Neo4j database: {e}")
            return False

    @property
    def name(self) -> str:
        return "Neo4j"