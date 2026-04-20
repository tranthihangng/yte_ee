from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_cases: int
    today_cases: int
    average_accuracy: float
    active_modules: int
    search_matches: list[dict[str, Any]] = []
    performance: dict[str, float]
    quick_tips: list[str]
    notifications: list[dict[str, Any]]


class RecentCaseItem(BaseModel):
    id: int
    case_code: str
    module_type: str
    created_at: datetime
    predicted_label: str | None = None
    status: str
    confidence: float | None = None


class RecentCasesResponse(BaseModel):
    items: list[RecentCaseItem]
