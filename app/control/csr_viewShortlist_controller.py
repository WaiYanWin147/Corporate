"""
User Story:
As a CSR Rep, I want to view my shortlisted service requests so that I can assess which opportunities are most suitable to support.
"""
from app.entity.shortlist import Shortlist

class CsrViewShortlistController:
    def viewShortlist(self, userID: int, page: int = 1, per_page: int = 10):
        """Returns a paginated list of shortlisted requests for a CSR."""
        pagination = Shortlist.query.filter_by(csrRepID=userID).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return pagination

