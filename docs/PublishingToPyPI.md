# Publishing a New Version to PyPI

This guide shows how to release a new version of `rrhfoem04-lib` to PyPI from Linux.

## Prerequisites
- PyPI account (and optionally a TestPyPI account)
- API token(s) created in your PyPI/TestPyPI account
- Python 3.12+

## 1. Bump the version
Edit `pyproject.toml`:

```toml
[project]
name = "rrhfoem04-lib"
version = "X.Y.Z"  # <- bump this
```

Commit the change:

```bash
git add pyproject.toml
git commit -m "chore(release): bump version to X.Y.Z"
```

Notes:
- PyPI rejects reusing an existing version. Always bump `X.Y.Z`.
- If you keep a CHANGELOG, update it here.

## 2. Prepare build tools and clean artifacts
```bash
python3 -m pip install --upgrade build twine
rm -rf dist build ./*.egg-info
```

## 3. Build the distributions
```bash
python3 -m build
```
This creates source and wheel artifacts in `dist/`.

Optionally validate metadata:
```bash
python3 -m twine check dist/*
```

## 4. Upload to TestPyPI (recommended first)
Create a TestPyPI token and export it in your shell:
```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-TEST-...your-token..."
python3 -m twine upload --repository testpypi dist/*
```

Verify install from TestPyPI in a clean venv:
```bash
python3 -m venv .venv-test
source .venv-test/bin/activate
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps rrhfoem04-lib==X.Y.Z
python3 -c "import rrhfoem04; print(rrhfoem04.__name__)"
deactivate
```

## 5. Upload to PyPI
Use a real PyPI token:
```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-...your-token..."
python3 -m twine upload dist/*
```

## 6. Tag the release (optional but recommended)
```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

## Troubleshooting
- 400: File already exists — You didn’t bump `version`. Update `pyproject.toml` and rebuild.
- 403/401: Invalid credentials — Ensure the token starts with `pypi-` and you used `__token__` as username.
- README/description rendering issues — `pyproject.toml` already points `readme = "README.md"`.
- Python version constraints — This project sets `requires-python = ">=3.12"`; users on older Python versions cannot install it.
- Missing or extra files — Check `dist/` contents and your package include rules if you customize them.

## Optional: Store credentials in ~/.pypirc
Instead of env vars, create `~/.pypirc`:
```ini
[pypi]
  username = __token__
  password = pypi-...your-token...

[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = pypi-TEST-...your-token...
```
Then upload without exporting env vars:
```bash
python3 -m twine upload dist/*
```
