from common.db.models import Person
from common.schemas.person import PersonSchema, TypePerson, PersonBase
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
    def _get_person_db(name: str) -> Person | None:
        try:
            return Person.nodes.get(name=name)
        except Person.DoesNotExist:
            return None

    @staticmethod
    def _update_follows(person: Person):
        person_db = Person.nodes.get(name=person.name)
        person_db.n_following = len(person_db.following)
        person_db.n_followers = len(person_db.followers)
        person_db.save()

    def update_relationships(self, person: PersonSchema, followers: list[str] = None, following: list[str] = None):
        person_db = self._get_person_db(name=person.name)
        followers_needs = None
        following_needs = None
        if not person_db:
            raise ValueError(f"Person with name '{person.name}' not found in database.")
        if followers:
            followers_needs = followers[:]
            for follower in person_db.followers:
                if follower.name not in followers_needs:
                    person_db.followers.disconnect(follower)
                else:
                    followers_needs.remove(follower.name)
        if following:
            following_needs = following[:]
            for follow in person_db.following:
                if follow.name not in following_needs:
                    person_db.following.disconnect(follow)
                else:
                    following_needs.remove(follow.name)
        person_db.save()
        self.create_relationships(person=person, followers=followers_needs, following=following_needs)

    def create_relationships(self, person: PersonSchema, followers: list[str] = None,
                             following: list[str] = None):
        person_db = self._get_person_db(name=person.name)
        if not person_db:
            raise ValueError(f"Person with name '{person.name}' not found in database.")
        if followers:
            for follower in followers:
                follower_db = self._get_person_db(name=follower)
                if follower_db:
                    person_db.followers.connect(follower_db)
                    self._update_follows(person=follower_db)
                else:
                    self.logger.warning(f"Follower with name '{follower}' not found in database. Skipping connection.")
        if following:
            for follow in following:
                follow_db = self._get_person_db(name=follow)
                if follow_db:
                    person_db.following.connect(follow_db)
                    self._update_follows(person=follow_db)
                else:
                    self.logger.warning(f"Following with name '{follow}' not found in database. Skipping connection.")
        person_db.n_following = len(person_db.following)
        person_db.n_followers = len(person_db.followers)
        person_db.save()

    def _transform_to_schema(self, person_db: Person) -> PersonSchema:
        person = PersonSchema(name=person_db.name, user_type=TypePerson(person_db.user_type), posts=person_db.posts,
                              n_followers=person_db.n_followers, n_following=person_db.n_following,
                              verified=person_db.verified)
        person.followers = [self._to_base(follower) for follower in person_db.followers]
        person.following = [self._to_base(follow) for follow in person_db.following]
        return person

    @staticmethod
    def _to_base(node_db: Person) -> PersonBase:
        return PersonBase(
            name=node_db.name,
            user_type=TypePerson(node_db.user_type),
            posts=node_db.posts,
            n_followers=node_db.n_followers,
            n_following=node_db.n_following,
            verified=node_db.verified
        )

    def get_person(self, name: str) -> PersonSchema | None:
        person_db = self._get_person_db(name=name)
        if not person_db:
            return None
        return self._transform_to_schema(person_db)

    def get_persons_by_type(self, user_type: TypePerson) -> list[PersonSchema]:
        persons_db = Person.nodes.filter(user_type=user_type.value)
        return [self._transform_to_schema(person_db) for person_db in persons_db]

    def get_persons_by_pagination(self, skip: int = 0, limit: int = 10, type_person: TypePerson = None
                                  ) -> list[PersonSchema]:

        conditional = f"WHERE p.user_type = '{type_person.value}'" if type_person else ""
        query = f"""
        MATCH (p:Person)
        {conditional}
        RETURN p
        ORDER BY p.name ASC
        SKIP {skip}
        LIMIT {limit}
        """
        results, _ = self.db.cypher_query(query)
        return [self._transform_to_schema(Person.inflate(row[0])) for row in results]

    def get_all_persons(self) -> list[PersonSchema]:
        persons_db = Person.nodes.all()
        return [self._transform_to_schema(person_db)
                for person_db in persons_db]

    def update_person(self, person: PersonSchema):
        person_db = Person.nodes.get(name=person.name)
        person_db.posts = person.posts
        person_db.user_type = person.user_type.value
        person_db.verified = person.verified
        person_db.save()

    def get_persons_by_names(self, names: list[str]) -> list[PersonSchema]:
        return [person for name in names if (person := self.get_person(name)) is not None]

    def get_neighborhoods(self, names: list[str], limit: int = 50) -> list[PersonSchema]:
        query = f"""
            UNWIND $names_list AS name
            CALL (name){{
                MATCH (p:Person {{name: name}})
                
                OPTIONAL MATCH (p)-[:FOLLOWS]->(fg)
                WITH p, fg ORDER BY rand()
                WITH p, collect(DISTINCT fg)[0..{limit}] AS following_list
                
                OPTIONAL MATCH (p)<-[:FOLLOWS*1]-(fr)
                WITH p, following_list, fr ORDER BY rand()
                WITH p, following_list, collect(DISTINCT fr)[0..{limit}] AS followers_list
                
                RETURN p AS root, following_list, followers_list
            }}
            RETURN root, following_list, followers_list 
        """
        results, _ = self.db.cypher_query(query, {'names_list': names})

        final_list = []
        for row in results:
            root = Person.inflate(row[0])
            following_list = [Person.inflate(follow) for follow in row[1]]
            followers_list = [Person.inflate(follower) for follower in row[2]]

            root_schema = PersonSchema(
                name=root.name,
                user_type=TypePerson(root.user_type),
                posts=root.posts,
                n_followers=root.n_followers,
                n_following=root.n_following,
                verified=root.verified
            )

            root_schema.following = [self._to_base(follow) for follow in following_list]
            root_schema.followers = [self._to_base(follow) for follow in followers_list]

            final_list.append(root_schema)

        return final_list

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

    def count_persons(self) -> int:
        query = "MATCH (p:Person) RETURN count(p) AS count"
        results, _ = self.db.cypher_query(query)
        return results[0][0] if results else 0