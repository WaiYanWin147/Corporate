# app/entity/match_record.py
from app import db

class MatchRecord(db.Model):
    __tablename__ = "match_records"

    matchRecordID = db.Column(db.Integer, primary_key=True)
    requestID = db.Column(db.Integer, db.ForeignKey("requests.requestID", ondelete="CASCADE"), nullable=False)
    csrRepID = db.Column(db.Integer, db.ForeignKey("user_accounts.userID"), nullable=False)
    pinID = db.Column(db.Integer, db.ForeignKey("user_accounts.userID"), nullable=False)
    categoryID = db.Column(db.Integer, db.ForeignKey("categories.categoryID"), nullable=False)
    status = db.Column(db.String(30), default="completed")
    matchedAt   = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    completedAt = db.Column(db.DateTime)

    # Link to Request.match_records
    request = db.relationship("Request", back_populates="match_records", lazy=True)

    csr_representative = db.relationship(
        "UserAccount",
        foreign_keys=[csrRepID],
        backref=db.backref("match_records_as_csr", lazy=True),
        lazy=True
    )

    person_in_need = db.relationship(
        "UserAccount",
        foreign_keys=[pinID],
        backref=db.backref("match_records_as_pin", lazy=True),
        lazy=True
    )

    category = db.relationship("Category", lazy=True)
