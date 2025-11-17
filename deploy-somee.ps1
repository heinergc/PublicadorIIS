param(
    [Parameter(Mandatory=$true)]
    [string]$publishDir,
    
    [Parameter(Mandatory=$true)]
    [string]$Env,
    
    [Parameter(Mandatory=$true)]
    [string]$Password
)

$ErrorActionPreference = "Stop"

# Leer configuración
$configFile = Join-Path $PSScriptRoot "deploy-settings.json"
if (-not (Test-Path $configFile)) {
    Write-Error "❌ No se encontró el archivo deploy-settings.json"
    exit 1
}

$config = Get-Content $configFile | ConvertFrom-Json
$envConfig = $config.environments.$Env

if (-not $envConfig) {
    Write-Error "❌ Entorno '$Env' no encontrado en deploy-settings.json"
    exit 1
}

$ftpHost = $envConfig.ftpHost
$ftpUser = $envConfig.ftpUser
$remoteRoot = $envConfig.remoteRoot

Write-Host "🚀 Iniciando deployment a $Env..." -ForegroundColor Cyan
Write-Host "📁 Directorio: $publishDir" -ForegroundColor Gray
Write-Host "🌐 Host FTP: $ftpHost" -ForegroundColor Gray
Write-Host "👤 Usuario: $ftpUser" -ForegroundColor Gray
Write-Host "📂 Ruta remota: $remoteRoot" -ForegroundColor Gray
Write-Host ""

# Verificar directorio de publicación
$fullPublishPath = Join-Path $PSScriptRoot $publishDir
if (-not (Test-Path $fullPublishPath)) {
    Write-Error "❌ No existe el directorio de publicación: $fullPublishPath"
    exit 1
}

# Función para crear directorio remoto
function Ensure-RemoteDirectory {
    param(
        [string]$ftpUri,
        [string]$username,
        [string]$password,
        [string]$remotePath
    )
    
    try {
        $request = [System.Net.FtpWebRequest]::Create($ftpUri + $remotePath)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::MakeDirectory
        $request.Credentials = New-Object System.Net.NetworkCredential($username, $password)
        $request.UseBinary = $true
        $request.KeepAlive = $false
        
        $response = $request.GetResponse()
        $response.Close()
        return $true
    }
    catch {
        # El directorio puede ya existir
        return $false
    }
}

# Función para subir archivo
function Upload-File {
    param(
        [string]$localFile,
        [string]$ftpUri,
        [string]$username,
        [string]$password,
        [string]$remotePath
    )
    
    try {
        $remoteUrl = $ftpUri + $remotePath
        $request = [System.Net.FtpWebRequest]::Create($remoteUrl)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
        $request.Credentials = New-Object System.Net.NetworkCredential($username, $password)
        $request.UseBinary = $true
        $request.KeepAlive = $false
        
        $fileContent = [System.IO.File]::ReadAllBytes($localFile)
        $request.ContentLength = $fileContent.Length
        
        $requestStream = $request.GetRequestStream()
        $requestStream.Write($fileContent, 0, $fileContent.Length)
        $requestStream.Close()
        
        $response = $request.GetResponse()
        $response.Close()
        
        return $true
    }
    catch {
        Write-Host "❌ Error subiendo $remotePath : $_" -ForegroundColor Red
        return $false
    }
}

# Función para subir directorio recursivamente
function Upload-Directory {
    param(
        [string]$localDir,
        [string]$ftpUri,
        [string]$username,
        [string]$password,
        [string]$remoteDir,
        [string]$baseLocalDir
    )
    
    # Crear directorio remoto
    if ($remoteDir -ne "/") {
        Ensure-RemoteDirectory -ftpUri $ftpUri -username $username -password $password -remotePath $remoteDir | Out-Null
    }
    
    # Subir archivos
    $files = Get-ChildItem -Path $localDir -File
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($baseLocalDir.Length).Replace("\", "/")
        $remotePath = $remoteDir + "/" + $file.Name
        
        Write-Host "📤 Subiendo: $relativePath" -ForegroundColor Yellow
        
        $success = Upload-File -localFile $file.FullName -ftpUri $ftpUri -username $username -password $password -remotePath $remotePath
        
        if ($success) {
            Write-Host "   ✅ OK" -ForegroundColor Green
        }
    }
    
    # Procesar subdirectorios
    $dirs = Get-ChildItem -Path $localDir -Directory
    foreach ($dir in $dirs) {
        $newRemoteDir = $remoteDir + "/" + $dir.Name
        Upload-Directory -localDir $dir.FullName -ftpUri $ftpUri -username $username -password $password -remoteDir $newRemoteDir -baseLocalDir $baseLocalDir
    }
}

# Iniciar subida
$ftpUri = "ftp://$ftpHost"

Write-Host "🔄 Subiendo archivos..." -ForegroundColor Cyan
Write-Host ""

Upload-Directory -localDir $fullPublishPath -ftpUri $ftpUri -username $ftpUser -password $Password -remoteDir $remoteRoot -baseLocalDir $fullPublishPath

Write-Host ""
Write-Host "✅ Deployment completado exitosamente!" -ForegroundColor Green
