@echo off
chcp 65001 >nul
setlocal

REM Genera resultados de válidas, informes y resultados generales (2026)

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

echo.
echo ═══════════════════════════════════════════════════════════
echo   FEDEMOTO - Generacion completa 2026
echo ═══════════════════════════════════════════════════════════
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro Python en PATH.
    pause
    exit /b 1
)

echo [1/4] Generando paginas de resultados de validadas...
python "Resultados_validas\Motocross\Primer semestre\generar_valida_girardota.py" || goto :error
python "Resultados_validas\Motocross\Primer semestre\generar_valida_ii_mx_barranquilla.py" || goto :error
python "Resultados_validas\Velotierra\Primer semestre\generar_valida_vt_tulua.py" || goto :error
python "Resultados_validas\Velotierra\Primer semestre\generar_valida_ii_vt_barcelona.py" || goto :error
python "Resultados_validas\Enduro\Primera valida\generar_valida_enduro_2026.py" || goto :error

echo [2/4] Generando informes por valida...
python "Informes\generar_informes_validas.py" || goto :error
python "Informes\Motocross\Primer semestre\analizar_valida_csv.py" || goto :error
python "Informes\Motocross\Primer semestre\generar_informe_html.py" || goto :error

echo [3/4] Generando resultados generales...
python "Resultados generales\generar_resultados_generales.py" || goto :error

echo [4/4] Proceso finalizado.
echo.
echo [OK] Generacion completada correctamente.
echo.
pause
exit /b 0

:error
echo.
echo [ERROR] El proceso se detuvo por un error.
echo Revisa la salida mostrada arriba.
echo.
pause
exit /b 1
