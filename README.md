# ista-vdm-api

[![PyPI version](https://badge.fury.io/py/ista-vdm-api.svg)](https://badge.fury.io/py/ista-vdm-api)
[![Python Versions](https://img.shields.io/pypi/pyversions/ista-vdm-api.svg)](https://pypi.org/project/ista-vdm-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

A Python library for accessing the ista VDM (Verbrauchsdatenmanagement) portal.

## Overview

This library provides an asynchronous Python interface to retrieve heating, hot water and cold water consumption data from the Austrian ista VDM portal (https://ista-vdm.at/).

## Features

- 🔄 **Async/Await Support**: Built with `asyncio` and `aiohttp`
- 🔐 **OAuth2 Authentication**: Secure login via Keycloak
- 📊 **Consumption Data**: Retrieve heating, hot water and cold water usage
- 🏠 **Flat Information**: Get address, square meters, and property details
- 🏢 **Multiple Flats**: Access every flat linked to your account
- 📈 **CSV Parsing**: Automatic parsing of consumption reports
- 💾 **Session Management**: Automatic token refresh and session handling
- 📝 **Type Hints**: Fully typed with mypy support

## Installation

```bash
pip install ista-vdm-api
```

## Quick Start

```python
import asyncio
from ista_vdm_api import IstaVdmAPI

async def main():
    async with IstaVdmAPI("your@email.com", "your_password") as api:
        # Authenticate
        await api.authenticate()
        
        # Get consumption data
        consumption_data = await api.get_consumption_data()
        
        for entry in consumption_data:
            print(f"Period: {entry.period_start} to {entry.period_end}")
            print(f"Heating: {entry.heating_consumption} kWh")
            print(f"Hot Water: {entry.hot_water_consumption} m³")
            print(f"Cold Water: {entry.cold_water_consumption} m³")
            print("---")

asyncio.run(main())
```

## Usage Examples

### Basic Usage

```python
from ista_vdm_api import IstaVdmAPI, IstaVdmAuthError, IstaVdmError

async def get_consumption():
    try:
        async with IstaVdmAPI("email@example.com", "password") as api:
            # Authenticate
            success = await api.authenticate()
            print(f"Authentication: {'Success' if success else 'Failed'}")
            
            # Get flat information
            flat_info = await api.get_flat_info()
            print(f"Address: {flat_info['street']} {flat_info['housenumber']}")
            print(f"City: {flat_info['city']}")
            print(f"Square Meters: {flat_info['squaremeter']}")
            
            # Get consumption data
            data = await api.get_consumption_data()
            print(f"Retrieved {len(data)} months of data")
            
    except IstaVdmAuthError as e:
        print(f"Authentication failed: {e}")
    except IstaVdmError as e:
        print(f"API error: {e}")
```

### Working with Consumption Data

```python
from ista_vdm_api import ConsumptionData

async def analyze_consumption():
    async with IstaVdmAPI("email@example.com", "password") as api:
        await api.authenticate()
        
        data = await api.get_consumption_data()
        
        # Calculate totals
        total_heating = sum(
            entry.heating_consumption or 0 
            for entry in data
        )
        total_hot_water = sum(
            entry.hot_water_consumption or 0 
            for entry in data
        )
        
        print(f"Total Heating: {total_heating:.2f} kWh")
        print(f"Total Hot Water: {total_hot_water:.2f} m³")
        
        # Get latest month
        latest = max(data, key=lambda x: x.period_end)
        print(f"Latest period: {latest.period_start} to {latest.period_end}")
        print(f"Latest heating: {latest.heating_consumption} kWh")
```

### Multiple Flats

If your account has more than one flat, `get_flats()` lists them all. Pass a
flat ID to `get_flat_info()` and `get_consumption_data()` to query a specific
flat; without one, the first flat of the account is used.

```python
async def all_flats():
    async with IstaVdmAPI("email@example.com", "password") as api:
        await api.authenticate()

        for flat in await api.get_flats():
            info = await api.get_flat_info(flat["id"])
            data = await api.get_consumption_data(flat["id"])
            print(f"{info['street']} {info['housenumber']}/{info['door']}: {len(data)} months")
```

### Using Custom Session

```python
import aiohttp
from ista_vdm_api import IstaVdmAPI

async def with_custom_session():
    # Create custom session with timeout
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        api = IstaVdmAPI(
            "email@example.com", 
            "password",
            session=session
        )
        
        await api.authenticate()
        data = await api.get_consumption_data()
        # Session will be managed externally
```

## API Reference

### IstaVdmAPI

Main API client class.

#### Constructor

```python
IstaVdmAPI(email: str, password: str, session: aiohttp.ClientSession | None = None)
```

- `email`: Your ista VDM portal email address
- `password`: Your ista VDM portal password
- `session`: Optional aiohttp ClientSession (one will be created if not provided)

#### Methods

##### `authenticate()`

Authenticate with the ista VDM portal.

```python
async def authenticate() -> bool
```

**Returns**: `True` if authentication successful

**Raises**:
- `IstaVdmAuthError`: If the portal rejects the credentials
- `IstaVdmConnectionError`: If the portal cannot be reached or has a server error
- `IstaVdmError`: For other errors

##### `get_consumption_data()`

Retrieve consumption data from the portal.

```python
async def get_consumption_data(flat_id: str | None = None) -> list[ConsumptionData]
```

- `flat_id`: Flat to query (defaults to the first flat of the account)

**Returns**: List of `ConsumptionData` objects

**Raises**:
- `IstaVdmError`: If data retrieval fails

##### `get_flat_info()`

Get information about the flat/property.

```python
async def get_flat_info(flat_id: str | None = None) -> dict | None
```

- `flat_id`: Flat to query (defaults to the first flat of the account)

**Returns**: Dictionary with flat details or `None` if not available

**Example return value**:
```python
{
    'id': '12345',
    'city': 'Vienna',
    'street': 'Test Street',
    'housenumber': '123',
    'door': '4',
    'squaremeter': 56.9,
    'postalcode': '1010',
    'flatnumber': '8',
    'floor': '2',
    'property_id': 'PROP-001'
}
```

##### `get_flats()`

List all flats of the account.

```python
async def get_flats() -> list[dict]
```

**Returns**: List of flat dictionaries with the same keys as `get_flat_info()`.
The values come from the flat list of the portal, so some fields may be `None`;
use `get_flat_info(flat_id)` for the full details of one flat.

#### Properties

- `is_authenticated: bool` - Check if client is authenticated
- `flat_id: str | None` - Get the default (first) flat ID
- `flat_ids: list[str]` - Get the IDs of all flats of the account
- `user_id: str | None` - Get the user ID

### ConsumptionData

Data class representing consumption for a single period.

```python
@dataclass
class ConsumptionData:
    period_start: date
    period_end: date
    heating_consumption: float | None
    heating_cost: float | None
    hot_water_consumption: float | None
    hot_water_cost: float | None
    cold_water_consumption: float | None = None
    cold_water_cost: float | None = None
```

Fields are `None` when the export of a flat has no data for that type (for
example, many flats have no separate cold water meter).

### Exceptions

#### `IstaVdmAuthError`

Raised when the portal rejects the credentials or the session token. Asking the
user for new credentials makes sense only for this error.

#### `IstaVdmError`

General API error (parsing errors, unexpected responses, etc.)

#### `IstaVdmConnectionError`

Subclass of `IstaVdmError`, raised when the portal cannot be reached (network
error, timeout) or answers with a server error (HTTP 5xx). It is temporary, so
retry later with the same credentials.

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/BeniKing99/ista-vdm-api.git
cd ista-vdm-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ista_vdm_api --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

### Code Quality

```bash
# Format code with black
black ista_vdm_api/ tests/

# Check with mypy
mypy ista_vdm_api/

# Lint with ruff
ruff check ista_vdm_api/ tests/

# Fix auto-fixable issues
ruff check --fix ista_vdm_api/ tests/
```

## Supported Regions

This library is designed for the **Austrian ista VDM portal** (https://ista-vdm.at/).

It may work with other regional portals if they use the same API structure, but this is not guaranteed.

## Data Privacy

- All communication is done over HTTPS
- Credentials are only used for authentication and are not stored or logged
- No data is sent to third parties
- The library only accesses data that is already available to you through the web portal

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure:
- Code follows the existing style (Black formatting)
- Type hints are included
- Tests pass (`pytest`)
- Mypy type checking passes (`mypy`)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial library and is not affiliated with or endorsed by ista SE. Use at your own risk. Always verify the data with your official ista VDM portal.

## Changelog

### 1.0.0 (2025-02-10)

- Initial release
- OAuth2 authentication support
- Consumption data retrieval
- Flat information access
- CSV parsing
- Full async/await support
- Type hints and mypy compliance

## Support

- [GitHub Issues](https://github.com/BeniKing99/ista-vdm-api/issues)
- [PyPI Project](https://pypi.org/project/ista-vdm-api/)

## Related Projects

- [Home Assistant Integration](https://github.com/BeniKing99/ista-vdm-homeassistant) - Home Assistant custom component using this library

---

Made with ❤️ for the Home Assistant community