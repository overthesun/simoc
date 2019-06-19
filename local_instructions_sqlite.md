# Setup `SIMOC`on `Linux/macOS`

## 1. Clone `SIMOC` code from `GitHub`
```bash
git clone -b celery_integration git@github.com:kstaats/simoc.git
cd simoc/
```

## 2. Follow the official guide to install `Python 3.6` 

- https://www.python.org/downloads/

## 3. Follow the official guide to install and start `Redis`
- https://redis.io/download

## 4. Set up `Python 3` virtual environment
```bash
python3 -m venv simoc-env
source simoc-env/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install --upgrade -r requirements.txt
```

## 4. Initialize `SQLite` database
```bash
python3 create_db.py
```

## 5. Test `SIMOC` set up

Start `SIMOC` in `console_mode` with a sample `game_config` file (interrupt when finished):
```bash
export NO_FLASK=1 && python3 -m simoc_server --console_mode \
    --username test --password test \
    --game_config_path sample_game_config.json \
    --num_steps 100
```
For custom scenarios, set up the path to the configuration file via `--game_config_path` argument.

## 6. Start `Celery` worker

Set up `Redis` connection (fill in the `REDIS_PASSWORD`):
```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

Set up number of threads per `Celery` worker:
```bash
export CELERY_THREADS=2
```

Start a new `Celery` worker process:
```bash
sh start_worker.sh
```
Worker logs will start streaming into the `Terminal` output. 

## 7. Run `SIMOC` wih `UI`

Open up a new `Terminal` window and navigate to the `simoc` folder:
```bash
cd /path/to/simoc/folder
```

Activate `Python` virtual environment:
```bash
source simoc-env/bin/activate
```

Set up `Redis` connection: (fill in the `REDIS_PASSWORD`):
```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

Set up `HTTP` port for the `SIMOC` web application:
```bash
export APP_PORT=8000
```

Start `SIMOC` application:
```bash
sh run.sh
```

## 8. Access `SIMOC` web application
Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)

# Reset `SQLite` database

Remove the `SQLite` database file from the `simoc/sqlite` directory:
```bash
rm sqlite/db.sqlite
```

Re-initialize an `SQLite` database:
```bash
python3 create_db.py
```

