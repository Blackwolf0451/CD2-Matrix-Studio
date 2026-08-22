# Building CD2 Matrix Studio

## Requirements

Recommended build environment:

- Windows 10 or Windows 11
- Python 3.12
- Git
- Inno Setup 6 for the installer

## Development environment

From the repository root:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
set PYTHONPATH=src
python main.py
```

## Run tests

```bat
set PYTHONPATH=src
pytest -q
```

## Build portable EXE

The easiest option is:

```bat
build_windows.bat
```

The portable build will appear at:

```text
dist\CD2-Matrix-Studio.exe
```

## Build installer

After the portable EXE exists, compile:

```text
installer\cd2_matrix_studio.iss
```

with Inno Setup 6.

The installer output is configured for:

```text
release\CD2-Matrix-Studio-Setup.exe
```

## GitHub Actions

The repository contains three workflows:

- `ci.yml` — lightweight source/tests checks
- `windows-build.yml` — builds downloadable Windows artifacts
- `release.yml` — publishes EXE + installer when a `v*` tag is pushed

## Release validation

Before tagging a release:

```bat
py -3 tools\check_release.py
```

This verifies that the version matches in:

- Python package
- `pyproject.toml`
- Inno Setup configuration
