====================
Data Objects
====================

.. highlight:: python

.. _simoc-config:

Config
======

Describes a single simulation.

::

    config = {                       # * = Required, ! = supports default arg only
        'agents': {                  # *
            'rice': {
                'amount': 10,        # *
                'id': 1,
                <currency>: 10,
                'connections': [<Agent>],
                'delay_start': 0,
            },
            #...
        },
        'termination': [{
            'condition': 'time',     # !
            'value': 100,
            'unit': 'day'            # 'min', 'hour', 'day', 'year'
        }],
        'priorities': [              # by agent class; sub-agents step randomly
            'structures', 'storage',
            'power_generation',
            'inhabitants', 'eclss',
            'plants'
        ],
        'seed': 12345,               # Must be an integer
        'global_entropy': 0,         # 0 = no variation, 1 = max variation
        'location': 'mars'           # !
        'minutes_per_step': 60,      # !
        'single_agent': 1,           # !
    }

.. _model-data:

Model Data
==========

The data returned by ``AgentModel.get_data()``. To return all fields use with
``debug=True``. All lists have one entry for each step of the simulation.

::

    data = {                               # * = default fields
        'rice': {
            'name': 'rice',                # *
            'full_amount': 10,             # *
            'lifetime': 720,
            'reproduce': True,
            'initial_variable': 0.98765,
            'capacity': {<storage>: 100},
            'amount': [10, ...],           # *
            'age': [0, 1, ...],
            'step_variable': [1.2, 2.3, ...],
            'storage': {<storage>: [0, ...]},
            'storage_ratios': {<storage>: [1, ...]},
            'flows': {
                'in': {<currency>: {<storage>: [1, ...]}},
                'out': {<currency>: {<storage>: [1, ...]}},
            },
            'buffer': {<currency>: [8, ...]},
            'deprive': {<currency>: [720, ...]},
            'growth': {
                'total_growth': [0, ...],
                'growth': [0, ...],
                'grown': [False, ...],
                'agent_step_num': [0, 1, ...],
            },
            'events': [{
                <event>: [{
                    'magnitude': 0.8,
                    'duration': 10
                }]
            }],
            'event_multipliers': {<event>: [0, ...]}
        }
    }

.. _currency-desc:

Currency Description
====================

::

    currency_desc = {
        'food': {                                  # Currency class
            'radish': {                            # * = Required, ^ = food only
                'label': 'Radish',                 # * Display name
                'description': 'Radishes, fresh',
                'source': <url>,                   # ^ Nutrition data reference
                'unit': 'kg',                      # ^
                'nutrition': {                     # ^ Grams per <unit>
                    "kcal": 180,
                    "water": 941,
                    "protein": 10,
                    "carbohydrate": 25,
                    "fat": 2
                }
            },
            # ...
        }
        # ...
    }

Currency classes: ``atmosphere``, ``nutrients``, ``food``, ``water``, ``energy``

.. _agent-desc:

Agent Description
====================

::

    agent_desc = {
        'plants': {                                 # Agent class
            'radish': {                             # Agent name
                'description': '',                  # Text description
                'data': {
                    'inputs': [...<Input>],         # Currencies consumed
                    'outputs': [...<Output>],       # Currencies produced
                    'characteristics': [...<Char>]  # Misc params
                }
            }
            # ...
        }
        # ...
    }

    <Input/Output> = {                  # * = Required
        'type': 'co2',                  # * Currency name, must be in currency_desc
        'value': 0.006534,              # * Amount exchagned
        'flow_rate': {                  # * Units applied to currency exchanged
            'unit': 'kg',
            'time': 'hour'
        },
        'required': 'mandatory',        # 'mandatory' = if unavailable, skip step()
                                        # 'desired' = if unavailable, continue step()
        'deprive': {                    # If unavailable, how long to survive
            'value': 72,
            'unit': 'hour'
        }
        'growth': {                     # Map value across the hours in a day
                                        # and/or hours in agent's lifetime such
                                        # that mean hourly value is as defined.
            "lifetime": {
                "type": "sigmoid"       # 'sigmoid' = greater and end-of-lifetime
                                        # 'normal' = greater at mid-life
            },
            "daily": {
                "type": "normal"        # 'normal' = greatest in middle of day
                                        # 'clipped' = reduced early/late values
                                        # 'switch' = boolean for 'is daylight'
            }
        },
        'requires': ['h2'],             # If input is missing, skip flow
        'weighted': 'current_growth'    # Multiply value by agent storage amount or attribute
        'criteria': {                   # Activate flow based on view of a connected agent
            'name': 'co2_ratio_in',     # '<currency>_<view>_<direction>'
            'limit': '>',               # '=', '>', '<'
            'value': 0.001,             # What the returned value is compared to
            'buffer': 2                 # Wait until valid for N steps before activating.
        }
    }

    <Char> = {
        'type': 'capacity_o2',      # Characteristic type
        'value': 10000,             # Supports bool, int, float or string
        'unit': 'kg'                # Optional
    }


