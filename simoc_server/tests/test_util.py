from simoc_server import db
from simoc_server.database.seed_data import seed


def setUpDB():
    db.create_all()
    seed.seed()
    db.session.commit()


def clearDB():
    db.sessionmaker.close_all()
    # db.engine.dispose()
    db.drop_all()