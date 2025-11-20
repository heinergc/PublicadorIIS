param(
    [Parameter(Mandatory=$true)]
    [string]$publishDir
)

$webConfigPath = Join-Path $publishDir "web.config"

if (-not (Test-Path $publishDir)) {
    Write-Error "El directorio no existe: $publishDir"
    exit 1
}

# Buscar el DLL principal
$mainDll = Get-ChildItem -Path $publishDir -Filter "*.dll" | 
    Where-Object { $_.Name -like "*App*.dll" -or $_.Name -like "*Web*.dll" } |
    Select-Object -First 1

if (-not $mainDll) {
    $mainDll = Get-ChildItem -Path $publishDir -Filter "*.dll" | 
        Where-Object { $_.Name -notlike "Microsoft.*" -and $_.Name -notlike "System.*" } |
        Select-Object -First 1
}

if (-not $mainDll) {
    Write-Error "No se pudo encontrar el DLL principal de la aplicacion"
    exit 1
}

$dllName = $mainDll.Name

Write-Host "Generando web.config para: $dllName" -ForegroundColor Cyan
Write-Host ""

# Crear backup si existe
if (Test-Path $webConfigPath) {
    $backupPath = $webConfigPath + ".backup"
    Copy-Item $webConfigPath $backupPath -Force
    Write-Host "Backup creado: $backupPath" -ForegroundColor Yellow
}

# Crear nuevo web.config
$webConfigContent = @"
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" resourceType="Unspecified" />
    </handlers>
    <aspNetCore processPath="dotnet" 
                arguments=".\$dllName" 
                stdoutLogEnabled="true" 
                stdoutLogFile=".\logs\stdout" 
                hostingModel="inprocess">
      <environmentVariables>
        <environmentVariable name="ASPNETCORE_ENVIRONMENT" value="Production" />
      </environmentVariables>
    </aspNetCore>
    <httpProtocol>
      <customHeaders>
        <add name="Content-Language" value="es-ES" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
"@

Set-Content -Path $webConfigPath -Value $webConfigContent -Encoding UTF8

Write-Host "[OK] web.config generado correctamente" -ForegroundColor Green
Write-Host ""
Write-Host "Contenido:" -ForegroundColor Cyan
Write-Host $webConfigContent -ForegroundColor Gray
Write-Host ""
Write-Host "IMPORTANTE: Crear carpeta 'logs' en el servidor!" -ForegroundColor Yellow
