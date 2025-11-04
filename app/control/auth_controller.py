from flask_login import login_user, logout_user
from flask import session
from app.entity.user_account import UserAccount

class AuthController:
    def login(self, email, password):
        # 1) Check account exists and is active
        user = UserAccount.query.filter_by(email=email).first()
        if not user or not user.isActive:
            return None, "Account not found or suspended."

        # 2) Validate password
        if not user.check_password(password):
            return None, "Invalid credentials."

        # 3) Log in using session cookie only (auto-logout when browser closes)
        login_user(user, remember=False)

        # 4) Determine redirect by role
        role = (user.profile.profileName if user.profile else "").lower()
        if role == "useradmin":
            return "/admin/dashboard", None
        if role in ("csrrep", "csr", "csr representative"):
            return "/csr/dashboard", None
        if role in ("pin", "personinneed", "person-in-need"):
            return "/pin/dashboard", None
        if role in ("platformmanager", "platform"):
            return "/pm/dashboard", None

        return "/", None

    def logout(self):
        # Fully remove session + authentication
        logout_user()
        session.clear()
        return True

