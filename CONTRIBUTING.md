# Contributing to ista-vdm-api

First off, thank you for considering contributing to ista-vdm-api! It's people like you that make this library better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what behavior you expected**
- **Include code samples and screenshots if applicable**

Example:
```python
import asyncio
from ista_vdm_api import IstaVdmAPI

async def reproduce_bug():
    api = IstaVdmAPI("test@example.com", "wrong_password")
    await api.authenticate()  # This raises IstaVdmAuthError instead of returning False

asyncio.run(reproduce_bug())
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` for your feature or bug fix
3. Make your changes
4. Ensure tests pass
5. Update documentation if needed
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip
- git

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/BeniKing99/ista-vdm-api.git
cd ista-vdm-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ista_vdm_api --cov-report=html

# Run specific test
pytest tests/test_api.py::test_authenticate
```

### Code Style

We use several tools to ensure code quality:

#### Black (Code Formatting)

```bash
# Format all code
black ista_vdm_api/ tests/

# Check formatting without making changes
black --check ista_vdm_api/ tests/
```

#### mypy (Type Checking)

```bash
# Run type checker
mypy ista_vdm_api/
```

#### ruff (Linting)

```bash
# Check for issues
ruff check ista_vdm_api/ tests/

# Fix auto-fixable issues
ruff check --fix ista_vdm_api/ tests/
```

#### Pre-commit Hooks

We recommend using pre-commit hooks to automatically check code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

### Project Structure

```
ista-vdm-api/
├── ista_vdm_api/          # Main library code
│   ├── __init__.py
│   ├── api.py            # API client
│   └── models.py         # Data models
├── tests/                # Test files
├── docs/                 # Documentation
├── .github/              # GitHub templates and workflows
├── pyproject.toml        # Project configuration
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting (100 character line length)
- Add type hints to all functions and methods
- Write docstrings in [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

Example:
```python
async def get_consumption_data(self) -> list[ConsumptionData]:
    """Get consumption data from ista VDM.
    
    Returns:
        List of ConsumptionData objects
        
    Raises:
        IstaVdmError: If data retrieval fails
    """
    # Implementation
```

### Testing Guidelines

- Write tests for all new functionality
- Aim for high test coverage (>90%)
- Use pytest fixtures for common setup
- Mock external API calls in tests
- Test both success and failure cases

Example test:
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_authenticate_success():
    """Test successful authentication."""
    with patch("ista_vdm_api.api.aiohttp.ClientSession") as mock_session:
        # Setup mock
        mock_response = AsyncMock()
        mock_response.status = 302
        mock_response.headers = {"Location": "https://example.com?code=test_code"}
        
        # Test
        api = IstaVdmAPI("test@example.com", "password")
        result = await api.authenticate()
        
        assert result is True
```

### Documentation

- Update README.md if you change the API
- Add docstrings to all public methods
- Include type hints in docstrings
- Update CHANGELOG.md with your changes

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, missing semi colons, etc)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Build process or auxiliary tool changes

Examples:
```
feat: add support for multiple flats
fix: handle missing consumption data gracefully
docs: update API reference with new methods
test: add tests for authentication retry logic
```

## Release Process

1. Update version in `ista_vdm_api/__init__.py`
2. Update CHANGELOG.md
3. Create a git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will automatically build and publish to PyPI

## Questions?

Feel free to:
- Open an issue for discussion
- Join our Discord server (if available)
- Contact the maintainers

Thank you for contributing! 🎉