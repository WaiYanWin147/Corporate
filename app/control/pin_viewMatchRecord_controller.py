"""
User Story:
As a PIN, I want to view my completed service matches so that I can keep track of past support received.
"""
from app.entity.match_record import MatchRecord

class PinViewMatchRecordController:
    def viewCompletedRecords(self, pin_id: int):
        """
        Returns all completed MatchRecord entries for this PIN user.
        Args:
            pin_id (int): Logged-in Person-In-Need user ID
        Returns:
            list[MatchRecord]: Completed match records
        """
        return (
            MatchRecord.query
            .filter_by(pinID=pin_id, status="completed")
            .order_by(MatchRecord.matchRecordID.desc())
            .all()
        )
