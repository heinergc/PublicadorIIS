"""
Interfaz Web para gestionar configuración de deployment
Usa Streamlit para una UI moderna accesible desde el navegador
"""

import streamlit as st
import json
from pathlib import Path
import subprocess

# Configuración de la página
st.set_page_config(
    page_title="Deploy Manager",
    page_icon="🚀",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f6aa5 0%, #3b8ed0 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3b8ed0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 Configurador de Deployment</h1>
    <p>Gestiona tus entornos de publicación FTP para IIS/Somee</p>
</div>
""", unsafe_allow_html=True)

# Funciones auxiliares
@st.cache_data
def load_config():
    """Carga la configuración desde deploy-settings.json"""
    config_file = Path(__file__).parent / "deploy-settings.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"environments": {}}

def save_config(config_data):
    """Guarda la configuración en deploy-settings.json"""
    config_file = Path(__file__).parent / "deploy-settings.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    st.cache_data.clear()

# Cargar configuración
config_data = load_config()

# Sidebar - Gestión de entornos
with st.sidebar:
    st.header("📋 Entornos")
    
    # Lista de entornos
    environments = list(config_data.get("environments", {}).keys())
    if not environments:
        environments = ["somee"]
        if "environments" not in config_data:
            config_data["environments"] = {}
        config_data["environments"]["somee"] = {
            "ftpHost": "ftp.somee.com",
            "ftpUser": "MI_USUARIO_FTP",
            "remoteRoot": "/site/wwwroot"
        }
        save_config(config_data)
    
    selected_env = st.selectbox(
        "Selecciona entorno:",
        environments,
        key="env_selector"
    )
    
    st.divider()
    
    # Agregar nuevo entorno
    with st.expander("➕ Nuevo Entorno"):
        new_env_name = st.text_input("Nombre del entorno:", key="new_env_name")
        if st.button("Crear", key="create_env"):
            if new_env_name:
                if new_env_name in config_data["environments"]:
                    st.error(f"El entorno '{new_env_name}' ya existe")
                else:
                    config_data["environments"][new_env_name] = {
                        "ftpHost": "ftp.example.com",
                        "ftpUser": "usuario",
                        "remoteRoot": "/site/wwwroot"
                    }
                    save_config(config_data)
                    st.success(f"✅ Entorno '{new_env_name}' creado")
                    st.rerun()
            else:
                st.warning("Ingresa un nombre")
    
    # Eliminar entorno
    if len(environments) > 1:
        st.divider()
        if st.button("🗑️ Eliminar Entorno Actual", type="secondary"):
            del config_data["environments"][selected_env]
            save_config(config_data)
            st.success(f"✅ Entorno '{selected_env}' eliminado")
            st.rerun()
    
    st.divider()
    
    # Info
    st.markdown("""
    ### 💡 Consejos
    - La contraseña **NO** se guarda aquí
    - Se solicitará al ejecutar deployment
    - Agrega múltiples entornos según necesites
    """)

# Main content - Configuración del entorno seleccionado
if selected_env in config_data.get("environments", {}):
    env_config = config_data["environments"][selected_env]
    
    st.header(f"⚙️ Configuración de '{selected_env}'")
    
    # Formulario de configuración
    with st.form("config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌐 Host FTP")
            ftp_host = st.text_input(
                "Host FTP",
                value=env_config.get("ftpHost", ""),
                placeholder="ftp.somee.com",
                help="Dirección del servidor FTP",
                label_visibility="collapsed"
            )
            
            st.subheader("👤 Usuario FTP")
            ftp_user = st.text_input(
                "Usuario FTP",
                value=env_config.get("ftpUser", ""),
                placeholder="mi_usuario_ftp",
                help="Tu nombre de usuario FTP",
                label_visibility="collapsed"
            )
        
        with col2:
            st.subheader("📂 Directorio Remoto")
            remote_root = st.text_input(
                "Directorio Remoto",
                value=env_config.get("remoteRoot", ""),
                placeholder="/site/wwwroot",
                help="Ruta remota donde se publicarán los archivos",
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="info-box">
                <strong>🔒 Seguridad:</strong><br>
                La contraseña FTP se solicitará al momento de ejecutar el deployment y nunca se almacena en archivos.
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Botón de guardar
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submit_button = st.form_submit_button("💾 Guardar Configuración", type="primary")
        
        if submit_button:
            if not all([ftp_host, ftp_user, remote_root]):
                st.error("❌ Todos los campos son obligatorios")
            else:
                config_data["environments"][selected_env] = {
                    "ftpHost": ftp_host.strip(),
                    "ftpUser": ftp_user.strip(),
                    "remoteRoot": remote_root.strip()
                }
                save_config(config_data)
                st.success("✅ Configuración guardada correctamente")
                st.balloons()
    
    st.divider()
    
    # Sección de deployment
    st.header("🚀 Ejecutar Deployment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Entorno:** `{selected_env}`  
        **Host:** `{env_config.get('ftpHost', 'N/A')}`  
        **Usuario:** `{env_config.get('ftpUser', 'N/A')}`  
        **Destino:** `{env_config.get('remoteRoot', 'N/A')}`
        """)
    
    with col2:
        password = st.text_input(
            "Contraseña FTP:",
            type="password",
            help="Ingresa tu contraseña FTP para ejecutar el deployment"
        )
        
        if st.button("🚀 Ejecutar Deployment Ahora", type="primary"):
            if not password:
                st.error("❌ Debes ingresar la contraseña FTP")
            else:
                with st.spinner("Ejecutando deployment..."):
                    try:
                        script_path = Path(__file__).parent / "deploy-somee.ps1"
                        result = subprocess.run(
                            [
                                "powershell",
                                "-ExecutionPolicy", "Bypass",
                                "-File", str(script_path),
                                "-publishDir", "publish",
                                "-Env", selected_env,
                                "-Password", password
                            ],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0:
                            st.success("✅ Deployment completado exitosamente!")
                            with st.expander("Ver salida del comando"):
                                st.code(result.stdout)
                        else:
                            st.error("❌ Error durante el deployment")
                            with st.expander("Ver detalles del error"):
                                st.code(result.stderr)
                    except Exception as e:
                        st.error(f"❌ Error al ejecutar: {str(e)}")
    
    st.divider()
    
    # Comandos alternativos
    with st.expander("📋 Comandos manuales (VS Code)"):
        st.markdown("""
        ### Ejecutar desde VS Code Terminal:
        ```powershell
        # Publicar proyecto
        dotnet publish --configuration Release --output publish
        
        # Ejecutar deployment
        powershell -ExecutionPolicy Bypass -File deploy-somee.ps1 -publishDir publish -Env """ + selected_env + """ -Password TU_PASSWORD
        ```
        
        ### O usar Tasks de VS Code:
        1. `Ctrl+Shift+P`
        2. `Tasks: Run Task`
        3. `Deploy dinámico (FTP)`
        """)
    
    # Vista previa JSON
    with st.expander("🔍 Ver JSON completo"):
        st.json(config_data)

else:
    st.error("❌ Entorno no encontrado")
