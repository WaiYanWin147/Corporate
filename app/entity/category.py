from app import db

class Category(db.Model):
    __tablename__ = "categories"
    categoryID   = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(100), nullable=False, unique=True)
    description  = db.Column(db.String(255))
    isActive     = db.Column(db.Boolean, default=True)

    requests = db.relationship("Request", back_populates="category", lazy=True)
