@echo off
echo Compiling LaTeX report...
echo.

REM Check if pdflatex is available
where pdflatex >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: pdflatex not found. Please install MiKTeX or TeX Live.
    echo Download from: https://miktex.org/ or https://www.tug.org/texlive/
    pause
    exit /b 1
)

REM Compile the LaTeX document
echo Running pdflatex (first pass)...
pdflatex -interaction=nonstopmode report.tex
if %errorlevel% neq 0 (
    echo ERROR: First pdflatex run failed.
    pause
    exit /b 1
)

echo Running pdflatex (second pass)...
pdflatex -interaction=nonstopmode report.tex
if %errorlevel% neq 0 (
    echo ERROR: Second pdflatex run failed.
    pause
    exit /b 1
)

echo.
echo SUCCESS: LaTeX report compiled successfully!
echo Output file: report.pdf
echo.

REM Clean up auxiliary files
echo Cleaning up auxiliary files...
del *.aux *.log *.toc *.out 2>nul

echo.
echo Report compilation complete!
pause
