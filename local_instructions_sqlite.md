# Start `SIMOC` locally on `Linux/macOS` (`SQLite` backend)

## 1. Clone `SIMOC` code from `GitHub`
```bash
git clone -b celery_integration git@github.com:kstaats/simoc.git
cd simoc/
```

## 2. Follow the official guides to install `Python 3.6` and `Redis` 

- https://www.python.org/downloads/
- https://redis.io/download

### 2.1 Start `Redis` via `Docker` 
Instead of manually installing `Redis` on a local `OS`, follow the instructions below to deploy it as a `Docker` container.

#### 2.1.1 Follow the official guide to install `Docker`
- https://docs.docker.com/install/

#### 2.1.2 Set up `Redis` password (fill in the `REDIS_PASSWORD`)
```bash
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

#### 2.1.3 Start `Redis` container
```bash
docker run -d \
    --name=redis \
    --net=simoc-net \
    -p 6379:6379 \
    redis redis-server --requirepass $REDIS_PASSWORD
```

## 3. Set up `Python 3` virtual environment
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

## 5. Start `Celery Worker` process

Set up `Redis` connection (fill in the `REDIS_PASSWORD`):
```bash
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

Set up number of threads per `Celery Worker`:
```bash
export CELERY_THREADS=2
```

Start a new `Celery Worker` process:
```bash
sh start_worker.sh
```
Worker logs will start streaming into the `Terminal` output.

You can start multiple `Celery Workers` to process tasks in parallel.
Make sure you run each worker in a separate `Terminal` session and keep all sessions alive.

## 6. Start `Flask Application` server

Open up a new `Terminal` session and navigate to the `simoc` folder:
```bash
cd /path/to/simoc/folder
```

Activate `Python` virtual environment:
```bash
source simoc-env/bin/activate
```

Set up `Redis` connection (fill in the `REDIS_PASSWORD`):
```bash
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

Set up `HTTP` port for the `SIMOC` web application:
```bash
export APP_PORT=8000
```

Set up number of threads per `Flask Application`:
```bash
export WSGI_WORKERS=2
```

Start `SIMOC` application:
```bash
sh run.sh
```

## 7. Access `SIMOC` web application
Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)

# Useful commands

## Reset `SQLite` database

Remove the `SQLite` database file from the `simoc/sqlite` directory:
```bash
rm sqlite/db.sqlite
```

Re-initialize an `SQLite` database:
```bash
python3 create_db.py
```

## Run `SIMOC` in `console_mode`
Using a sample `game_config` file :
```bash
export NO_FLASK=1 && python3 -m simoc_server --console_mode \
    --username test --password test \
    --game_config_path sample_game_config.json \
    --num_steps 100
```
You should manually interrupt the script when it's finished.

For custom scenarios, modify the configuration file and set up the path to the file via `--game_config_path` argument.

## Kill all running `Celery Workers`
```bash
ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9
```



