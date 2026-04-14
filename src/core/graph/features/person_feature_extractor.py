from core.domain.entities.person import Person

class PersonFeatureExtractor:

    @staticmethod
    def extract(person: Person) -> list[float]:
        return [
            float(person.n_followers),
            float(person.n_following),
            float(person.posts),
            1.0 if person.verified else 0.0,
        ]