import pytest
from app import create_app, db
from app.entity.user_account import UserAccount

@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    with app.app_context():
        db.create_all()
        u = UserAccount(
            name="Test Login",
            email="testLogin@gmail.com",
            age=25,
            phoneNumber="123456789",
            profileID=1
        )
        u.password = "12345"
        db.session.add(u)
        db.session.commit()
    yield app

def test_intentional_fail_wrong_password(app):
    # push wrong password check to fail
    with app.app_context():
        user = UserAccount.query.first()
        # fail to proceed here
        assert user.check_password("wrong") is True
