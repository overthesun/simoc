import httpx
import asyncio
import time

url = 'http://127.0.0.1:8000'

num_of_simulations = 20
game_config = {
    "game_config": {"duration":      {"value": 90, "type": "day"}, "human_agent": {"amount": 4},
                    "food_storage":  {"amount": 10000}, "solar_pv_array_mars": {"amount": 30},
                    "power_storage": {"amount": 1}, "eclss": {"amount": 1}, "single_agent": 1,
                    "plants":        [{"species": "wheat", "amount": 50},
                                      {"species": "cabbage", "amount": 50},
                                      {"species": "strawberry", "amount": 50},
                                      {"species": "radish", "amount": 50},
                                      {"species": "red_beet", "amount": 33},
                                      {"species": "lettuce", "amount": 34}],
                    "greenhouse":    "greenhouse_small", "habitat": "crew_habitat_small"},
    'step_num':    1000}

request_step_data = {"min_step_num":       0,
                     "n_steps":            game_config['step_num'],
                     "total_production":   ["atmo_co2", "atmo_o2", "h2o_potb", "enrg_kwh",
                                            "biomass_totl"],
                     "total_consumption":  ["atmo_o2", "h2o_potb", "enrg_kwh"],
                     "storage_ratios":     {
                         "air_storage_1": ["atmo_co2", "atmo_o2", "atmo_ch4", "atmo_n2", "atmo_h2",
                                           "atmo_h2o"]},
                     "total_agent_count":  ["human_agent", "cabbage"],
                     "agent_growth":       ["cabbage", "wheat", "strawberry", "radish", "red_beet",
                                            "lettuce"],
                     "storage_capacities": {}}


async def get_steps_background(request, user_creds, timeout=2, max_retries=50):
    retries_left = max_retries
    step_count = 0
    n_steps = request['n_steps']
    async with httpx.AsyncClient() as client:
        _ = await client.post(f'{url}/login', json=user_creds, timeout=None)
        while True:
            await asyncio.sleep(timeout)
            r = await client.post(f'{url}/get_steps', json=request, timeout=None)
            json_body = r.json()
            step_data = json_body['step_data']
            step_count += len(step_data)
            if len(step_data) == 0:
                retries_left -= 1
            else:
                print(f'username: {user_creds["username"]}, step_count: {step_count}, max_steps: {n_steps}')
                retries_left = max_retries
            if step_count >= n_steps or retries_left <= 0:
                print(f'{step_count} steps retrieved for "{user_creds["username"]}"')
                break
            else:
                request['min_step_num'] = step_count + 1


async def main():
    start_time = time.time()
    game_ids = {}
    tasks = []
    for i in range(num_of_simulations):
        sim_start_time = time.time()
        print(f'-> Starting simulation {i + 1}')
        user_creds = {'username': f'test_{i}', 'password': 'test'}
        async with httpx.AsyncClient() as client:
            _ = await client.post(f'{url}/register', json=user_creds, timeout=None)
            _ = await client.post(f'{url}/login', json=user_creds, timeout=None)
            r = await client.post(f'{url}/new_game', json=game_config, timeout=None)
        json_body = r.json()
        if 'game_id' in json_body:
            request = request_step_data.copy()
            game_ids[i] = request['game_id'] = json_body['game_id']
            tasks.append(get_steps_background(request, user_creds))
        else:
            print(f'Cannot start simulation {i + 1}')
            pass
        elapsed_time = time.time() - sim_start_time
        print(f'-> Simulation {i} started in {elapsed_time:.2f} seconds')
    elapsed_time = time.time() - start_time
    print(f'==>> {len(game_ids)} simulations started in {elapsed_time:.2f} seconds')
    await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
