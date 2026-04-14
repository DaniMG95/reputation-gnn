from core.domain.enums.type_person import TypePerson

class PersonLabelEncoder:
    MAPPING = {
        TypePerson.BOT: 0,
        TypePerson.PERSON: 1,
        TypePerson.INFLUENCER: 1,
    }

    @classmethod
    def encode(cls, user_type: TypePerson) -> int:
        return cls.MAPPING[user_type]

    @classmethod
    def decode(cls, user_type_int: int) -> TypePerson:
        for key, value in cls.MAPPING.items():
            if value == user_type_int:
                return key
        raise ValueError(f"Invalid user type integer: {user_type_int}")