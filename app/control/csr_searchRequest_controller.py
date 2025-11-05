"""
User Story:
As a CSR Rep, I want to search for service requests so that I can find opportunities that match my organization’s resources.
"""
from app.entity.request import Request
from app.entity.category import Category

class CsrSearchRequestController:
    def searchRequest(self, category: str):
        """Returns a list of open requests filtered by category (if provided)."""
        q = Request.query.join(Category, Request.categoryID == Category.categoryID)

        # Filter only active categories and open requests
        q = q.filter(Category.isActive == True, Request.status == "open")

        if category:
            q = q.filter(Category.categoryName.ilike(f"%{category}%"))

        return q.order_by(Request.requestID.desc()).all()
