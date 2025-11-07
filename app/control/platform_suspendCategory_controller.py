"""
User Story:
As a Platform Manager, I want to suspend unused service categories so that invalid service categories are no longer used.
"""
from app import db
from app.entity.category import Category

class PlatformSuspendCategoryController:
    def suspendCategory(self, categoryID: int) -> bool:
        """Deactivates a category by setting isActive = False."""
        category = Category.query.get(categoryID)
        if not category:
            raise ValueError("Category not found.")
        category.isActive = False
        db.session.commit()
        return True
