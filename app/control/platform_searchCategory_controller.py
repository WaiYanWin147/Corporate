"""
User Story:
As a Platform Manager, I want to search service categories by name so that I can quickly find a specific category.
"""
from app.entity.category import Category

class PlatformSearchCategoryController:
    def searchCategoryByName(self, name: str):
        """Returns a list of categories matching the given name (case-insensitive)."""
        like_pattern = f"%{name or ''}%"
        return (
            Category.query
            .filter(Category.categoryName.ilike(like_pattern))
            .order_by(Category.categoryName)
            .all()
        )
