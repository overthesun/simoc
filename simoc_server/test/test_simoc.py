import os
import json
import tempfile

import pytest

import simoc_server


@pytest.fixture
def client():
    #db_fd, simoc_server.app.config['DATABASE'] = tempfile.mkstemp()
    simoc_server.app.config['TESTING'] = True
    with simoc_server.app.test_client() as client:
        #with simoc_server.app.app_context():
            #simoc_server.init_db()
        yield client

    #os.close(db_fd)
    #os.unlink(simoc_server.app.config['DATABASE'])

def register(client, username, password):
    data = json.dumps(dict(username=username, password=password))
    return client.post('/register', data=data, follow_redirects=True)

def login(client, username, password):
    data = json.dumps(dict(username=username, password=password))
    return client.post('/login', data=data, follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login_logout(client):
    """Make sure login and logout works."""
    import random # temporary workaround before we mock the db
    username = 'testuser' + str(random.randrange(1000000))
    password = 'testpassword'

    rv = register(client, username, password)
    assert b'Registration complete.' in rv.data

    rv = logout(client)
    assert b'Logged out' in rv.data

    rv = login(client, username, password)
    assert b'Logged in' in rv.data

    # invalid logins
    rv = login(client, f"{username}x", password)
    assert b'Invalid username' in rv.data

    rv = login(client, username, f'{password}x')
    assert b'Invalid username or password' in rv.data
