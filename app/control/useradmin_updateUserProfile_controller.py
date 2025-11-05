"""
User Story:
As a user admin, I want to update user profile so that I can ensure information is the latest.
"""
from app import db
from app.entity.user_profile import UserProfile
from app.control.useradmin_activateUserProfile_controller import UserAdminActivateUserProfileController
from app.control.useradmin_suspendUserProfile_controller import UserAdminSuspendUserProfileController

class UserAdminUpdateUserProfileController:
    def updateUserProfile(self, profileID: int, newProfileID: int = None,
                          profileName: str = None, description: str = None) -> bool:
        """Updates a user profile based on UML spec. Returns True if successful."""
        p = UserProfile.query.get(profileID)
        if not p:
            raise ValueError("Profile not found.")

        # handle profile ID change 
        if newProfileID and newProfileID != profileID:
            if UserProfile.query.get(newProfileID):
                raise ValueError(f"Profile ID '{newProfileID}' already exists.")
            p.profileID = newProfileID

        # update name and description
        if profileName:
            p.profileName = profileName.strip()
        if description is not None:
            p.description = description  # allow empty string

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to update profile: {e}")

    def toggleActivation(self, profileID: int, activate: bool) -> bool:
        if activate:
            return UserAdminActivateUserProfileController().activateUserProfile(profileID)
        else:
            return UserAdminSuspendUserProfileController().suspendUserProfile(profileID)

