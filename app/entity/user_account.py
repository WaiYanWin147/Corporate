from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class UserAccount(UserMixin, db.Model):
    __tablename__ = "user_accounts"

    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)  # explicit auto increment
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    _password = db.Column("password", db.String(255), nullable=False)
    age = db.Column(db.Integer)
    phoneNumber = db.Column(db.String(20))
    isActive = db.Column(db.Boolean, default=True)
    profileID = db.Column(db.Integer, db.ForeignKey("user_profiles.profileID"), nullable=False)

    profile = db.relationship("UserProfile", back_populates="users", lazy=True)

    # Flask-Login requirement
    def get_id(self):
        return str(self.userID)

    # Password property
    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self._password, raw)


@login_manager.user_loader
def load_user(user_id):
    return UserAccount.query.get(int(user_id))
