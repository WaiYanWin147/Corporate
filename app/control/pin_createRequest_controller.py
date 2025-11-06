"""
User Story:
As a PIN, I want to create a service request so that I can get assistance.
"""
from app import db
from app.entity.request import Request

class PinCreateRequestController:
    def createRequest(self, requestID:int=None, userID:int=None, categoryID:int=None,
                      title:str=None, description:str=None) -> bool:
        """Creates a new service request (UML-aligned). Returns True if successful."""
        if not (userID and categoryID and title and description):
            raise ValueError("Missing required fields.")

        try:
            new_request = Request(
                pinID=userID,
                categoryID=categoryID,
                title=title,
                description=description,
                status="open"
            )
            db.session.add(new_request)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to create request: {e}")
