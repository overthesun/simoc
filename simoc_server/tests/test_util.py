from simoc_server import db, app
from simoc_server.database.seed_data import seed_agents


def setup_db():
    clear_db()
    db.create_all()
    seed_agents.seed(app.config["AGENT_CONFIG"])
    db.session.commit()


def clear_db():
    db.sessionmaker.close_all()
    # db.engine.dispose()
    db.drop_all()
