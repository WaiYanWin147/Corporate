"""
User Story:
As a user admin, I want to update user account so that I can ensure information is the latest.
"""
from app import db
from app.entity.user_account import UserAccount
from app.entity.user_profile import UserProfile

class UserAdminUpdateUserAccountController:
    def updateUserAccount(self, userID: int, name: str = None, email: str = None,
                          password: str = None, age: int = None,
                          phoneNumber: str = None, profileID: int = None) -> bool:
        """Updates an existing user account and returns True if successful."""
        user = UserAccount.query.get(userID)
        if not user:
            raise ValueError("User not found.")

        # update profile if provided
        if profileID is not None:
            profile = UserProfile.query.filter_by(profileID=profileID, isActive=True).first()
            if not profile:
                raise ValueError(f"Profile ID '{profileID}' not found or inactive.")
            user.profileID = profileID

        # update basic fields
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if age is not None:
            user.age = age
        if phoneNumber is not None:
            user.phoneNumber = phoneNumber

        # update password if provided
        if password:
            user.password = password

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to update user: {e}")
