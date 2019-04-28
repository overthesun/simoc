import datetime,json

from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import generate_password_hash, check_password_hash

from simoc_server import db

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_graphql import GraphQLView
from simoc_server import app

class BaseEntity(db.Model):
    __abstract__ = True  # Prevent sql alchemy from creating a table for BaseEntity

    @declared_attr
    def date_created(cls):
        # work around to move columns to end of table
        return db.Column(db.DateTime, server_default=db.func.now())

    @declared_attr
    def date_modified(cls):
        # work around to move columns to end of table
        return db.Column(db.DateTime, server_default=db.func.now(),
                         server_onupdate=db.func.now())


class User(BaseEntity, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


class BaseAttribute(BaseEntity):
    # Base attribute, used to store generic information in string
    # format along with type data for conversion
    __abstract__ = True

    @declared_attr
    def name(cls):
        return db.Column(db.String(128), nullable=False)

    @declared_attr
    def value(cls):
        return db.Column(db.String(512))

    @declared_attr
    def value_type(cls):
        return db.Column(db.String(80))


class DescriptiveAttribute(BaseAttribute):
    # Extends base attribute by adding unit and description as columns
    __abstract__ = True

    @declared_attr
    def details(cls):
        return db.Column(db.String(128), nullable=True)

    @declared_attr
    def description(cls):
        return db.Column(db.String(512), nullable=True)

    @declared_attr
    def growth(cls):
        return db.Column(db.Integer, nullable=True)


class AgentModelParam(DescriptiveAttribute):
    id = db.Column(db.Integer, primary_key=True)


class AgentType(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    agent_class = db.Column(db.String(80), nullable=False, unique=False)

#graphene definitions
class AgentTypeObject(SQLAlchemyObjectType):
    class Meta:
        model =AgentType
#        filter_fields = ["name","agent_class","id"]
        interfaces = (graphene.relay.Node,)

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    agent_type = graphene.relay.Node.Field(AgentTypeObject)
#    agent_type = graphene.Field(AgentTypeObject,filters=graphene.Argument(graphene.Filters,default_value={}))
#    agent_class=graphene.String()
    all_agent_types = SQLAlchemyConnectionField(AgentTypeObject)
    energy = graphene.String(agentName=graphene.String())
#    energy = graphene.String(agent_name = graphene.String())

#    def resolve_agent_type(self,args,context,info):
#        print ("CONTEXT",context)
#        query = AgentTypeObject.get_query(context)
#        return query.get(args.get("agentClass"))

    def resolve_energy(self,info,**args):
        '''
        Sends front end energy values for config wizard.
        Takes in the request values "agent_name" and "quantity"
        
        Returns
        -------
        json object with energy value for agent
        '''
#        print ("HERE1")
        agent_name= args.get("agentName")
        agent_quantity = None
        
        attribute_name = "in_enrg_kwh"
        value_type = "energy_input"
        total = {}
        if not agent_quantity:
            agent_quantity = 1
        if agent_name == "eclss":
            total_eclss = 0
            for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentType.id == AgentTypeAttribute.agent_type_id).filter(AgentTypeAttribute.name == "in_enrg_kwh").filter(AgentType.agent_class == "eclss").all():
                total_eclss += float(agent.AgentTypeAttribute.value)
            value = total_eclss * agent_quantity
            total = {value_type : value}
        else:
            if agent_name == "solar_pv_array_mars":
                attribute_name = "out_enrg_kwh"
                value_type = "energy_output"
            elif agent_name == "power_storage":
                attribute_name = "char_capacity_enrg_kwh"
                value_type = "energy_capacity"
            for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentType.id == AgentTypeAttribute.agent_type_id).filter(AgentTypeAttribute.name == attribute_name).all():
                if agent.AgentType.name == agent_name:
                    value = float(agent.AgentTypeAttribute.value) * agent_quantity
                    total = { value_type : value}
        return json.dumps(total)
        


    #may be able to take json as input. so can specify quantity with get_energy. 
