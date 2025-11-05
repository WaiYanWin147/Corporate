"""
User Story:
As a user admin, I want to search for users by user profile so that I can easily find all users belonging to a specific profile.
"""
from app.entity.user_account import UserAccount
from app.entity.user_profile import UserProfile

class UserAdminSearchUserProfileController:
    def searchUserByProfile(self, profileID: int):
        """Search users belonging to a specific profile ID. Returns list of UserAccount."""
        if not profileID:
            return []
        
        profile = UserProfile.query.get(profileID)
        if not profile:
            raise ValueError(f"Profile ID '{profileID}' not found.")
        
        return UserAccount.query.filter_by(profileID=profileID).order_by(UserAccount.userID).all()
