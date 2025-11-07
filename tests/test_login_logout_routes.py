import pytest
from app import create_app, db
from app.entity.user_profile import UserProfile
from app.entity.user_account import UserAccount

@pytest.fixture()
# make a tem db to test and then clean up
def app(): 
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # tem memory DB
        "WTF_CSRF_ENABLED": False, 
    })
    with app.app_context():
        db.create_all() # build tem db tables for test
    yield app # pytest cleans up after test

@pytest.fixture() # simulate GET/POST requests to dummy web app
def client(app):
    return app.test_client()

def _seed_user():    
    # dummy profile + account for login tests
    profile = UserProfile(
        profileName="Test Profile",       
    )
    db.session.add(profile)
    db.session.flush()  # save profile to get profile.profileID

    user = UserAccount(
        name="Test Login",
        email="testLogin@gmail.com",
        age=25,
        phoneNumber="1234567890",
        profileID=profile.profileID,    
    )
    user.password = "12345"                 # hashes auto password set
    db.session.add(user)
    db.session.commit()
    return user, profile

def test_login_logout_flow(app, client):
    with app.app_context():
        _seed_user()

    # try login with same information
    resp = client.post("/login", data={"email": "testLogin@gmail.com", "password": "12345"}, follow_redirects=False)
    assert resp.status_code in (200, 302)

    # Flask-Login _user_id
    with client.session_transaction() as sess:
        assert "_user_id" in sess and str(sess["_user_id"]).isdigit()

    # logout
    resp2 = client.get("/logout", follow_redirects=False)
    assert resp2.status_code in (200, 302)

    # clear session
    with client.session_transaction() as sess:
        assert "_user_id" not in sess

def test_login_rejects_bad_password(app, client):
    with app.app_context():
        _seed_user()

    # try login with wrong password
    resp = client.post("/login", data={"email": "testLogin@gmail.com", "password": "wrong"}, follow_redirects=False)
    
    # should be fail, normally crash, put status 200 but failure message shown 
    assert resp.status_code in (200, 400, 401, 302)

    with client.session_transaction() as sess:
        assert "_user_id" not in sess
