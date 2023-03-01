import numpy as np
import matplotlib.pyplot as plt
from agent_model.util import parse_data

def plot_agent(data, agent, category, exclude=[], i=None, j=None, ax=None):
    """Helper function for plotting model data

    Plotting function which takes model-exported data, agent name,
    one of (flows, growth, storage, deprive), exclude, and i:j
    """
    i = i if i is not None else 0
    j = j if j is not None else data['step_num']
    ax = ax if ax is not None else plt
    if category == 'flows':
        path = [agent, 'flows', '*', '*', 'SUM', f'{i}:{j}']
        flows = parse_data(data, path)
        for direction in ('in', 'out'):
            if direction not in flows:
                continue
            for currency, values in flows[direction].items():
                label = f'{direction}_{currency}'
                if currency in exclude or label in exclude:
                    continue
                ax.plot(range(i, j), values, label=label)
    elif category == 'storage':
        path = [agent, 'storage', '*', f'{i}:{j}']
        storage = parse_data(data, path)
        for currency, values in storage.items():
            if currency in exclude:
                continue
            ax.plot(range(i, j), values, label=currency)
    elif category == 'deprive':
        path = [agent, 'deprive', '*', f'{i}:{j}']
        deprive = parse_data(data, path)
        for currency, values in deprive.items():
            if currency in exclude:
                continue
            ax.plot(range(i, j), values, label=currency)
    elif category == 'growth':
        path = [agent, 'growth', '*', f'{i}:{j}']
        deprive = parse_data(data, path)
        for field, values in deprive.items():
            if field in exclude:
                continue
            ax.plot(range(i, j), values, label=field)
    ax.legend()

def plot_b2_data(data, i=None, j=None):
    nrows = 5
    ncols = 3
    fig, axs = plt.subplots(nrows, ncols, figsize=(12, 9))
    fig.tight_layout()
    if i is None and j is None:
        index = '*'
    elif i is None:
        index = f':{j}'
    elif j is None:
        index = f'{i}:'
    else:
        index = f'{i}:{j}'

    # Greenhouse CO2, O2, h2o
    gh_atm_total = np.array(parse_data(data, ['greenhouse_b2', 'storage', 'SUM', index]))
    gh_co2 = np.array(parse_data(data, ['greenhouse_b2', 'storage', 'co2', index]))
    gh_o2 = np.array(parse_data(data, ['greenhouse_b2', 'storage', 'o2', index]))
    gh_h2o = np.array(parse_data(data, ['greenhouse_b2', 'storage', 'h2o', index]))
    co2_ppm = gh_co2 / gh_atm_total * 1000000
    o2_perc = gh_o2 / gh_atm_total * 100
    h2o_perc = gh_h2o / gh_atm_total * 100
    axs[0][0].plot(co2_ppm)
    axs[0][0].set_title('greenhouse co2 (ppm)')
    axs[0][1].plot(o2_perc)
    axs[0][1].set_title('greenhouse o2 (%)')
    axs[0][2].plot(h2o_perc)
    axs[0][2].set_title('greenhouse h2o (%)')

    # wheat, sweet potato, vegetables
    axs[1][0].set_title('wheat')
    plot_agent(data, 'wheat', 'growth', exclude=['agent_step_num', 'grown', 'te_factor'], ax=axs[1][0], i=i, j=j)
    axs[1][1].set_title('vegetables')
    plot_agent(data, 'vegetables', 'growth', exclude=['agent_step_num', 'grown', 'te_factor'], ax=axs[1][1], i=i, j=j)
    axs[1][2].set_title('sweet potatos')
    plot_agent(data, 'sweet_potato', 'growth', exclude=['agent_step_num', 'grown', 'te_factor'], ax=axs[1][2], i=i, j=j)

    # food_storage, human_deprive
    axs[2][0].set_title('food storage')
    food_storage = parse_data(data, ['food_storage', 'storage', '*', index])
    for food, amount in food_storage.items():
        axs[2][0].plot(amount, label=food)
    axs[2][1].set_title('human deprive')
    plot_agent(data, 'human_agent', 'deprive', ax=axs[2][1], i=i, j=j)
    axs[2][2].set_title('co2 storage')
    plot_agent(data, 'co2_storage', 'storage', ax=axs[2][2], i=i, j=j)

    # power, water, purifier
    axs[3][0].set_title('power storage')
    plot_agent(data, 'power_storage', 'storage', ax = axs[3][0], i=i, j=j)
    axs[3][1].set_title('water storage')
    plot_agent(data, 'water_storage', 'storage', exclude=['feces'], ax=axs[3][1], i=i, j=j)
    axs[3][2].set_title('water purifier')
    plot_agent(data, 'multifiltration_purifier_post_treatment', 'flows', ax=axs[3][2], i=i, j=j)

    # Sun, concrete, soil
    axs[4][0].set_title('sun')
    plot_agent(data, 'b2_sun', 'storage', ax=axs[4][0], i=i, j=j)
    axs[4][1].set_title('concrete')
    plot_agent(data, 'concrete', 'storage', ax=axs[4][1], i=i, j=j)
