from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo)
import ingest.db.connection

class Person(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    label = StringProperty()
    posts = IntegerProperty()
    n_followers = IntegerProperty()
    n_following = IntegerProperty()
    followers = RelationshipTo('Person', 'FOLLOWED_BY')
    following = RelationshipTo('Person', 'FOLLOWS')


