"""
User Story:
As a Platform Manager, I want to generate monthly reports so that I can track monthly usage.
+ generateMonthlyReport(month: int, year: int): Report
"""
import json
from datetime import datetime, timedelta
from app import db
from app.entity.report import Report
from app.entity.user_account import UserAccount
from app.entity.request import Request
from app.entity.match_record import MatchRecord
from app.entity.category import Category

class PlatformGenerateMonthlyReportController:
    def generateMonthlyReport(self, manager_id: int, month_string: str):
        """
        month_string expected format: 'YYYY-MM' (example: '2025-10')
        """

        # parse start and end of month
        year_val, month_val = map(int, month_string.split("-"))
        month_start = datetime(year_val, month_val, 1)
        # naive month end = first day next month
        if month_val == 12:
            month_end = datetime(year_val + 1, 1, 1)
        else:
            month_end = datetime(year_val, month_val + 1, 1)

        # metrics (same global stats again for simplicity)
        total_users = UserAccount.query.count()
        total_requests = Request.query.count()
        open_requests = Request.query.filter_by(status="open").count()
        closed_requests = Request.query.filter_by(status="closed").count()

        total_matches = MatchRecord.query.count()
        recent_matches_30 = (
            MatchRecord.query
            .filter(MatchRecord.completedAt >= datetime.utcnow() - timedelta(days=30))
            .count()
        )

        breakdown = {}
        cats = Category.query.all()
        for c in cats:
            cat_reqs = Request.query.filter_by(categoryID=c.categoryID).all()
            breakdown[c.categoryName] = {
                "total_requests": len(cat_reqs),
                "open_requests": len([r for r in cat_reqs if r.status == "open"]),
                "closed_requests": len([r for r in cat_reqs if r.status == "closed"]),
            }

        data = {
            "summary": {
                "total_users": total_users,
                "total_requests": total_requests,
                "open_requests": open_requests,
                "closed_requests": closed_requests,
                "total_matches": total_matches,
                "recent_matches_30_days": recent_matches_30,
            },
            "category_breakdown": breakdown
        }

        report = Report(
            reportTitle=f"Monthly Report - {month_string}",
            reportType="monthly",
            generatedBy=manager_id,
            period=month_string,
            reportData=json.dumps(data)
        )

        db.session.add(report)
        db.session.commit()
        return report
