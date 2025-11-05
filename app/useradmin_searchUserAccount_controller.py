"""
User Story:
As a user admin, I want to search user account by name so that I can find the user quickly.
"""
from app.entity.user_account import UserAccount

class UserAdminSearchUserAccountController:
    def searchUserAccountByName(self, userName: str):
        """Searches for user accounts by name (case-insensitive). Returns a list."""
        like_pattern = f"%{userName.strip()}%" if userName else "%"
        return (
            UserAccount.query
            .filter(UserAccount.name.ilike(like_pattern))
            .order_by(UserAccount.userID)
            .all()
        )
