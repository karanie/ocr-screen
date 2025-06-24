@setlocal enableextensions
@cd /d "%~dp0"

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

uv python install
uv sync
uv run python setup.py