Agent classes: ``inhabitants``, ``eclss``, ``plants``, ``isru``, ``structures``,
``fabrication``, ``power_generation``, ``mobility``, ``communication``, ``storage``

Characteristic types:

* ``capacity_<currency>``: The maximum amount of a particular currency that can be stored.
* ``lifetime``: Length of one growth cycle
* ``carbon_fixation``: 'c3' or 'c4', determines if/how plant responds to ambient co2.
* ``volume``: m**3
* ``mass``: kg
* ``category``: sub-class, e.g. 'habitat'
* ``reproduce``: boolean; whether lifecycle ends or is repeated
* ``custom_function``: two are included in the SIMOC repo: ``atmosphere_equalizer`` and ``rate_finder``.
* ``threshold_lower_<currency>``: Agent is killed if ambient currency falls below

.. _agent-conn:

Agent Connections
=================

Connections are directional links between agents which determine the source of
inputs or destination of outputs.

The ``to``/``from`` fields specify an agent and currency. For the agent field,
two additional options, ``habitat`` and ``greenhouse``, are used; when a model
is initialized, those options are replaced with the agent that includes the
word 'habitat' or 'greenhouse' (e.g. 'greenhouse.o2' -> 'greenhouse_medium.o2')

The ``priority`` field is optional. If present, when the first connection
(priority=0) is empty, the initiating agent will change to the second
(priority=1) connection, and so on.

::

    agent_conn = [{
        'from': '<agent>.<currency>',
        'to': '<agent>.<currency>',
        'priority': 0
    }, ...]

.. _agent-variation:

Agent Variation
===============

Agent variation is off by default. To activate, set the ``global_entropy``
parameter in ``config`` to a number 0 < N <= 1.

When active, all currency exchange values are scaled up or down when
initialized and/or every step. Scalars are a random number from a
defined probability density function. The ``upper`` and ``lower`` parameters
specify the maximum absolute distance up or down from 1 (no effect).

::

    agent_variation = {
        'plants': {                         # Can be agent or agent class
            'initial': {                    # Applied to values on initialization
                'upper': 0.5,               # Multiplier upper bound
                'lower': 0.5,               # Multiplier lower bound
                'distribution': 'normal'    # Probability: 'normal' or 'exponential'
            },
            'step': {
                'upper': 0.1,
                'lower': 0.1,
                'distribution': 'normal'
            }
        }

Alternatively, upper and lower values can be defined for each individual
currency.

::

    agent_variation['humans'] = {
        'initial': {
            "upper": {
                "o2": 0.045,
                # ...
            },
            "lower": {
                "o2": 0.025417,
                # ...
            },
            "distribution": "normal",
            "stdev_range": 1.65,
            "characteristics": ["mass"]
        }
        # ...
    }

.. _agent-events:

Agent Events
============

Agent events are off by default. To activate, set the ``global_entropy``
parameter in ``config`` to a number 0 < N <= 1.

::

    agent_events = {
        "solar_pv_array_mars": [
            {
                "type": "duststorm",
                "function": "multiplier",         # 'multiplier': apply to all flows
                                                  # 'termination': kill agent
                "scope": "group",                 # 'group': affects all instances
                                                  # 'agent': affects a single instance
                "probability": {                  # Per group/individual based on scope
                    "value": 0.0004566210046,     # Likelihood per step (if not active)
                    "unit": "hour"
                },
                "magnitude": {
                    "value": 1,
                    "variation": {
                        "upper": 0,               # Maximum remains 1x, no effect
                        "lower": 0.9,             # Minimum is 0.1x
                        "distribution": "normal"  # Mean is 0.55x
                    }
                },
                "duration": {
                    "value": 24,                  # How long the effect lasts
                    "unit": "hour",
                    "variation": {
                        "upper": 60,              # "From 1 to 60 days"
                        "lower": 1,
                        "distribution": "exponential"  # Likely a low number
                    }
                }
            },
            # ...
        ]
    }

