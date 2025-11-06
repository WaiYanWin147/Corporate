"""
User Story:
As a PIN, I want to track the number of views on each of my service requests so that I know the level of interest.
"""
from app.entity.request import Request

class PinTrackViewsController:
    def trackViews(self, request_id:int) -> int:
        r = Request.query.get(request_id)
        return (r.viewCount if r else 0)
