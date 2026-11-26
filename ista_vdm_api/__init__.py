"""Ista VDM API Client.

A Python library for accessing the ista VDM (Verbrauchsdatenmanagement) portal.
"""

from .api import IstaVdmAPI, IstaVdmAuthError, IstaVdmConnectionError, IstaVdmError
from .models import ConsumptionData

__version__ = "1.2.0"
__all__ = [
    "IstaVdmAPI",
    "IstaVdmAuthError",
    "IstaVdmConnectionError",
    "IstaVdmError",
    "ConsumptionData",
]
