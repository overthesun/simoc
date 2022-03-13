====================
Getting Started
====================

Basic Case
==========

.. code-block:: python

    from agent_model import AgentModel
    import json

    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)

    model = AgentModel.from_config(config, data_collection=True)

    model.step_to(n_steps=601)

    data = model.get_data(debug=True)

Custom Agents
=============
To add custom agents, provide custom currency and agent description files
when initializing AgentModel.

.. code-block:: python

    currency_desc = {...}
    agent_desc = {...}
    agent_conn = {...}
    model = AgentModel.from_config(config, data_collection=True,
                                   currency_desc=currency_desc,
                                   agent_desc=agent_desc,
                                   agent_conn=agent_conn)

**Example**: Mushrooms

Target behavior:
* Consumes 10g o2 and 10g inedible_biomass per hour (sigmoid)
* Grow 20g per hour (normal)
* Lifetime of 30 days
* At end of lifetime, 90% edible (mushroom) 10% waste (mushroom_waste)

First, define two new currencies: food/mushroom, and nutrients/mushroom_waste.
Create a currency_desc object that mirrors the structure of the defualt
`currency_desc.json` file.

.. code-block:: python

    custom_currency_desc = {
        'food': {
                'label': 'Mushroom'
            }
        },
        'nutrients': {
            'mushroom_waste': {
                'label': 'Mushroom Waste'
            }
        }
    }

Next, add the new agent to an object hat mirrors the default `agent_desc.json`.

Also, add storage capacity for the new currencies. Existing agents can be
modified by mirroring their structure, and changing or adding specific fields.

.. code-block:: python

    agent_desc = {
        # Add a capacity to store these currencies in the appropriate agent
        'storage': {
            'food_storage': {
                'data': {
                    'characteristics': [
                        {
                            'type': 'capacity_mushroom',
                            'value': 1000,
                            'unit': 'kg'
                        }
                    ]
                }
            },
            'nutrient_storage': {
                'data': {
                    'characteristics': [
                        {
                            'type': 'capacity_mushroom_waste',
                            'value': 1000,
                            'unit': 'kg'
                        }
                    ]
                }
            }
        },
        'plants': {
            'mushroom': {
                'data': {
                    'input': [
                        {
                            'type': 'o2',
                            'value': 0.01,
                            'required': 'desired',
                            'flow_rate': {
                                'unit': 'kg',
                                'time': 'hour'
                            },
                            'growth': {
                                'lifetime': {
                                    'type': 'sigmoid'  # Value is 'reshaped' over lifetime
                                }
                            },
                            # If demand is unfulfilled for longer than this, agent dies.
                            'deprive':  {
                                'value': 72,
                                'unit': 'hour'
                            }
                        },
                        {
                            'type': 'inedible_biomass',
                            'value': 0.01,
                            'required': 'desired',
                            'flow_rate': {
                                'unit': 'kg',
                                'time': 'hour',
                            },
                            'growth': {
                                'lifetime': {
                                    'type': 'sigmoid'
                                }
                            },
                            'deprive': {
                                'value': 72,
                                'unit': 'hour'
                            }
                        },
                        {
                            'type': 'biomass',
                            'value': 1,
                            'weighted': 'current_growth',
                            'flow_rate': {
                                'unit': 'kg',
                                'time': 'hour',
                            },
                            'criteria': {
                                'name': 'grown',
                                'limit': '=',
                                'value': True
                            }
                        }
                    ],
                    'output': [
                        {
                            'type': 'biomass',
                            'value': 0.02,
                            'flow_rate': {
                                'unit': 'kg',
                                'time': 'hour'
                            },
                            'growth': {
                                'lifetime': {
                                    'type': 'norm'
                                }
                            }
                        },
                        {
                            'type': 'mushroom',
                            'value': 0.9,
                            'weighted': 'current_growth',
                            'flow_rate': {
                                'unit': 'kg',
                                'time': 'hour'
                            },
                            'criteria': {
                                'name': 'grown',
                                'limit': '=',
                                'value': True
                            }
                        },
                        {
                            'type': 'mushroom_waste',
                            'value': 0.1,
                            'weighted': 'current_growth',
                            'flow_rate': {
                                'unit': 'kg',
                                'time': 'hour'
                            },
                            'criteria': {
                                'name': 'grown',
                                'limit': '=',
                                'value': True
                            }
                        }
                    ],
                    'characteristics': [
                        {
                            'type': 'lifetime',
                            'value': 720,
                            'unit': 'hour'
                        },
                        {
                            'type': 'growth_criteria',
                            'value': 'out_biomass'
                        },
                        {
                            'type': 'capacity_biomass',
                            'value': 100,
                            'unit': 'kg'
                        }
                    ]
                }
            }
        }
    }

