@echo off
echo Starting MiniSQL API Server...
start "MiniSQL Backend" cmd /k "python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload"

echo Starting MiniSQL React UI...
cd ui
start "MiniSQL Frontend" cmd /k "npm run dev"

echo Both servers are starting! Wait for the windows to load, then open your browser to the local Vite URL mentioned in the frontend window.
pause
