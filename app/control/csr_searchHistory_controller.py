"""
User Story:
As a CSR Rep, I want to search and view the history of my completed volunteer services,
filtered by category and date period.
"""
from app.entity.match_record import MatchRecord
from datetime import datetime
from sqlalchemy import func   # ✅ Add this

class CsrSearchHistoryController:
    def searchHistory(self, userID: int, category_id: int = None, start_date: str = None, end_date: str = None):
        """Returns completed match records for a CSR representative filtered by category and date."""
        q = MatchRecord.query.filter(
            MatchRecord.csrRepID == userID,
            MatchRecord.status == "completed"
        )

        # Filter by category
        if category_id:
            q = q.filter(MatchRecord.categoryID == category_id)

        # Filter by date range (compare DATE only)
        if start_date:
            q = q.filter(func.date(MatchRecord.completedAt) >= start_date)

        if end_date:
            q = q.filter(func.date(MatchRecord.completedAt) <= end_date)

        return q.order_by(MatchRecord.completedAt.desc()).all()
