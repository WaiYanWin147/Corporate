"""
User Story:
As a Platform Manager, I want to view service categories so that I can see the types of service categories.
"""
from app.entity.category import Category

class PlatformViewCategoryController:
    def view_categories(self, active_only:bool=False):
        q = Category.query
        if active_only: q = q.filter_by(isActive=True)
        return q.order_by(Category.categoryName).all()
