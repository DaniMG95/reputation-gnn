from core.persistence.neo4j.models.person_node import Person as PersonModel
from core.domain.entities.person import PersonWithRelations
from core.domain.enums.type_person import TypePerson
from core.persistence.interfaces.repository_interfaces import RepositoryPeopleInterface
from core.observability.logger import Logger
from core.persistence.neo4j.mappers.person_mapper import PersonModelMapper

class RepositoryPeopleNeo4j(RepositoryPeopleInterface):

    def __init__(self, db):
        self.db = db
        self.logger = Logger(name="common.RepositoryPeopleNeo4j")

    def delete_all(self):
        self.logger.debug("Deleting all persons from the database.")
        self.db.cypher_query('MATCH (n:Person) DETACH DELETE n')

    def create_person(self, person: PersonWithRelations):
        self.logger.debug("Creating person with name '%s' in the database.", person.name)
        PersonModel(name=person.name, user_type=person.user_type.value, posts=person.posts,
                    n_followers=person.n_followers, n_following=person.n_following, verified=person.verified).save()

    def _get_person_db(self, name: str) -> PersonModel | None:
        try:
            return PersonModel.nodes.get(name=name)
        except PersonModel.DoesNotExist:
            self.logger.warning(f"Person with name {name} not found in database.")
            return None

    @staticmethod
    def _update_follows(person: PersonModel):
        person_db = PersonModel.nodes.get(name=person.name)
        person_db.n_following = len(person_db.following)
        person_db.n_followers = len(person_db.followers)
        person_db.save()

    def update_relationships(self, person: PersonWithRelations, followers: list[str] = None, following: list[str] = None):
        self.logger.debug(f"Updating relationships for person '{person.name}' with followers: {followers} and "
                          f"following: {following}")
        person_db = self._get_person_db(name=person.name)
        followers_needs = None
        following_needs = None
        if not person_db:
            self.logger.warning("Person with name '{person.name}' not found in database. Cannot update relationships.")
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

    def create_relationships(self, person: PersonWithRelations, followers: list[str] = None,
                             following: list[str] = None):
        self.logger.debug(f"Creating relationships for person '{person.name}' with followers: "
                          f"{followers} and following: {following}")
        person_db = self._get_person_db(name=person.name)
        if not person_db:
            self.logger.warning(f"Person with name '{person.name}' not found in database. Cannot create relationships.")
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

    def _transform_to_relationships(self, person_db: PersonModel) -> PersonWithRelations:
        person = PersonWithRelations(name=person_db.name, user_type=TypePerson(person_db.user_type), posts=person_db.posts,
                              n_followers=person_db.n_followers, n_following=person_db.n_following,
                              verified=person_db.verified)
        person.followers = [PersonModelMapper.to_domain(follower) for follower in person_db.followers]
        person.following = [PersonModelMapper.to_domain(follow) for follow in person_db.following]
        return person

    def get_person(self, name: str) -> PersonWithRelations | None:
        self.logger.debug(f"Getting person with name '{name}' from the database.")
        person_db = self._get_person_db(name=name)
        if not person_db:
            self.logger.warning(f"Person with name '{name}' not found in database.")
            return None
        return self._transform_to_relationships(person_db)

    def get_persons_by_type(self, user_type: TypePerson) -> list[PersonWithRelations]:
        self.logger.debug(f"Getting persons by type '{user_type.value}' from the database.")
        persons_db = PersonModel.nodes.filter(user_type=user_type.value)
        return [self._transform_to_relationships(person_db) for person_db in persons_db]

    def get_persons_by_pagination(self, skip: int = 0, limit: int = 10, type_person: TypePerson = None
                                  ) -> list[PersonWithRelations]:
        self.logger.debug(f"Getting persons by pagination with skip={skip}, limit={limit}, type_person={type_person}")
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
        return [self._transform_to_relationships(PersonModel.inflate(row[0])) for row in results]

    def get_all_persons(self) -> list[PersonWithRelations]:
        self.logger.debug("Getting all persons from the database.")
        persons_db = PersonModel.nodes.all()
        return [self._transform_to_relationships(person_db)
                for person_db in persons_db]

    def update_person(self, person: PersonWithRelations):
        person_db = PersonModel.nodes.get(name=person.name)
        person_db.posts = person.posts
        person_db.user_type = person.user_type.value
        person_db.verified = person.verified
        person_db.save()

    def get_persons_by_names(self, names: list[str]) -> list[PersonWithRelations]:
        self.logger.debug(f"Getting persons by names: {names}")
        return [person for name in names if (person := self.get_person(name)) is not None]

    def get_neighborhoods(self, names: list[str], limit: int = 50) -> list[PersonWithRelations]:
        self.logger.debug("Getting neighborhoods for names: %s with limit: %d", names, limit)
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
            root = PersonModel.inflate(row[0])
            following_list = [PersonModel.inflate(follow) for follow in row[1]]
            followers_list = [PersonModel.inflate(follower) for follower in row[2]]

            root_schema = PersonWithRelations(
                name=root.name,
                user_type=TypePerson(root.user_type),
                posts=root.posts,
                n_followers=root.n_followers,
                n_following=root.n_following,
                verified=root.verified
            )

            root_schema.following = [PersonModelMapper.to_domain(follow) for follow in following_list]
            root_schema.followers = [PersonModelMapper.to_domain(follow) for follow in followers_list]

            final_list.append(root_schema)

        return final_list

    def get_random_nodes(self, n: int) -> list[PersonWithRelations]:
        self.logger.debug("Getting random nodes from the database.")
        query = f"""
        MATCH (p:Person)
        RETURN p, rand() as r
        ORDER BY r
        LIMIT {n}
        """
        results, _ = self.db.cypher_query(query)
        if results:
            return [self._transform_to_relationships(PersonModel.inflate(row[0])) for row in results]
        return []

    def delete_person(self, name: str):
        self.logger.debug(f"Deleting person with name '{name}' from database.")
        person_db = PersonModel.nodes.get(name=name)
        if person_db:
            person_db.delete()
        else:
            self.logger.warning(f"Person with name '{name}' not found in database. Cannot delete.")
            raise ValueError(f"Person with name '{name}' not found in database.")

    def ping(self) -> bool:
        self.logger.debug("Pinging Neo4j database.")
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
        self.logger.debug("Counting the number of persons in the database.")
        query = "MATCH (p:Person) RETURN count(p) AS count"
        results, _ = self.db.cypher_query(query)
        return results[0][0] if results else 0

    def get_all_labeled_names(self) -> list[str]:
        self.logger.debug("Getting all labeled names from the database.")
        query = """
        MATCH (p:Person)
        RETURN p.name AS name
        """
        results, _ = self.db.cypher_query(query)
        return [record[0] for record in results]