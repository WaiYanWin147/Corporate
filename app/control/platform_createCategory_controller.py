"""
User Story:
As a Platform Manager, I want to create service categories (transport, health support) so that requests are properly classified.
"""
from app import db
from app.entity.category import Category

class PlatformCreateCategoryController:
    def create_category(self, name:str, description:str=None):
        c = Category(categoryName=name, description=description, isActive=True)
        db.session.add(c); db.session.commit(); return c
