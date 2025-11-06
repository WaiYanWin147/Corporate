"""
User Story:
As a PIN, I want to update my service request so that I can change details if necessary.
UML: + updateRequest(requestID: int, newRequestID: int, userID: int,
                     categoryID: int, title: string, description: string): boolean
"""
from app import db
from app.entity.request import Request

class PinUpdateRequestController:
    def updateRequest(self,
                      requestID: int,
                      newRequestID: int | None,
                      userID: int,
                      categoryID: int | None,
                      title: str | None,
                      description: str | None,
                      status: str | None = None) -> bool:
        # get the request
        r = Request.query.get(requestID)
        if not r:
            raise ValueError("Request not found.")

        # ownership check
        if r.pinID != userID:
            raise PermissionError("Not authorized to edit this request.")

        # handle newRequestID (rare IRL but UML demands)
        if newRequestID and newRequestID != r.requestID:
            # make sure we don't collide
            if Request.query.get(newRequestID):
                raise ValueError("That request ID is already in use.")
            r.requestID = newRequestID

        # update fields if provided
        if categoryID is not None:
            r.categoryID = categoryID
        if title:
            r.title = title
        if description:
            r.description = description
        if status:
            r.status = status  # e.g. "Open", "Draft"

        db.session.commit()
        return True
