# app/entity/shortlist.py
from app import db

class Shortlist(db.Model):
    __tablename__ = "shortlists"

    shortlistID = db.Column(db.Integer, primary_key=True)
    requestID = db.Column(db.Integer, db.ForeignKey("requests.requestID", ondelete="CASCADE"), nullable=False)
    csrRepID = db.Column(db.Integer, db.ForeignKey("user_accounts.userID"), nullable=False)
    createdAt = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    # ✅ This is the key part
    request = db.relationship("Request", back_populates="shortlists", lazy=True)

    csr_representative = db.relationship(
        "UserAccount",
        foreign_keys=[csrRepID],
        backref=db.backref("shortlisted_requests", lazy=True),
        lazy=True
    )

    