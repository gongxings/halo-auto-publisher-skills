@echo off
echo ========================================
echo Cairo Environment Checker
echo ========================================
echo.

REM 检查cairosvg模块
python -c "import cairosvg; print('[+] cairosvg module found')" 2>nul || (
    echo [!] cairosvg module not found
    echo     Install with: pip install cairosvg
    goto :end
)

REM 检查cairo库
echo [*] Checking cairo library...
python -c "import cairosvg; import io; cairosvg.svg2png(bytestring=b'<svg width=\"1\" height=\"1\"></svg>', write_to=io.BytesIO()); print('[+] cairo works!')" 2>nul || (
    echo [!] cairo library not found or not working
    echo.
    echo Please install cairo using one of these methods:
    echo.
    echo 1. MSYS2 (recommended):
    echo    - Download from https://www.msys2.org/
    echo    - Run: pacman -S mingw-w64-ucrt-x86_64-cairo
    echo    - Add C:\msys64\ucrt64\bin to PATH
    echo.
    echo 2. GTK3 bundle:
    echo    - Download from https://github.com/wingtk/gvsbuild/releases
    echo    - Extract to a folder
    echo    - Set CAIRO_LIBRARY_PATH to that folder\bin
    echo.
    echo 3. Conda:
    echo    - conda install -c conda-forge cairo
    echo.
    goto :end
)

echo.
echo [+] All good! cairosvg is fully functional.
echo.

:end
pause
