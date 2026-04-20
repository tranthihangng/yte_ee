from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_cases: int
    today_cases: int
    avg_accuracy: float
    active_modules: int


class MetricBar(BaseModel):
    label: str
    value: float


class DashboardPerformance(BaseModel):
    donut_value: float
    metrics: list[MetricBar]
