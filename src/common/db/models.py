from neomodel import (StructuredNode, StringProperty, IntegerProperty, BooleanProperty,
                      UniqueIdProperty, RelationshipTo, RelationshipFrom)

class Person(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    user_type = StringProperty()
    posts = IntegerProperty()
    n_followers = IntegerProperty()
    n_following = IntegerProperty()
    verified = BooleanProperty()
    followers = RelationshipFrom('Person', 'FOLLOWS')
    following = RelationshipTo('Person', 'FOLLOWS')


