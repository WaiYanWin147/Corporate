# app/control/pin_searchMatchRecord_controller.py
from sqlalchemy import func
from app import db
from app.entity.match_record import MatchRecord
from app.entity.request import Request
from app.entity.category import Category

class PinSearchMatchRecordController:
    def searchMatchRecord(self, pin_id: int, category_query: str = "", start_date: str = "", end_date: str = ""):
        """
        Returns completed match records for a PIN, filtered by optional category text and an inclusive date range.
        """
        # Base: only this PIN's completed records
        q = (
            db.session.query(MatchRecord)
            .join(Request, MatchRecord.requestID == Request.requestID)
            .join(Category, Request.categoryID == Category.categoryID)
            .filter(
                Request.pinID == pin_id,
                MatchRecord.status == "completed"   # ensure 'Completed Matches'
            )
        )

        # Category free-text search
        if category_query and category_query.strip():
            like = f"%{category_query.strip()}%"
            q = q.filter(Category.categoryName.ilike(like))

        # Inclusive date range (compare DATE only; ignores time)
        if start_date:
            q = q.filter(func.date(MatchRecord.completedAt) >= start_date)
        if end_date:
            q = q.filter(func.date(MatchRecord.completedAt) <= end_date)

        return q.order_by(MatchRecord.completedAt.desc()).all()
