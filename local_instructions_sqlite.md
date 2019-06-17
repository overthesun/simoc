# Setup `SIMOC`on `Linux/macOS`

## 1. Clone `SIMOC` code from `GitHub`
```bash
git clone -b abm_database git@github.com:kstaats/simoc.git
cd simoc/
```

## 2. Follow the official guide to install `Python 3.6+` 

- https://www.python.org/downloads/

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

## 5. Run `SIMOC`

Set up `HTTP` port for the `SIMOC` web application:
```bash
export APP_PORT=8000
```

Start `SIMOC` application:
```bash
sh run.sh
```

## 6. Access `SIMOC` web application
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

