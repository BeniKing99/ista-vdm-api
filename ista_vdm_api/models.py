"""Data models for ista VDM API."""

from dataclasses import dataclass
from datetime import date


@dataclass
class ConsumptionData:
    """Represents consumption data for a single period."""

    period_start: date
    period_end: date
    heating_consumption: float | None
    heating_cost: float | None
    hot_water_consumption: float | None
    hot_water_cost: float | None
    cold_water_consumption: float | None = None
    cold_water_cost: float | None = None

    def __post_init__(self) -> None:
        """Validate data after initialization."""
        if self.period_end < self.period_start:
            raise ValueError("period_end must be after period_start")
