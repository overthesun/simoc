====================
Getting Started
====================

.. highlight:: python

Basic Case
==========
The :ref:`agent-model` class is the main point of interaction between a user and
SIMOC. Below is a very basic example of loading a configuration, initializing
a model, running the model, and exporting the results.

::

    import json
    from agent_model import AgentModel

    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)

    model = AgentModel.from_config(config, data_collection=True)

    model.step_to(n_steps=601)

    data = model.get_data(debug=True)

Preset Configurations
=====================
Presets include everything required for a successful simulation, including:

* All full ECLSS system comprised of 8-10 individual agents
* Enough potable water and food rations to support the crew
* An earth-normal atmosphere in the habitat and/or greenhouse

The :ref:`simoc-config` object specifies which agents are included and at what
quantity, starting currency allocations, termination conditions, step order,
and other fields. The SIMOC repository includes 5 preset configurations,
matching the 5 preset simulations on the web interface.

* ``config_1h.json``: A small crew quarters with one human
* ``config_1hrad.json``: A small crew quarters with one human and one radish
* ``config_4h.json``: A medium crew quarters with four humans
* ``config_4hg.json``: A medium crew quarters with four humans and a small garden.
* ``config_1hg_sam.json``: The SAM habitat with 1 human and a small garden.

Presets are stored as ``.json`` files in the ``data_files`` directory. Load
presets into Python, then generate a SIMOC simulation using the
``AgentModel.from_config()`` method.

::

    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)
    model = AgentModel.from_config(config)

Custom Configurations
=====================
A best practice for custom configurations is to first load a preset, and then
modify it. This assures that all required fields are included, and the
atmosphere currencies are initialized correctly.

::

    # Load preset
    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)
    # Adjust agent amount
    config['agents']['radish']['amount'] += 10
    # Adjust starting currency allocation
    config['agents']['ration_storage']['ration'] += 10
    # Add a new agent
    config['agents']['rice'] = dict(amount=10)

Visualization
=============
``AgentModel.get_data()`` returns a :ref:`model-data`, which can be used to
generate visualizations. Below are two useful functions for inspecting
the data:

Inspect A Group
^^^^^^^^^^^^^^^
Agents' data includes up to 4 'group' fields, or fields that include several
currencies or variables. These are:

* ``growth``: All variables related to tracking and coordinating agent growth (e.g. ``current_growth``)
* ``storage``: The agent's current balance of stored currencies (e.g. ``internal_biomass``)
* ``flows``: The actual amount of each currency exchange (i.e. input/output)
* ``deprive``: The size and status of the deprivation buffer for each relevant currency

Each group is a dict of lists, and each list is the value of a variable at
every step of the simulation. Because they have a common structure, it is
convenient to view them with a single function, shown below. Also included
in the function are a list of variables to exclude, and an optional
start/finish step.

::

    import matplotlib.pyplot as plt

    def plot_group(group, exclude=[], i=None, j=None):
        plt.figure(figsize=(12,6))
        length = len(next(iter(group.values())))
        i = i or 0
        j = j or length-1
        steps = range(j-i)
        for currency, values in group.items():
            if sum(values) == 0 or currency in exclude:
                continue
            plt.plot(steps, values[i:j], label=currency)
        plt.legend()
        plt.show()

    # Inspect the co2 and h2o levesl of the crew habitat
    plot_group(data['crew_habitat_small']['storage'], exclude=['n2', 'o2'])

Inspect a Currency
^^^^^^^^^^^^^^^^^^
Sometimes you want to view all flows of a particular currency across all
agents. Below is a function that does this by iterating through the agents,
searching for the currency, and plotting it if found.

Note that flows are recorded in two different variables in agent data:

* ``flows``: the total absolute value of exchanges for a currency on a step.
* ``flow_records``: the amount input and output for each exchange of a currency on a step.

Above we used ``flows``, and here we'll use ``flow_records`` so we can plot
both postive and negative values:

::

    import matplotlib.pyplot as plt

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
                    at_least_one = False
                    for record in step:
                        if agent_name not in flows:
                            flows[agent_name] = [0] * n
                        if not at_least_one:
                            at_least_one = True
                            flows[agent_name].append(-record['amount'])
                        else:
                            flows[agent_name][-1] -= record['amount']
                    if not at_least_one and agent_name in flows:
                        flows[agent_name].append(0)
        plt.figure(figsize=(12,6))
        i = i or 0
        j = j or length
        steps = range(j-i)
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

Custom Agents
=============
SIMOC agent descriptions are spread across five data objects. ``.json`` files
for built-in agents are in the ``data_files`` directory, and are loaded
automatically when initializing a model. These data objects are:

* :ref:`currency-desc`: All currencies of exchange used by agents
* :ref:`agent-desc`: Inputs, outputs and charateristics that define how the agent functions
* :ref:`agent-conn`: Which agent(s) it is connected to for a particular currency
* :ref:`agent-variation` (optional): Initial and step-wise variation parameters
* :ref:`agent-events` (optional): Random events with their likelihood, duration and effects.

To add custom agents, first build custom description files for that agent,
then add description files as arguments to ``AgentModel.from_config()``.

