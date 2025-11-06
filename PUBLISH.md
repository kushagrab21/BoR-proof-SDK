# Publishing Guide for BoR-Proof SDK

This guide explains how to publish the BoR-Proof SDK to PyPI.

## Prerequisites

1. Create accounts on PyPI and TestPyPI:
   - PyPI: https://pypi.org/account/register/
   - TestPyPI: https://test.pypi.org/account/register/

2. Install publishing tools:
   ```bash
   pip install build twine
   ```

3. Set up API tokens:
   - Generate an API token at https://pypi.org/manage/account/token/
   - Save it for later use

## Building the Package

Clean previous builds and create new distribution files:

```bash
# Clean previous builds
rm -rf dist build bor_sdk.egg-info

# Build source distribution and wheel
python -m build
```

This creates two files in the `dist/` directory:
- `bor_sdk-1.0.0.tar.gz` (source distribution)
- `bor_sdk-1.0.0-py3-none-any.whl` (wheel distribution)

## Testing on TestPyPI (Recommended First Step)

Before publishing to the real PyPI, test on TestPyPI:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Install from TestPyPI to verify
pip install --index-url https://test.pypi.org/simple/ bor-sdk

# Test the installation
borp --help
```

## Publishing to PyPI

Once verified on TestPyPI, publish to the real PyPI:

```bash
# Upload to PyPI
twine upload dist/*
```

When prompted, enter:
- Username: `__token__`
- Password: Your API token (including the `pyp-` prefix)

## Verifying the Published Package

After publishing, verify the installation:

```bash
# Create a clean virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install bor-sdk

# Verify CLI works
borp --help

# Verify version
python -c "import bor; print('BoR-SDK installed successfully')"
```

## Post-Publication Checklist

- [ ] Package appears on PyPI: https://pypi.org/project/bor-sdk/
- [ ] README renders correctly on PyPI page
- [ ] `pip install bor-sdk` works in clean environment
- [ ] `borp` CLI is available after installation
- [ ] Tag the release on GitHub: `git tag v1.0.0 && git push origin v1.0.0`
- [ ] Create a GitHub release with release notes

## Updating the Package

For future releases:

1. Update version in `pyproject.toml` and `setup.py`
2. Update `CHANGELOG.md` with changes
3. Build and test as described above
4. Publish to PyPI
5. Tag the release on GitHub

## Troubleshooting

**Issue: `twine: command not found`**
```bash
pip install --upgrade twine
```

**Issue: Authentication failed**
- Verify your API token is correct
- Ensure you're using `__token__` as username
- Check token has the right permissions

**Issue: Package already exists**
- You cannot re-upload the same version
- Increment version number in `pyproject.toml` and rebuild

## Security Notes

- **Never commit API tokens** to version control
- Use `.pypirc` file for storing credentials securely (add to `.gitignore`)
- Rotate API tokens periodically
- Use scoped tokens (project-specific) when possible

