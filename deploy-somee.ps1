param(
    [Parameter(Mandatory=$true)]
    [string]$publishDir,
    
    [Parameter(Mandatory=$true)]
    [string]$Env,
    
    [Parameter(Mandatory=$true)]
    [string]$Password
)

$ErrorActionPreference = "Stop"

# Leer configuracion
$configFile = Join-Path $PSScriptRoot "deploy-settings.json"
if (-not (Test-Path $configFile)) {
    Write-Error "No se encontro el archivo deploy-settings.json"
    exit 1
}

$config = Get-Content $configFile | ConvertFrom-Json
$envConfig = $config.environments.$Env

if (-not $envConfig) {
    Write-Error "Entorno '$Env' no encontrado en deploy-settings.json"
    exit 1
}

$ftpHost = $envConfig.ftpHost
$ftpUser = $envConfig.ftpUser
$remoteRoot = $envConfig.remoteRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando deployment a $Env" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Directorio: $publishDir" -ForegroundColor Gray
Write-Host "Host FTP: $ftpHost" -ForegroundColor Gray
Write-Host "Usuario: $ftpUser" -ForegroundColor Gray
Write-Host "Ruta remota: $remoteRoot" -ForegroundColor Gray
Write-Host ""

# Verificar credenciales FTP
Write-Host "Verificando conexion FTP..." -ForegroundColor Yellow
try {
    $testUri = "ftp://$ftpHost/"
    $testRequest = [System.Net.FtpWebRequest]::Create($testUri)
    $testRequest.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory
    $testRequest.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $Password)
    $testRequest.UseBinary = $true
    $testRequest.KeepAlive = $false
    $testRequest.Timeout = 30000
    
    $testResponse = $testRequest.GetResponse()
    $testResponse.Close()
    Write-Host "Conexion FTP exitosa!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Error "Error al conectar con FTP: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Posibles causas:" -ForegroundColor Yellow
    Write-Host "  1. Usuario o contrasena incorrectos" -ForegroundColor Gray
    Write-Host "  2. Host FTP incorrecto" -ForegroundColor Gray
    Write-Host "  3. El servidor FTP no esta disponible" -ForegroundColor Gray
    Write-Host "  4. Firewall bloqueando la conexion" -ForegroundColor Gray
    exit 1
}

# Verificar directorio de publicacion
if ([System.IO.Path]::IsPathRooted($publishDir)) {
    $fullPublishPath = $publishDir
} else {
    $fullPublishPath = Join-Path $PSScriptRoot $publishDir
}

if (-not (Test-Path $fullPublishPath)) {
    Write-Error "No existe el directorio de publicacion: $fullPublishPath"
    exit 1
}

Write-Host "Ruta completa: $fullPublishPath" -ForegroundColor Gray
Write-Host ""

# Funcion para crear directorio remoto
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
        $request.Timeout = 30000
        
        $response = $request.GetResponse()
        $response.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Funcion para subir archivo
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
        $request.Timeout = 60000
        
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
        $errorMsg = $_.Exception.Message
        if ($_.Exception.InnerException) {
            $errorMsg += " | " + $_.Exception.InnerException.Message
        }
        Write-Host "    ERROR: $errorMsg" -ForegroundColor Red
        return $false
    }
}

# Funcion para subir directorio recursivamente
function Upload-Directory {
    param(
        [string]$localDir,
        [string]$ftpUri,
        [string]$username,
        [string]$password,
        [string]$remoteDir,
        [string]$baseLocalDir
    )
    
    if ($remoteDir -ne "/") {
        Ensure-RemoteDirectory -ftpUri $ftpUri -username $username -password $password -remotePath $remoteDir | Out-Null
    }
    
    $files = Get-ChildItem -Path $localDir -File
    $fileCount = 0
    
    foreach ($file in $files) {
        $fileCount++
        $relativePath = $file.FullName.Substring($baseLocalDir.Length).Replace("\", "/")
        $remotePath = $remoteDir + "/" + $file.Name
        
        $fileSizeMB = [math]::Round($file.Length / 1MB, 2)
        Write-Host "[$fileCount] Subiendo: $relativePath ($fileSizeMB MB)" -ForegroundColor Yellow
        
        $success = Upload-File -localFile $file.FullName -ftpUri $ftpUri -username $username -password $password -remotePath $remotePath
        
        if ($success) {
            Write-Host "    OK" -ForegroundColor Green
        }
    }
    
    $dirs = Get-ChildItem -Path $localDir -Directory
    foreach ($dir in $dirs) {
        $newRemoteDir = $remoteDir + "/" + $dir.Name
        Upload-Directory -localDir $dir.FullName -ftpUri $ftpUri -username $username -password $password -remoteDir $newRemoteDir -baseLocalDir $baseLocalDir
    }
}

# Iniciar subida
$ftpUri = "ftp://$ftpHost"

Write-Host "Subiendo archivos..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Creando carpeta logs en el servidor..." -ForegroundColor Yellow
Ensure-RemoteDirectory -ftpUri $ftpUri -username $ftpUser -password $Password -remotePath ($remoteRoot + "/logs") | Out-Null

Upload-Directory -localDir $fullPublishPath -ftpUri $ftpUri -username $ftpUser -password $Password -remoteDir $remoteRoot -baseLocalDir $fullPublishPath

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment completado!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Archivos subidos exitosamente" -ForegroundColor Gray
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "  - Carpeta 'logs' creada en el servidor" -ForegroundColor Gray
Write-Host "  - Revisar logs en el servidor si hay errores" -ForegroundColor Gray
Write-Host "  - Asegurarse que .NET Runtime este instalado" -ForegroundColor Gray
Write-Host ""
