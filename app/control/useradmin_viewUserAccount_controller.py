"""
User Story:
As a user admin, I want to view user account so that I can view user’s details.
"""
from app.entity.user_account import UserAccount

class UserAdminViewUserAccountController:
    def viewUserAccount(self, user_id:int):
        return UserAccount.query.get(user_id)
    def list_all(self):
        return UserAccount.query.order_by(UserAccount.userID).all()
