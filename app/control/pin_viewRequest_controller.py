"""
User Story:
As a PIN, I want to view my service requests and their details so that I can track their status.
"""
from app.entity.request import Request

class PinViewRequestController:
    def viewRequests(self, pin_id:int):
        """Returns all requests belonging to this PIN."""
        return Request.query.filter_by(pinID=pin_id).order_by(Request.requestID.desc()).all()

    def viewRequestDetails(self, requestID:int):
        """Returns a single request by ID."""
        req = Request.query.get(requestID)
        if not req:
            raise ValueError("Request not found.")
        return req
