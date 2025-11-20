param(
    [Parameter(Mandatory=$true)]
    [string]$publishDir
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Verificador de Publicacion ASP.NET Core" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $publishDir)) {
    Write-Error "El directorio no existe: $publishDir"
    exit 1
}

Write-Host "Verificando directorio: $publishDir" -ForegroundColor Yellow
Write-Host ""

# Verificar archivos criticos
$criticalFiles = @(
    "web.config",
    "appsettings.json"
)

Write-Host "1. Archivos criticos:" -ForegroundColor Cyan
$missingFiles = @()
foreach ($file in $criticalFiles) {
    $fullPath = Join-Path $publishDir $file
    if (Test-Path $fullPath) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [FALTA] $file" -ForegroundColor Red
        $missingFiles += $file
    }
}
Write-Host ""

# Verificar DLL principal
Write-Host "2. DLL Principal:" -ForegroundColor Cyan
$dllFiles = Get-ChildItem -Path $publishDir -Filter "*.dll" | Where-Object { $_.Name -notlike "Microsoft.*" -and $_.Name -notlike "System.*" }
if ($dllFiles.Count -gt 0) {
    foreach ($dll in $dllFiles | Select-Object -First 3) {
        Write-Host "  [OK] $($dll.Name)" -ForegroundColor Green
    }
    if ($dllFiles.Count -gt 3) {
        Write-Host "  ... y $($dllFiles.Count - 3) mas" -ForegroundColor Gray
    }
} else {
    Write-Host "  [ERROR] No se encontraron DLLs de la aplicacion" -ForegroundColor Red
}
Write-Host ""

# Verificar web.config
Write-Host "3. Configuracion de web.config:" -ForegroundColor Cyan
$webConfigPath = Join-Path $publishDir "web.config"
if (Test-Path $webConfigPath) {
    [xml]$webConfig = Get-Content $webConfigPath
    $aspNetCore = $webConfig.configuration.location.system.webServer.aspNetCore
    
    if ($aspNetCore) {
        Write-Host "  processPath: $($aspNetCore.processPath)" -ForegroundColor Gray
        Write-Host "  arguments: $($aspNetCore.arguments)" -ForegroundColor Gray
        Write-Host "  stdoutLogEnabled: $($aspNetCore.stdoutLogEnabled)" -ForegroundColor Gray
        Write-Host "  stdoutLogFile: $($aspNetCore.stdoutLogFile)" -ForegroundColor Gray
        
        # Verificar que el DLL en arguments existe
        if ($aspNetCore.arguments) {
            $dllName = $aspNetCore.arguments -replace '.*\\(.+\.dll).*', '$1'
            $dllPath = Join-Path $publishDir $dllName
            if (Test-Path $dllPath) {
                Write-Host "  [OK] DLL de inicio existe: $dllName" -ForegroundColor Green
            } else {
                Write-Host "  [ERROR] DLL de inicio no existe: $dllName" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  [ERROR] No se encontro seccion aspNetCore en web.config" -ForegroundColor Red
    }
} else {
    Write-Host "  [ERROR] web.config no existe" -ForegroundColor Red
}
Write-Host ""

# Verificar runtime
Write-Host "4. Runtime requerido:" -ForegroundColor Cyan
$runtimeConfigFiles = Get-ChildItem -Path $publishDir -Filter "*.runtimeconfig.json"
if ($runtimeConfigFiles.Count -gt 0) {
    $runtimeConfig = Get-Content $runtimeConfigFiles[0].FullName | ConvertFrom-Json
    $framework = $runtimeConfig.runtimeOptions.framework
    Write-Host "  Framework: $($framework.name)" -ForegroundColor Gray
    Write-Host "  Version: $($framework.version)" -ForegroundColor Gray
} else {
    Write-Host "  [INFO] No se encontro archivo runtimeconfig.json" -ForegroundColor Yellow
    Write-Host "        (Puede ser deployment autocontenido)" -ForegroundColor Gray
}
Write-Host ""

# Resumen
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($missingFiles.Count -eq 0 -and (Test-Path (Join-Path $publishDir "web.config"))) {
    Write-Host "Archivos basicos: OK" -ForegroundColor Green
} else {
    Write-Host "Archivos basicos: REVISAR" -ForegroundColor Red
}

Write-Host ""
Write-Host "RECOMENDACIONES para error 500.30:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Habilitar logs detallados en web.config:" -ForegroundColor White
Write-Host "   <aspNetCore stdoutLogEnabled='true' stdoutLogFile='.\logs\stdout' />" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Verificar que el servidor tenga instalado:" -ForegroundColor White
Write-Host "   - .NET Runtime correcto (ver version arriba)" -ForegroundColor Gray
Write-Host "   - ASP.NET Core Hosting Bundle" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Crear carpeta 'logs' en el servidor" -ForegroundColor White
Write-Host ""
Write-Host "4. Revisar los logs en el servidor en:" -ForegroundColor White
Write-Host "   .\logs\stdout_*.log" -ForegroundColor Gray
Write-Host ""
