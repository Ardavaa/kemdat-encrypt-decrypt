## Caesar Encrypt/Decrypt UI (Streamlit)

A simple yet polished Streamlit interface for Caesar cipher based on `encrypt-decrypt.py`.

### Features
- Encrypt or decrypt text with adjustable shift (0-25)
- Input via text area or file upload
- Download processed result as `.txt`
- Live letter frequency charts (input vs output)

### Requirements
- Python >= 3.13
- Dependencies are managed via `pyproject.toml`

### Install

#### Using UV (Recommended)
UV is a fast Python package installer. First, install UV:
```bash
# On Windows
curl -LsSf https://astral.sh/uv/install.ps1 | powershell
# Or via pip
pip install uv
```

Then install dependencies:
```bash
# Install in current environment
uv pip install -e .
# Or create and use a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Using pip
```bash
pip install -r requirements.txt  # if using requirements, or
pip install .  # editable install if packaged, or
pip install streamlit altair  # minimal
```

This repo uses `pyproject.toml` with `streamlit` specified, so you can also run:
```bash
pip install -e .
```

### Run
From the project root:
```bash
streamlit run streamlit_app.py
```

On Windows (PowerShell or Git Bash), the command is the same.

### Notes
- The app dynamically loads functions from `encrypt-decrypt.py`. You can edit that file and refresh the app to apply changes.
- Non-letter characters remain unchanged, and case is preserved.