Then create a new agent_conn, mirroring the default `agent_conn.json`.

.. code-block:: python

    agent_conn = [
        {
            'from': 'greenhouse.o2',
            'to': 'mushroom.o2'
        },
        {
            'from': 'nutrient_storage.inedible_biomass',
            'to': 'mushroom.inedible_biomass'
        },
        {
            'from': 'mushroom.biomass',
            'to': 'mushroom.biomass'
        },
        {
            'from': 'mushroom.mushroom',
            'to': 'food_storage.mushroom',
        },
        {
            'from': 'mushroom.mushroom_waste',
            'to': 'nutrient_storage.mushroom_waste'
        }
    ]

Finally, add them to a new model.

.. code-block:: python

    from agent_model import AgentModel
    import json

    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)
    config['agents']['mushroom'] = {'amount': 10}
    config['agents']['nutrient_storage']['inedible_biomass'] = 200
    model = AgentModel.from_config(config,
                                data_collection=True,
                                currency_desc=currency_desc,
                                agent_desc=agent_desc,
                                connections=agent_conn)
    model.step_to(n_steps=721)
    data = model.get_data(debug=True)

Inspect A Group
===============
Plot all elements for one group with an agent.

Available groups vary by agent based on function, and may include: growth, storage, flows, deprive

.. code-block:: python

    import matplotlib.pyplot as plt

    def plot_group(group, exclude=[], i=None, j=None):
        plt.figure(figsize=(12,6))
        length = len(next(iter(group.values())))
        i = i if i else 0
        j = j if j else length-1
        steps = [i for i in range(j-i)]
        for currency, values in group.items():
            if sum(values) == 0 or currency in exclude:
                continue
            plt.plot(steps, values[i:j], label=currency)
        plt.legend()
        plt.show()

    plot_group(data['crew_habitat_small']['storage'], exclude=['n2', 'o2'])

Inspect a Currency
==================
Plot all flows of a particular currency

.. code-block:: python

    import matplotlib.pyplot as plt

    data = model.get_data(debug=True)
    def plot_currency(data, currency, exclude=[], i=None, j=None):
        flows = {}
        length = None
        for agent_name, agent_data in data.items():
            if 'flow_records' not in agent_data:
                continue
            for currency_name, currency_data in agent_data['flow_records'].items():
                if currency_name != currency:
                    continue
                flow_records = {}
                if not length:
                    length = len(currency_data)
                for n, step in enumerate(currency_data):
                    # Steps can include records for multiple currencies,
                    # or multiple records for the same currency
                    at_least_one = False
                    for record in step:
                        if agent_name not in flows:
                            flows[agent_name] = [] + [0] * n
                        if not at_least_one:
                            at_least_one = True
                            flows[agent_name].append(-record['amount'])
                        else:
                            flows[agent_name][-1] -= record['amount']
                    if not at_least_one and agent_name in flows:
                        flows[agent_name].append(0)

        if not length:
            print("No flow records for", currency)
            return

        plt.figure(figsize=(12,6))
        i = i if i else 0
        j = j if j else length
        steps = [x for x in range(j-i)]
        for agent_name, agent_data in flows.items():
            if agent_name in exclude:
                continue
            pad_zeros = len(steps) - len(agent_data)
            if pad_zeros > 0:
                agent_data += [0] * pad_zeros
            plt.plot(steps, agent_data[i:j], label=agent_name)
        plt.legend(loc='lower right')
        plt.show()

    plot_currency(data, 'o2')
