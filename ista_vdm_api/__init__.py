"""Ista VDM API Client.

A Python library for accessing the ista VDM (Verbrauchsdatenmanagement) portal.
"""

from .api import IstaVdmAPI, IstaVdmAuthError, IstaVdmError
from .models import ConsumptionData

__version__ = "1.1.0"
__all__ = ["IstaVdmAPI", "IstaVdmAuthError", "IstaVdmError", "ConsumptionData"]