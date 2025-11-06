"""
User Story:
As a PIN, I want to search my service requests so that I can locate them easily when I have many open service requests.
"""
from app.entity.request import Request

class PinSearchRequestController:
    def searchRequests(self, pin_id:int, keyword:str=None, status:str=None):
        q = Request.query.filter_by(pinID=pin_id)
        if keyword: q = q.filter(Request.title.ilike(f"%{keyword}%"))
        if status: q = q.filter_by(status=status)
        return q.order_by(Request.requestID.desc()).all()
