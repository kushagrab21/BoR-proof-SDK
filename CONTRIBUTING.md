# Contributing to BoR-Proof SDK

Thank you for your interest in contributing! This document provides guidelines for contributing to the BoR-Proof SDK.

## Development Setup

### Quick Start

```bash
# Clone the repository
git clone https://github.com/kushagrab21/BoR-proof-SDK.git
cd BoR-proof-SDK

# Setup development environment
make setup

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
coverage run -m pytest
coverage report
```

### Code Quality

We use automated tools to maintain code quality:

```bash
# Check code style
make lint

# Auto-format code
make fmt

# Run all checks (lint + test)
make check
```

### Pre-commit Hooks

Pre-commit hooks automatically run before each commit:

- **black**: Code formatting
- **ruff**: Linting
- **isort**: Import sorting

Install with:
```bash
pre-commit install
```

Run manually:
```bash
pre-commit run --all-files
```

## Development Workflow

1. **Create a branch** for your feature or bugfix
2. **Make changes** with tests
3. **Run checks** locally: `make check`
4. **Commit** your changes (pre-commit hooks will run)
5. **Push** and create a Pull Request

## Testing Your Changes

```bash
# Generate proof bundle
make prove

# Verify bundle
make verify

# Run self-audit
make audit

# Build consensus ledger
make consensus

# Full demo (prove + verify)
make demo
```

## CI/CD

All pull requests run through GitHub Actions CI:
- Linting (ruff, black, isort)
- Test suite (pytest)
- Coverage report

## Code Style

- Line length: 100 characters
- Python version: 3.11+
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for public functions

## Adding New Features

1. Add tests in `tests/`
2. Update documentation if needed
3. Ensure backward compatibility
4. Run full test suite: `make check`

## Questions?

Open an issue on GitHub: https://github.com/kushagrab21/BoR-proof-SDK/issues
