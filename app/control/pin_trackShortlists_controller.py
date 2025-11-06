"""
User Story:
As a PIN, I want to track the number of times my service requests are shortlisted so that I know how many CSR Reps are considering it.
"""
from app.entity.request import Request

class PinTrackShortlistsController:
    def trackShortlists(self, request_id:int) -> int:
        r = Request.query.get(request_id)
        return (r.shortlistCount if r else 0)
