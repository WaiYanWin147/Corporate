"""
User Story:
As a Platform Manager, I want to reactivate previously suspended service categories 
so that they can be used again for new requests.
"""
from app import db
from app.entity.category import Category

class PlatformActivateCategoryController:
    def activateCategory(self, categoryID: int) -> bool:
        """Reactivates a category by setting isActive = True."""
        category = Category.query.get(categoryID)
        if not category:
            raise ValueError("Category not found.")
        category.isActive = True
        db.session.commit()
        return True
