@echo off
cd /d "%~dp0backend"
python -m uvicorn api_service.main:app --host 0.0.0.0 --port 8000
