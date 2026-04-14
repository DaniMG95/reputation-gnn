from core.domain.entities.person import Person, PersonWithRelations

class PersonMapper:
    @staticmethod
    def schema_to_domain(person_schema: PersonWithRelations) -> Person:
        return Person(
            name=person_schema.name,
            user_type=person_schema.user_type,
            posts=person_schema.posts,
            n_followers=person_schema.n_followers,
            n_following=person_schema.n_following,
            verified=person_schema.verified,
        )