"""
User Story:
As a Platform Manager, I want to generate daily reports so that I can track daily usage.
+ generateDailyReport(date: date): Report
"""
import json
from datetime import datetime, timedelta
from app import db
from app.entity.report import Report
from app.entity.user_account import UserAccount
from app.entity.request import Request
from app.entity.match_record import MatchRecord
from app.entity.category import Category

class PlatformGenerateDailyReportController:
    def generateDailyReport(self, manager_id: int, day_string: str):
        """
        day_string expected format: 'YYYY-MM-DD'
        """

        # parse the day
        day_start = datetime.strptime(day_string, "%Y-%m-%d")
        next_day = day_start + timedelta(days=1)

        # metrics
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

        # category breakdown
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

        # persist Report row
        report = Report(
            reportTitle=f"Daily Report - {day_string}",
            reportType="daily",
            generatedBy=manager_id,
            period=day_string,
            reportData=json.dumps(data)
        )

        db.session.add(report)
        db.session.commit()
        return report
