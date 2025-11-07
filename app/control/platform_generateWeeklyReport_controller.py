"""
User Story:
As a Platform Manager, I want to generate weekly reports so that I can track usage over a week.
+ generateWeeklyReport(startDate: date): Report
"""

import json
from datetime import datetime, timedelta
from app import db
from app.entity.report import Report
from app.entity.user_account import UserAccount
from app.entity.request import Request
from app.entity.match_record import MatchRecord
from app.entity.category import Category


class PlatformGenerateWeeklyReportController:

    def generateWeeklyReport(self, manager_id: int, start_date_str: str):
        """
        start_date_str expected format: 'YYYY-MM-DD'
        Example: '2025-10-20'
        This will generate a report for the 7-day period starting from start_date_str.
        """

        # Convert input string to datetime
        try:
            week_start = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD for weekly reports.")

        week_end = week_start + timedelta(days=7)

        # General summary
        total_users = UserAccount.query.count()
        total_requests = Request.query.count()
        open_requests = Request.query.filter_by(status="open").count()
        closed_requests = Request.query.filter_by(status="closed").count()

        # Match records completed within the week
        weekly_matches = (
            MatchRecord.query
            .filter(MatchRecord.completedAt >= week_start)
            .filter(MatchRecord.completedAt < week_end)
            .count()
        )

        # Category-level breakdown
        breakdown = {}
        for c in Category.query.all():
            reqs_in_cat = Request.query.filter_by(categoryID=c.categoryID).all()
            breakdown[c.categoryName] = {
                "total_requests": len(reqs_in_cat),
                "open_requests": len([r for r in reqs_in_cat if r.status == "open"]),
                "closed_requests": len([r for r in reqs_in_cat if r.status == "closed"]),
            }

        # Data structure to be stored JSON
        data = {
            "summary": {
                "week_start": week_start.strftime("%Y-%m-%d"),
                "week_end":   week_end.strftime("%Y-%m-%d"),
                "total_users": total_users,
                "total_requests": total_requests,
                "open_requests": open_requests,
                "closed_requests": closed_requests,
                "matches_completed_this_week": weekly_matches,
            },
            "category_breakdown": breakdown
        }

        report = Report(
            reportTitle=f"Weekly Report ({week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')})",
            reportType="weekly",
            generatedBy=manager_id,
            period=start_date_str,
            reportData=json.dumps(data)
        )

        db.session.add(report)
        db.session.commit()
        return report
