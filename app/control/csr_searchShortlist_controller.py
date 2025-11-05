"""
User Story:
As a CSR Rep, I want to search my shortlisted service requests by category
so that I can quickly find saved opportunities related to specific services.
+ searchShortlistByCategory(categoryID: int): list<Request>
"""
from app.entity.shortlist import Shortlist
from app.entity.request import Request
from app.entity.category import Category

class CsrSearchShortlistController:
    def searchShortlistByCategory(self, csr_id: int, category_id: int = None):
        """
        Returns all Shortlist entries for a CSR, optionally filtered by category.
        """
        q = Shortlist.query.join(Request).filter(Shortlist.csrRepID == csr_id)

        if category_id:
            q = q.filter(Request.categoryID == category_id)

        return q.order_by(Shortlist.shortlistID.desc()).all()
