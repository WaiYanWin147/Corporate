"""
User Story:
As a CSR Rep, I want to view the history of services by service type so that I can track contributions by category.
"""
from app.entity.match_record import MatchRecord

class CsrViewHistoryController:
    def viewHistoryByService(self, csrID:int, categoryID:int):
        """Returns all match records for a CSR filtered by category."""
        return MatchRecord.query.filter_by(
            csrRepID=csrID,
            categoryID=categoryID
        ).order_by(MatchRecord.matchRecordID.desc()).all()
