from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo)

class Person(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    user_type = StringProperty()
    posts = IntegerProperty()
    n_followers = IntegerProperty()
    n_following = IntegerProperty()
    followers = RelationshipTo('Person', 'FOLLOWED_BY')
    following = RelationshipTo('Person', 'FOLLOWS')


