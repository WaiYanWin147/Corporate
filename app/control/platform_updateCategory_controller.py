"""
User Story:
As a Platform Manager, I want to update service categories so that they remain relevant.
"""
from app import db
from app.entity.category import Category

class PlatformUpdateCategoryController:
    def updateCategory(self, categoryID: int, categoryName: str, description: str):
        """Updates category name and description."""
        category = Category.query.get(categoryID)
        if not category:
            raise ValueError("Category not found.")

        category.categoryName = categoryName
        category.description = description

        db.session.commit()
        return True
