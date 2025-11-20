# PublicadorIIS

Sistema para publicar aplicaciones en servidores FTP/IIS de forma sencilla con interfaz gráfica.

## 🚀 Características

- ✅ Interfaz gráfica moderna (CustomTkinter)
- ✅ Gestión de múltiples entornos (dev, test, prod, etc.)
- ✅ Selector de directorios mediante explorador de archivos
- ✅ Validación de conexión FTP antes de subir archivos
- ✅ Subida recursiva de archivos y carpetas
- ✅ Reporte detallado del proceso de deployment
- ✅ Configuración guardada en JSON

## 📋 Requisitos

- Python 3.8 o superior
- PowerShell (incluido en Windows)
- Acceso a servidor FTP

## 🔧 Instalación

1. Instalar dependencias:
```powershell
pip install customtkinter darkdetect
```

## 💻 Uso

### Opción 1: Interfaz Gráfica (Recomendado)

Ejecuta la aplicación:
```powershell
python deploy-config-ui.py
```

La interfaz te permite:
1. **Seleccionar el directorio** con los archivos compilados
2. **Configurar el servidor FTP** (host, usuario, directorio remoto)
3. **Crear múltiples entornos** (somee, azure, etc.)
4. **Guardar la configuración** para futuros deployments
5. **Ejecutar el deployment** directamente desde la interfaz

### Opción 2: Línea de Comandos

```powershell
powershell -ExecutionPolicy Bypass -File deploy-somee.ps1 -publishDir "C:\MiProyecto\bin\Release\publish" -Env somee -Password "tu_password"
```

## ⚙️ Configuración

El archivo `deploy-settings.json` almacena tus configuraciones:

```json
{
  "environments": {
    "somee": {
      "publishDir": "D:\\MiProyecto\\bin\\release\\publish",
      "ftpHost": "155.254.246.25/www.miapp.somee.com",
      "ftpUser": "tu_usuario",
      "remoteRoot": "/"
    },
    "produccion": {
      "publishDir": "D:\\MiProyecto\\bin\\release\\publish",
      "ftpHost": "ftp.miservidor.com",
      "ftpUser": "usuario_prod",
      "remoteRoot": "/wwwroot"
    }
  }
}
```

**Nota:** Para servidores Somee.com, el host suele ser una IP con subdirectorio:
- Host: `155.254.246.25/www.tuapp.somee.com` (sin `ftp://`)
- Remote Root: `/` (el subdirectorio ya está en el host)

## 🔒 Seguridad

- ✅ La contraseña FTP **NO se almacena** en archivos
- ✅ Se solicita cada vez que ejecutas el deployment
- ✅ Conexiones mediante protocolo FTP seguro

## ❌ Solución de Problemas

### Error 530: "No ha iniciado sesión"

**Causas comunes:**
1. Usuario o contraseña incorrectos
2. El host FTP es incorrecto
3. El servidor requiere conexión FTPS (no soportado actualmente)
4. Firewall bloqueando la conexión

**Solución:**
- Verifica las credenciales en la interfaz
- Prueba conectarte con un cliente FTP (FileZilla) usando las mismas credenciales
- Asegúrate de que el host sea correcto (sin `ftp://` al inicio)

### El directorio no existe

- Usa el botón **"📂 Examinar"** para seleccionar la carpeta correcta
- Asegúrate de que la carpeta contenga los archivos compilados de tu aplicación

### Timeout al subir archivos

- Archivos muy grandes pueden tardar más
- El script tiene timeout de 60 segundos por archivo
- Verifica tu conexión a internet

## 📝 Ejemplo de Uso Completo

1. **Compila tu proyecto .NET:**
   ```powershell
   dotnet publish -c Release -o D:\MiProyecto\bin\release\publish
   ```

2. **Ejecuta la interfaz:**
   ```powershell
   python deploy-config-ui.py
   ```

3. **Configura tu entorno:**
   - Haz clic en "📂 Examinar" y selecciona `D:\MiProyecto\bin\release\publish`
   - Ingresa tu host FTP: `155.254.246.25/www.tuapp.somee.com` (sin ftp://)
   - Usuario: `tu_usuario`
   - Directorio remoto: `/`

4. **Guarda y despliega:**
   - Clic en "💾 Guardar Configuración"
   - Clic en "🚀 Ejecutar Deployment"
   - Ingresa tu contraseña FTP
   - ¡Listo!

## 🤝 Contribuir

¿Encontraste un bug o tienes una sugerencia? Abre un issue en GitHub.

## 📄 Licencia

MIT License
