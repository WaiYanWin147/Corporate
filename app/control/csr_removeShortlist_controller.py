"""
User Story:
As a CSR Rep, I want to remove service requests from my shortlist so that I can manage saved opportunities.
"""
from app import db
from app.entity.shortlist import Shortlist
from app.entity.request import Request

class CsrRemoveShortlistController:
    def removeFromShortlist(self, csrRepID: int, requestID: int) -> bool:
        """Removes a shortlist record and returns True if successful."""
        record = Shortlist.query.filter_by(csrRepID=csrRepID, requestID=requestID).first()
        if not record:
            raise ValueError("Shortlist entry not found.")

        try:
            req = record.request  # uses the relationship you added earlier
            if req and req.shortlistCount and req.shortlistCount > 0:
                req.shortlistCount -= 1

            db.session.delete(record)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to remove from shortlist: {e}")

