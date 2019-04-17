import json
import math

from flask import request

#from simoc_server import app, db
#from simoc_server.database.db_model import AgentType, AgentTypeAttribute

import graphene as gp

'''
In this file, some routes which exist in views.py are rewritten using graphene/graphQL to see if it simplifies things

For testing, classes which were previously defined in db_model.py are redefined here using graphene

'''

class AgentType(gp.ObjectType):
    id = gp.Int()
    name = gp.String()
    agent_class = gp.String(name="agent_class")

class AgentTypeAttribute(DescriptiveAttribute):
    id = gp.Int()
    #FIXME: to be convertred to graphene
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), index=True,
                              nullable=False)
    agent_type = db.relationship("AgentType",
                                 backref=db.backref("agent_type_attributes", lazy=False,
                                                    cascade="all, delete-orphan"))

class Query(gp.ObjectType):
    
    agent_type = gp.Field(AgentType)
    
    def resolve_agent_type(self,info):
        return AgentType()

schema = gp.Schema(query=Query)

#/get_agent_types?agent_class=plants&agent_name=none                                                                   
#def get_agent_types_by_class():
def get_agent_types():
    args, results = {}, []
    agent_class = request.args.get("agent_class", type=str)
    agent_name = request.args.get("agent_name", type=str)
    if agent_class:
        args["agent_class"] = agent_class
    if agent_name:
        args["name"] = agent_name
    
    #Step 1: want to use graphene to get agent, TBD: filter by class and naem
    result = schema.execute(query)
    #if I understand correctly, this will return all agent objects. 

    #step2: get attributes for all returned agents, check if I can avoid loops and have graphene return
    # required info directly
##%    for agent in AgentType.query.filter_by(**args).all():
##%        entry = {"agent_class": agent.agent_class, "name": agent.name}
##%        for attr in agent.agent_type_attributes:
##%            prefix, currency = attr.name.split('_', 1)
##%            if prefix not in entry:
##%                entry[prefix] = []
##%            if prefix in ['in', 'out']:
##%                entry[prefix].append(currency)
##%            else:
##%                entry[prefix].append(
##%                    {"name": currency, "value": attr.value, "units": attr.details})
##%        results.append(entry)
    #FIXME: here is an example of the output which should be produced, for reference.
    results = 
    return json.dumps(results)
