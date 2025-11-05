"""
User Story:
As a user admin, I want to view user profile so that I can view all types of user profiles.
"""
from app.entity.user_profile import UserProfile

class UserAdminViewUserProfileController:
    def viewUserProfile(self, profile_id:int):
        return UserProfile.query.get(profile_id)
    def list_all(self, active_only=False):
        q = UserProfile.query
        if active_only: q = q.filter_by(isActive=True)
        return q.order_by(UserProfile.profileName).all()
