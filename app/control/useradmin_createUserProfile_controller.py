"""
User Story:
As a user admin, I want to create user profiles so that users can have the right access to the platform.
"""
from app import db
from app.entity.user_profile import UserProfile

class UserAdminCreateUserProfileController:
    def createUserProfile(self, profile_name:str, description:str=None):
        p = UserProfile(profileName=profile_name, description=description, isActive=True)
        db.session.add(p); db.session.commit(); return p