::

    currency_desc = {...}
    agent_desc = {...}
    agent_conn = {...}
    model = AgentModel.from_config(config,
                                   currency_desc=currency_desc,
                                   agent_desc=agent_desc,
                                   agent_conn=agent_conn)

User-defined data objects are merged with the built-ins, replacing existing
fields of the same name, or adding new fields if not defined. This allows the
user to add new agents and currencies by defining an agent with a new name, or
modify built-in agents and currencies by mirroring the structure of the default
description but modifying specific fields.

Defining a new agent: Mushrooms
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here we define a very basic mushroom agent. First let's describe our target
behavior, then we'll integrate it into SIMOC.

* Consumes 10 grams of oxygen and 10 grams of inedible biomass per hour, following a sigmoid lifetime growth curve (i.e. mature plant consumes more)
* Grows 20g per hour (sum of oxygen and inedible biomass), following a normal lifetime growth curve (i.e. growth is fastest in the middle of lifetime)
* Live for 30 days, then harvest
* At harvest time, convert 90% of biomass to ``mushrooms``, and 10% to ``mushroom_waste``. Here we create a separate currency from ``inedible_bimoass`` (which the other plants produce) so that the mushroom can't eat itself.

The first task is to update the :ref:`currency-desc`. Oxygen, biomass and
inedible biomass are already defined, so we just need to add mushrooms
and mushroom waste. Make sure to nest them within the currect currency
class.

::

    custom_currency_desc = {
        'food': {
            'mushroom': {
                'label': 'Mushroom'
            }
        },
        'nutrients': {
            'mushroom_waste': {
                'label': 'Mushroom Waste'
            }
        }
    }

Next, we need to add capacity for these currencies to our storage agents
in the :ref:`agent-desc` data object. We do this by adding a new characteristic
to the existing storages. Again, don't forget to nest the agents within
the correct agent class.

::

    custom_agent_desc = {
        'storage': {
            'food_storage': {
                'data': {
                    'characteristics': [{
                        'type': 'capacity_mushroom',
                        'value': 1000,
                        'unit': 'kg'}]}},
            'nutrient_storage': {
                'data': {
                    'characteristics': [{
                        'type': 'capacity_mushroom_waste',
                        'value': 1000,
                        'unit': 'kg'}]}}
        }
    }

Now we'll add our new mushroom agent and define its inputs, outputs and
characteristics. We can add this to the ``agent_desc`` object we created in
the previous step.

::

    custom_agent_desc['plants'] = {
        'mushroom': {
            'data': {
                'input': [{
                    'type': 'o2',
                    'value': 0.01,
                    'required': 'desired',
                    'flow_rate': dict(unit='kg', time='hour'),
                    'growth': dict(lifetime={'type': 'sigmoid'}),
                    'deprive':  dict(value=72, unit='hour')
                }, {
                    'type': 'inedible_biomass',
                    'value': 0.01,
                    'required': 'desired',
                    'flow_rate': dict(unit='kg', time='hour'),
                    'growth': dict(lifetime={'type': 'sigmoid'}),
                    'deprive':  dict(value=72, unit='hour')
                }, {
                    'type': 'biomass',
                    'value': 1,
                    'weighted': 'current_growth',
                    'flow_rate': dict(unit='kg', time='hour'),
                    'criteria': dict(name='grown', 'limit='=', value=True)
                }],
                'output': [{
                    'type': 'biomass',
                    'value': 0.02,
                    'flow_rate': dict(unit='kg', time='hour'),
                    'growth': dict(lifetime={'type': 'sigmoid'}),
                }, {
                    'type': 'mushroom',
                    'value': 0.9,
                    'weighted': 'current_growth',
                    'flow_rate': dict(unit='kg', time='hour'),
                    'criteria': dict(name='grown', 'limit='=', value=True)
                }, {
                    'type': 'mushroom_waste',
                    'value': 0.1,
                    'weighted': 'current_growth',
                    'flow_rate': dict(unit='kg', time='hour'),
                    'criteria': dict(name='grown', 'limit='=', value=True)
                }],
                'characteristics': [
                    dict(type='lifetime', value=720, unit='hour'),
                    dict(type='growth_criteria', value='out_biomass'),
                    dict(type='capacity_biomass', value=100, unit='kg')
                ]
            }
        }
    }

Then we add connections for each currency exchanges to the :ref:`agent-conn`.

::

    custom_agent_conn = [
        dict(from='greenhouse.o2', to='mushroom.o2'),
        dict(from='nutrient_storage.inedible_biomass', to='mushroom.inedible_biomass'),
        dict(from='mushroom.biomass', to='mushroom.biomass'),
        dict(from='mushroom.mushroom', to='food_storage.mushroom'),
        dict(from='mushroom.mushroom_waste', to='nutrient_storage.mushroom_waste'),
    ]

Finally, we import a preset configuration, add some mushrooms to it, and
instantiate a new model using our custom data objects:

::

    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)
    config['agents']['mushroom'] = {'amount': 10}
    config['agents']['nutrient_storage']['inedible_biomass'] = 200
    model = AgentModel.from_config(config,
                                   data_collection=True,
                                   currency_desc=custom_currency_desc,
                                   agent_desc=custom_agent_desc,
                                   connections=custom_agent_conn)
    model.step_to(n_steps=1000)
    data = model.get_data(debug=True)
