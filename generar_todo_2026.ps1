[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  FEDEMOTO - Generación completa 2026" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

function Invoke-Step {
    param(
        [string]$Label,
        [string[]]$ScriptArgs
    )
    Write-Host $Label -ForegroundColor Yellow
    & python @ScriptArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Error ejecutando: python $($ScriptArgs -join ' ')"
    }
}

try {
    Invoke-Step "[1/4] Generando páginas de resultados de válidas..." @("Resultados_validas\Motocross\Primer semestre\generar_valida_girardota.py")
    Invoke-Step "" @("Resultados_validas\Motocross\Primer semestre\generar_valida_ii_mx_barranquilla.py")
    Invoke-Step "" @("Resultados_validas\Velotierra\Primer semestre\generar_valida_vt_tulua.py")
    Invoke-Step "" @("Resultados_validas\Velotierra\Primer semestre\generar_valida_ii_vt_barcelona.py")
    Invoke-Step "" @("Resultados_validas\Enduro\Primera valida\generar_valida_enduro_2026.py")

    Invoke-Step "[2/4] Generando informes por válida..." @("Informes\generar_informes_validas.py")
    Invoke-Step "" @("Informes\Motocross\Primer semestre\analizar_valida_csv.py")
    Invoke-Step "" @("Informes\Motocross\Primer semestre\generar_informe_html.py")

    Invoke-Step "[3/4] Generando resultados generales..." @("Resultados generales\generar_resultados_generales.py")

    Write-Host ""
    Write-Host "[4/4] Proceso finalizado." -ForegroundColor Green
    Write-Host "[OK] Generación completada correctamente." -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "[ERROR] El proceso se detuvo por un error." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}
