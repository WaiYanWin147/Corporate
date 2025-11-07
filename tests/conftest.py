import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app, db

@pytest.fixture()
def app():
    # tem DB create and FLASK APP for test
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # tem memory for test
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all() # create tem DB
    yield app

@pytest.fixture()
def client(app): # dummy web for GET/POST
    return app.test_client()
