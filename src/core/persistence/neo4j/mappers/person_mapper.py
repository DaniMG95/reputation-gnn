from core.domain import TypePerson, Person
from core.persistence.neo4j.models.person_node import Person as PersonNode


class PersonModelMapper:
    @staticmethod
    def to_domain(node: PersonNode) -> Person:
        return Person(
            name=node.name,
            verified=node.verified,
            posts=node.posts,
            n_followers=node.n_followers,
            n_following=node.n_following,
            user_type=TypePerson(node.user_type) if node.user_type else None,
        )