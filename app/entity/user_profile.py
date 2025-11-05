from app import db

class UserProfile(db.Model):
    __tablename__ = "user_profiles"
    profileID   = db.Column(db.Integer, primary_key=True, autoincrement=True)  # explicit auto increment
    profileName = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))
    isActive    = db.Column(db.Boolean, default=True)

    users = db.relationship("UserAccount", back_populates="profile", lazy=True)
