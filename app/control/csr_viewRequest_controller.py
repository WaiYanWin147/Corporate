from app import db
from app.entity.request import Request

class CsrViewRequestController:
    def viewRequestDetails(self, requestID: int):
        """Returns a single Request entity and increments its viewCount."""
        r = Request.query.get(requestID)
        if not r:
            raise ValueError("Request not found.")
        r.viewCount = (r.viewCount or 0) + 1
        db.session.commit()
        return r
