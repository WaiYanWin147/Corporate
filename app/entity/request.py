# app/entity/request.py
from app import db

class Request(db.Model):
    __tablename__ = "requests"

    requestID = db.Column(db.Integer, primary_key=True)
    pinID = db.Column(db.Integer, db.ForeignKey("user_accounts.userID"), nullable=False)
    csrRepID = db.Column(db.Integer, db.ForeignKey("user_accounts.userID"))
    categoryID = db.Column(db.Integer, db.ForeignKey("categories.categoryID"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default="open")
    viewCount = db.Column(db.Integer, default=0)
    shortlistCount = db.Column(db.Integer, default=0)
    createdAt = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    closedAt  = db.Column(db.DateTime)

    category = db.relationship("Category", back_populates="requests", lazy=True)

    person_in_need = db.relationship(
        "UserAccount",
        foreign_keys=[pinID],
        backref=db.backref("requests_made", lazy=True),
        lazy=True
    )

    csr_representative = db.relationship(
        "UserAccount",
        foreign_keys=[csrRepID],
        backref=db.backref("requests_supported", lazy=True),
        lazy=True
    )

    # link both sides using back_populates
    shortlists = db.relationship(
        "Shortlist",
        back_populates="request",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    match_records = db.relationship(
        "MatchRecord",
        back_populates="request",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
