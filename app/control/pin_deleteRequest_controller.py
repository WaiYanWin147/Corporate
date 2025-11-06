"""
User Story:
As a PIN, I want to delete my service requests so that I can stop receiving offers I do not need.

UML: + deleteRequest(requestID: int): boolean
Hard delete: remove row from database.
"""
from app import db
from app.entity.request import Request

class PinDeleteRequestController:
    def deleteRequest(self, requestID: int, userID: int) -> bool:
        """Permanently delete a request owned by this PIN."""
        r = Request.query.get(requestID)
        if not r:
            raise ValueError("Request not found.")
        if r.pinID != userID:
            raise PermissionError("Unauthorized: You cannot delete another user's request.")

        try:
            db.session.delete(r)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to delete request: {e}")
