"""
User Story:
As a user admin, I want to suspend user account so that I can maintain user access.
"""
from app import db
from app.entity.user_account import UserAccount

class UserAdminSuspendUserAccountController:
    def suspendUserAccount(self, userID: int) -> bool:
        """Suspends a user account and returns True if successful."""
        user = UserAccount.query.get(userID)
        if not user:
            raise ValueError("User not found.")

        user.isActive = False
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to suspend user: {e}")
