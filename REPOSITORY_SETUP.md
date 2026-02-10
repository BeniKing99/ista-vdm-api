# Repository Setup Guide

Complete guide for setting up and publishing the ista-vdm-api library.

## 📁 Repository Structure

```
ista-vdm-api/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Continuous Integration
│   │   └── publish.yml         # PyPI Publishing
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
├── ista_vdm_api/               # Main package
│   ├── __init__.py
│   ├── api.py
│   ├── models.py
│   └── py.typed                # PEP 561 marker
├── tests/                      # Test suite (create this)
│   ├── __init__.py
│   ├── test_api.py
│   └── test_models.py
├── pyproject.toml             # Modern Python packaging
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
└── .gitignore
```

## 🚀 Quick Start for Repository Setup

### 1. Create GitHub Repository

```bash
# Create new repository on GitHub
# https://github.com/new
# Repository name: ista-vdm-api

# Clone locally
git clone https://github.com/BeniKing99/ista-vdm-api.git
cd ista-vdm-api

# Copy all files into this directory
cp -r /path/to/ista-vdm-api/* .

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Build artifacts
*.whl
*.tar.gz

# Version file (auto-generated)
ista_vdm_api/_version.py
EOF

# Initial commit
git add .
git commit -m "Initial commit: ista-vdm-api library"
git push origin main
```

### 2. Set Up PyPI Account and API Token

1. **Create PyPI Account**:
   - Go to https://pypi.org/account/register/
   - Verify your email

2. **Create API Token**:
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Name: `ista-vdm-api-github-actions`
   - Scope: Entire account (or specific project after first upload)
   - Copy the token (starts with `pypi-`)

3. **Add Token to GitHub Secrets**:
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste your PyPI token
   - Click "Add secret"

### 3. Install Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Verify installation
python -c "from ista_vdm_api import IstaVdmAPI; print('✓ Installation successful')"
```

### 4. Run Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ista_vdm_api --cov-report=html

# Open coverage report
# Linux/macOS: open htmlcov/index.html
# Windows: start htmlcov/index.html
```

### 5. Code Quality Checks

```bash
# Format code
black ista_vdm_api/

# Check types
mypy ista_vdm_api/

# Lint
ruff check ista_vdm_api/

# Fix auto-fixable issues
ruff check --fix ista_vdm_api/
```

## 📦 Publishing to PyPI

### Method 1: Automatic (via GitHub Release)

1. **Update Version**:
   ```bash
   # Update version in ista_vdm_api/__init__.py
   __version__ = "1.0.0"
   ```

2. **Update Changelog**:
   ```bash
   # Edit CHANGELOG.md with release notes
   ```

3. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Release version 1.0.0"
   git push origin main
   ```

4. **Create Release on GitHub**:
   - Go to GitHub repository
   - Click "Releases" → "Create a new release"
   - Tag version: `v1.0.0`
   - Release title: `Version 1.0.0`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"

5. **GitHub Actions Will**:
   - Automatically build the package
   - Upload to PyPI using your token
   - Verify at: https://pypi.org/project/ista-vdm-api/

### Method 2: Manual (for testing)

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check the distribution
twine check dist/*

# Upload to TestPyPI (recommended for testing)
twine upload --repository testpypi dist/*

# If everything looks good, upload to real PyPI
twine upload dist/*
```

## 🔧 Setting Up TestPyPI (Optional)

For testing uploads:

1. Create account at https://test.pypi.org/
2. Create API token
3. Configure `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-real-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token
```

## 🔄 Updating the Library

### Patch Release (1.0.1)

```bash
# Fix bugs
# Update CHANGELOG.md
git add .
git commit -m "Fix: description of fix"
git push origin main

# Create release v1.0.1 on GitHub
```

### Minor Release (1.1.0)

```bash
# Add features
# Update CHANGELOG.md
# Update __version__ = "1.1.0"
git add .
git commit -m "feat: description of feature"
git push origin main

# Create release v1.1.0 on GitHub
```

### Major Release (2.0.0)

```bash
# Breaking changes
# Update CHANGELOG.md
# Update __version__ = "2.0.0"
git add .
git commit -m "BREAKING CHANGE: description"
git push origin main

# Create release v2.0.0 on GitHub
```

## 📋 Pre-Publish Checklist

Before creating a release, ensure:

- [ ] Version updated in `ista_vdm_api/__init__.py`
- [ ] CHANGELOG.md updated with release notes
- [ ] All tests pass (`pytest`)
- [ ] Code formatted (`black`)
- [ ] Type checking passes (`mypy`)
- [ ] Linting passes (`ruff`)
- [ ] Documentation updated if needed
- [ ] GitHub Secrets has `PYPI_API_TOKEN`

## 🐛 Troubleshooting

### Build Fails

```bash
# Clean build artifacts
rm -rf build/ dist/ *.egg-info

# Rebuild
python -m build
```

### Import Errors

```bash
# Reinstall in development mode
pip install -e ".[dev]" --force-reinstall
```

### Tests Fail

```bash
# Check test dependencies
pip install pytest pytest-asyncio pytest-aiohttp

# Run with verbose output
pytest -v
```

### PyPI Upload Fails

1. Check token is correct
2. Verify token has upload permissions
3. Ensure version number is unique (not already on PyPI)

## 📝 Additional Files to Consider

### SECURITY.md

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities by emailing security@your-email.com
```

### CODE_OF_CONDUCT.md

Use GitHub's template:
- Go to repository Insights → Community → Code of conduct
- Click "Propose" and select "Contributor Covenant"

## 🎉 Success!

After setup, your repository will:
- ✅ Automatically run tests on every PR
- ✅ Check code quality (black, mypy, ruff)
- ✅ Publish to PyPI on every GitHub release
- ✅ Have proper issue templates
- ✅ Be ready for community contributions

## 📚 Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Documentation](https://docs.pypi.org/)
- [SemVer Specification](https://semver.org/)