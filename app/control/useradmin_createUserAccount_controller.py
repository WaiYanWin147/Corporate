"""
User Story:
As a user admin, I want to create user account so that new users can access the platform.
"""
from app import db
from app.entity.user_account import UserAccount
from app.entity.user_profile import UserProfile


class UserAdminCreateUserAccountController:
    def createUserAccount(self, name: str, email: str, password: str,
                          age: int, phoneNumber: str, profileID: int) -> bool:
        """Creates a new user account and returns True if successful."""

        # verify profile exists
        profile = UserProfile.query.filter_by(profileID=profileID, isActive=True).first()
        if not profile:
            raise ValueError(f"Profile ID '{profileID}' not found or inactive.")

        # prevent duplicate emails
        if UserAccount.query.filter_by(email=email).first():
            raise ValueError(f"Email '{email}' already exists.")

        try:
            user = UserAccount(
                name=name,
                email=email,
                age=age,
                phoneNumber=phoneNumber,   # ensure correct field name
                profileID=profileID,
            )

            # assign password (hash handled in property setter)
            user.password = password

            db.session.add(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to create user account: {e}")
