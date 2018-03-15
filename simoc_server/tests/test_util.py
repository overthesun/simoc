from simoc_server import db, app
from simoc_server.database.seed_data import seed


def setup_db():
    clear_db()
    db.create_all()
    seed.seed()
    db.session.commit()

def clear_db():
    db.sessionmaker.close_all()
    # db.engine.dispose()
    db.drop_all()