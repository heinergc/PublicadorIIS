# Solución Error 500.30 - ASP.NET Core App Failed to Start

## ✅ Pasos ya realizados

1. **web.config corregido** con la configuración correcta
2. **Carpeta logs** se creará automáticamente en el servidor
3. **Logs habilitados** para diagnóstico

## 🔧 Soluciones por orden de prioridad

### 1. Verificar .NET Runtime en Somee.com

**Problema:** Somee.com puede no tener el runtime .NET que necesitas.

**Solución:**
- Verifica qué versión de .NET usa tu aplicación (ej: .NET 6, .NET 7, .NET 8)
- Somee.com soporta versiones específicas de .NET
- **Opción A:** Cambiar tu aplicación a una versión soportada
- **Opción B:** Publicar como **self-contained** (incluye el runtime)

Para publicar self-contained:
```powershell
dotnet publish -c Release -r win-x64 --self-contained true -o bin/release/publish
```

### 2. Verificar web.config

Tu `web.config` debe verse así:
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" resourceType="Unspecified" />
    </handlers>
    <aspNetCore processPath="dotnet" 
                arguments=".\RubricasApp.Web.dll" 
                stdoutLogEnabled="true" 
                stdoutLogFile=".\logs\stdout" 
                hostingModel="inprocess">
      <environmentVariables>
        <environmentVariable name="ASPNETCORE_ENVIRONMENT" value="Production" />
      </environmentVariables>
    </aspNetCore>
  </system.webServer>
</configuration>
```

Si es self-contained, cambia:
```xml
<aspNetCore processPath=".\RubricasApp.Web.exe" 
            stdoutLogEnabled="true" 
            stdoutLogFile=".\logs\stdout" 
            hostingModel="inprocess">
```

### 3. Revisar Connection Strings

**Problema:** Si usas SQL Server LocalDB o conexiones locales, fallarán en Somee.

**Solución en `appsettings.json`:**
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "workstation id=tudb.mssql.somee.com;packet size=4096;user id=usuario;pwd=password;data source=tudb.mssql.somee.com;persist security info=False;initial catalog=tudb"
  }
}
```

### 4. Verificar permisos de archivos

Somee.com tiene restricciones de permisos. Asegúrate de:
- No escribir archivos fuera de tu directorio
- No intentar acceder a rutas absolutas como `C:\`
- Usar rutas relativas para logs y archivos temporales

### 5. Verificar dependencias

Asegúrate de que todos los archivos se subieron:
```powershell
# Ejecutar desde tu máquina local
powershell -ExecutionPolicy Bypass -File verify-publish.ps1 -publishDir "D:\Fuentes_gitHub\RubricasApp.Web\bin\release\publish"
```

### 6. Habilitar logs detallados

Ya está configurado en tu `web.config`, pero para verlos:

1. Accede a tu panel de Somee.com
2. Busca la carpeta `logs`
3. Descarga el archivo `stdout_YYYYMMDDHHMMSS.log`
4. Ahí verás el error específico

### 7. Errores comunes en Somee.com

**A. Base de datos no accesible**
```
Error: "A network-related or instance-specific error occurred"
```
- Verifica la connection string
- Usa el servidor SQL de Somee: `tudb.mssql.somee.com`

**B. Runtime no compatible**
```
Error: "The specified framework 'Microsoft.NETCore.App', version 'X.X.X' was not found"
```
- Publica como self-contained
- O usa una versión de .NET soportada por Somee

**C. Archivos faltantes**
```
Error: "Could not load file or assembly"
```
- Verifica que todos los archivos se subieron
- Re-ejecuta el deployment

## 📋 Checklist de verificación

- [ ] web.config tiene la sección `<aspNetCore>` correcta
- [ ] El DLL principal existe: `RubricasApp.Web.dll`
- [ ] Carpeta `logs` existe en el servidor
- [ ] Connection strings apuntan al servidor de Somee
- [ ] No hay rutas absolutas en el código
- [ ] .NET Runtime correcto o publicación self-contained
- [ ] Todos los archivos se subieron correctamente

## 🚀 Pasos siguientes

1. **Vuelve a desplegar** con el web.config corregido
2. **Espera 1-2 minutos** para que IIS reinicie
3. **Accede a tu sitio**: http://www.rubricasapp.somee.com
4. Si sigue fallando, **descarga los logs** de la carpeta `logs`
5. **Comparte el contenido del log** para diagnóstico específico

## 📞 Obtener ayuda

Si necesitas más ayuda, proporciona:
- Contenido del archivo `stdout_*.log`
- Versión de .NET que usas
- Connection string (sin contraseñas)
- Cualquier mensaje de error adicional
