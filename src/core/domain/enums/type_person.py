from enum import Enum


class TypePerson(str, Enum):
    BOT = 'bot'
    PERSON = 'person'
    INFLUENCER = 'influencer'
