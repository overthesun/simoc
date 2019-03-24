import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from simoc_server.database.db_model import AgentType, AgentTypeAttribute, SavedGame, User

class AgentTypeAttributeQL(SQLAlchemyObjectType):
    class Meta:
        model = AgentTypeAttribute
        interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    agent = graphene.Field(lambda: graphene.List(AgentTypeAttributeQL),
                           name=graphene.String())

    def resolve_agent(self, info, **kwargs):
        query = AgentTypeAttributeQL.get_query(info)
        if kwargs.get('name'):
            result = (query.filter(
                AgentTypeAttribute.name == kwargs.get('name')).all())
        else:
            result = query.all()
        return result

schema = graphene.Schema(query=Query, types=[AgentTypeAttributeQL])
