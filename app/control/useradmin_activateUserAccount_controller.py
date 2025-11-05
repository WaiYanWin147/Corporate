"""
User Story:
As a user admin, I want to activate suspended user account so that users can regain access.
"""
from app import db
from app.entity.user_account import UserAccount

class UserAdminActivateUserAccountController:
    def activateUserAccount(self, userID: int) -> bool:
        """Activates a suspended user account and returns True if successful."""
        user = UserAccount.query.get(userID)
        if not user:
            raise ValueError("User not found.")

        user.isActive = True
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to activate user: {e}")
