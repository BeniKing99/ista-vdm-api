"""Data models for ista VDM API."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class ConsumptionData:
    """Represents consumption data for a single period."""
    
    period_start: date
    period_end: date
    heating_consumption: Optional[float]
    heating_cost: Optional[float]
    hot_water_consumption: Optional[float]
    hot_water_cost: Optional[float]
    cold_water_consumption: Optional[float] = None
    cold_water_cost: Optional[float] = None

    def __post_init__(self):
        """Validate data after initialization."""
        if self.period_end < self.period_start:
            raise ValueError("period_end must be after period_start")