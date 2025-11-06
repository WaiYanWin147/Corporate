from app import db

class Report(db.Model):
    __tablename__ = "reports"
    reportID    = db.Column(db.Integer, primary_key=True)
    reportTitle = db.Column(db.String(255), nullable=False)
    reportType  = db.Column(db.String(50), nullable=False)
    generatedBy = db.Column(db.Integer, db.ForeignKey("user_accounts.userID"), nullable=False)
    reportData  = db.Column(db.Text)
    period      = db.Column(db.String(50))
    generatedAt = db.Column(db.DateTime, default=db.func.now(), nullable=False)
