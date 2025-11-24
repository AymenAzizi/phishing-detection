@echo off
echo ========================================
echo Starting DevSecScan Platform
echo ========================================
echo.
echo Starting API Server on port 8000...
start "DevSecScan API" cmd /k python real_api.py
timeout /t 5
echo.
echo Starting Dashboard on port 3000...
start "DevSecScan Dashboard" cmd /k python dashboard_server.py
timeout /t 3
echo.
echo ========================================
echo Both servers started!
echo ========================================
echo API: http://localhost:8000
echo Dashboard: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Opening dashboard in browser...
timeout /t 2
start http://localhost:3000
echo.
echo Press any key to exit this window...
pause

