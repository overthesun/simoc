from simoc_server import db


def add_all(data):
    if isinstance(data, dict):
        for key, value in data.items():
            db.session.add(value)
    else:
        try:
            for value in data:
                db.session.add(value)
        except TypeError:
            raise TypeError("Data must be either a dict or iterable.")
    db.session.commit()