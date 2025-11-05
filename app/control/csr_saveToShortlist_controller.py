from app import db
from app.entity.request import Request
from app.entity.shortlist import Shortlist

class CsrSaveToShortlistController:
    def saveToShortlist(self, requestID: int, csrID: int) -> bool:
        """Adds a request to the CSR's shortlist and returns True if successful."""
        r = Request.query.get(requestID)
        if not r:
            raise ValueError("Request not found.")

        # check if already shortlisted (optional safeguard)
        exists = Shortlist.query.filter_by(csrRepID=csrID, requestID=requestID).first()
        if exists:
            return False

        r.shortlistCount = (r.shortlistCount or 0) + 1
        db.session.add(Shortlist(csrRepID=csrID, requestID=requestID))
        db.session.commit()
        return True