#    some_func = Field(SomeObjectType, args={'value': graphene.List(graphene.String)})

schema = graphene.Schema(query=Query)

#route to check out graphene interface
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)


class AgentTypeAttribute(DescriptiveAttribute):
    id = db.Column(db.Integer, primary_key=True)
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), index=True,
                              nullable=False)
    agent_type = db.relationship("AgentType",
                                 backref=db.backref("agent_type_attributes", lazy=False,
                                                    cascade="all, delete-orphan"))


class AgentState(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_model_state_id = db.Column(db.Integer, db.ForeignKey("agent_model_state.id"),
                                     nullable=False, index=True)
    agent_model_state = db.relationship("AgentModelState",
                                        backref=db.backref("agent_states", lazy=False,
                                                           cascade="all, delete-orphan"))
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"),
                              nullable=False)
    agent_type = db.relationship("AgentType")
    agent_unique_id = db.Column(db.String(120), nullable=False)
    model_time_created = db.Column(db.Interval(), nullable=False)
    agent_id = db.Column(db.Integer, nullable=True)
    active = db.Column(db.String(120), nullable=True)
    age = db.Column(db.Float, nullable=True)
    amount = db.Column(db.Integer, nullable=True)
    lifetime = db.Column(db.Integer, nullable=True)
    connections = db.Column(db.String(1000), nullable=True)
    buffer = db.Column(db.String(1000), nullable=True)
    deprive = db.Column(db.String(1000), nullable=True)
    attributes = db.Column(db.String(1000), nullable=False)


class AgentStateAttribute(BaseAttribute):
    id = db.Column(db.Integer, primary_key=True)
    agent_state_id = db.Column(db.Integer, db.ForeignKey("agent_state.id"), nullable=False,
                               index=True)
    agent_state = db.relationship("AgentState",
                                  backref=db.backref("agent_state_attributes", lazy=False,
                                                     cascade="all, delete-orphan"))


class AgentModelState(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    step_num = db.Column(db.Integer, nullable=False)
    grid_width = db.Column(db.Integer, nullable=False)
    grid_height = db.Column(db.Integer, nullable=False)
    model_time = db.Column(db.Interval, nullable=False)
    seed = db.Column(db.BigInteger, nullable=False)
    random_state = db.Column(db.PickleType, nullable=False)
    termination = db.Column(db.String(300), nullable=False)
    priorities = db.Column(db.String(300), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    minutes_per_step = db.Column(db.Integer, nullable=False)
    config = db.Column(db.String(300), nullable=False)
    logging = db.Column(db.String(300), nullable=False)
    logs = db.Column(db.String(1000), nullable=False)


class AgentModelSnapshot(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_model_state_id = db.Column(db.Integer, db.ForeignKey("agent_model_state.id"))
    agent_model_state = db.relationship("AgentModelState",
                                        backref=db.backref("agent_model_snapshot", uselist=False))
    snapshot_branch_id = db.Column(db.Integer, db.ForeignKey("snapshot_branch.id"))
    snapshot_branch = db.relationship("SnapshotBranch",
                                      backref=db.backref("agent_model_snapshots", lazy=True))


class SnapshotBranch(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, nullable=False)
    __mapper_args__ = {
        "version_id_col": version_id
    }
    parent_branch_id = db.Column(db.Integer, db.ForeignKey("snapshot_branch.id"))
    parent_branch = db.relationship("SnapshotBranch", backref=db.backref("child_branches"),
                                    remote_side=[id])

    def get_root_branch(self):
        node = self
        while node.parent_branch is not None:
            node = node.parent_branch
        return node


class SavedGame(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), default=lambda: str(datetime.datetime.utcnow()))
    agent_model_snapshot_id = db.Column(db.Integer, db.ForeignKey("agent_model_snapshot.id"))
    agent_model_snapshot = db.relationship("AgentModelSnapshot")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")
