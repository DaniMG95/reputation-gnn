from dataclasses import dataclass
from core.domain.enums.type_person import TypePerson


@dataclass
class PersonPredict:
    name: str
    user_type: TypePerson
    confidence: float