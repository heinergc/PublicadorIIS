#!/usr/bin/env python3
"""
Interfaz gráfica para gestionar configuración de deployment
Usa CustomTkinter para una UI moderna y bonita
"""

import customtkinter as ctk
import json
import os
from pathlib import Path
from tkinter import messagebox, filedialog
import subprocess
import sys

# Configuración de tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DeployConfigUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.config_file = Path(__file__).parent / "deploy-settings.json"
        self.config_data = self.load_config()
        
        # Configuración de ventana
        self.title("🚀 Deploy Manager - IIS/Somee")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Main content
        self.create_main_content()
        
        # Footer con botones
        self.create_footer()
        
    def load_config(self):
        """Carga la configuración desde deploy-settings.json"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"environments": {}}
    
    def save_config(self):
        """Guarda la configuración en deploy-settings.json"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, indent=2, ensure_ascii=False)
    
    def create_header(self):
        """Crea el header de la aplicación"""
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#3b8ed0", "#1f6aa5"))
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🚀 Configurador de Deployment",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=20)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Gestiona tus entornos de publicación FTP",
            font=ctk.CTkFont(size=14),
            text_color=("#E0E0E0", "#E0E0E0")
        )
        subtitle_label.pack(pady=(0, 15))
    
    def create_main_content(self):
        """Crea el contenido principal"""
        # Frame principal con scroll
        main_frame = ctk.CTkFrame(self, corner_radius=10)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame, corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        
        # Selector de entorno
        env_selector_frame = ctk.CTkFrame(self.scroll_frame)
        env_selector_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 20))
        
        ctk.CTkLabel(
            env_selector_frame,
            text="Entorno:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        self.env_selector = ctk.CTkOptionMenu(
            env_selector_frame,
            values=list(self.config_data.get("environments", {}).keys()) or ["somee"],
            command=self.on_env_change,
            width=200
        )
        self.env_selector.pack(side="left", padx=10)
        
        add_env_btn = ctk.CTkButton(
            env_selector_frame,
            text="➕ Nuevo Entorno",
            command=self.add_new_environment,
            width=150,
            fg_color=("#2fa572", "#106A43")
        )
        add_env_btn.pack(side="left", padx=10)
        
        delete_env_btn = ctk.CTkButton(
            env_selector_frame,
            text="🗑️ Eliminar",
            command=self.delete_environment,
            width=120,
            fg_color=("#d32f2f", "#b71c1c")
        )
        delete_env_btn.pack(side="left", padx=10)
        
        # Separador
        separator = ctk.CTkFrame(self.scroll_frame, height=2, fg_color=("#cccccc", "#333333"))
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Campos de configuración
        self.create_config_fields()
        
    def create_config_fields(self):
        """Crea los campos de configuración"""
        current_env = self.env_selector.get()
        env_config = self.config_data.get("environments", {}).get(current_env, {})
        
        row = 2
        
        # Directorio de Publicación
        ctk.CTkLabel(
            self.scroll_frame,
            text="📁 Directorio de Publicación:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 5))
        
        publish_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        publish_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        publish_frame.grid_columnconfigure(0, weight=1)
        
        self.publish_dir_entry = ctk.CTkEntry(
            publish_frame,
            placeholder_text="D:\\MiProyecto\\bin\\Release\\net8.0\\publish",
            height=40
        )
        self.publish_dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.publish_dir_entry.insert(0, env_config.get("publishDir", ""))
        
        browse_btn = ctk.CTkButton(
            publish_frame,
            text="📂 Examinar",
            command=self.browse_publish_dir,
            width=120,
            height=40,
            fg_color=("#3b8ed0", "#1f6aa5")
        )
        browse_btn.grid(row=0, column=1)
        
        row += 2
        
        # FTP Host
        ctk.CTkLabel(
            self.scroll_frame,
            text="🌐 Host FTP:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.ftp_host_entry = ctk.CTkEntry(
            self.scroll_frame,
            placeholder_text="ftp.somee.com",
            height=40
        )
        self.ftp_host_entry.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        self.ftp_host_entry.insert(0, env_config.get("ftpHost", ""))
        
        row += 2
        
        # FTP User
        ctk.CTkLabel(
            self.scroll_frame,
            text="👤 Usuario FTP:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.ftp_user_entry = ctk.CTkEntry(
            self.scroll_frame,
            placeholder_text="mi_usuario_ftp",
            height=40
        )
        self.ftp_user_entry.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        self.ftp_user_entry.insert(0, env_config.get("ftpUser", ""))
        
        row += 2
        
        # Remote Root
        ctk.CTkLabel(
            self.scroll_frame,
            text="📂 Directorio Remoto:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.remote_root_entry = ctk.CTkEntry(
            self.scroll_frame,
            placeholder_text="/site/wwwroot",
            height=40
        )
        self.remote_root_entry.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        self.remote_root_entry.insert(0, env_config.get("remoteRoot", ""))
        
        row += 2
        
        # Info box
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("#E3F2FD", "#1E3A5F"))
        info_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        info_text = """
💡 Consejos:
• Especifica la ruta completa del directorio con los archivos compilados
• La contraseña NO se guarda aquí por seguridad
• Se pedirá al ejecutar el deployment desde VS Code
• Puedes agregar múltiples entornos (test, prod, etc.)
        """
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        ).pack(padx=15, pady=15, fill="both")
    
    def on_env_change(self, choice):
        """Actualiza los campos al cambiar de entorno"""
        # Limpiar campos actuales
        for widget in self.scroll_frame.winfo_children()[3:]:  # Mantener selector y separador
            widget.destroy()
        
        # Recrear campos con nueva configuración
        self.create_config_fields()
    
    def browse_publish_dir(self):
        """Abre el diálogo para seleccionar directorio de publicación"""
        initial_dir = self.publish_dir_entry.get() or str(Path.home())
        
        directory = filedialog.askdirectory(
            title="Seleccionar directorio de publicación",
            initialdir=initial_dir
        )
        
        if directory:
            self.publish_dir_entry.delete(0, "end")
            self.publish_dir_entry.insert(0, directory)
    
    def add_new_environment(self):
        """Agrega un nuevo entorno"""
        dialog = ctk.CTkInputDialog(
            text="Nombre del nuevo entorno:",
            title="Nuevo Entorno"
        )
        env_name = dialog.get_input()
        
        if env_name:
            if env_name in self.config_data.get("environments", {}):
                messagebox.showwarning("Advertencia", f"El entorno '{env_name}' ya existe")
                return
            
            # Crear nuevo entorno con valores por defecto
            if "environments" not in self.config_data:
                self.config_data["environments"] = {}
            
            self.config_data["environments"][env_name] = {
                "publishDir": "",
                "ftpHost": "ftp.example.com",
                "ftpUser": "usuario",
                "remoteRoot": "/site/wwwroot"
            }
            
            # Actualizar selector
            self.env_selector.configure(values=list(self.config_data["environments"].keys()))
            self.env_selector.set(env_name)
            self.on_env_change(env_name)
            
            messagebox.showinfo("Éxito", f"Entorno '{env_name}' creado")
    
    def delete_environment(self):
        """Elimina el entorno actual"""
        current_env = self.env_selector.get()
        
        if len(self.config_data.get("environments", {})) <= 1:
            messagebox.showwarning("Advertencia", "Debe existir al menos un entorno")
            return
        
        result = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar el entorno '{current_env}'?"
        )
        
        if result:
            del self.config_data["environments"][current_env]
            
            # Actualizar selector
            remaining_envs = list(self.config_data["environments"].keys())
            self.env_selector.configure(values=remaining_envs)
            self.env_selector.set(remaining_envs[0])
            self.on_env_change(remaining_envs[0])
            
            messagebox.showinfo("Éxito", f"Entorno '{current_env}' eliminado")
    
    def create_footer(self):
        """Crea el footer con botones de acción"""
        footer_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Botón Guardar
        save_btn = ctk.CTkButton(
            footer_frame,
            text="💾 Guardar Configuración",
            command=self.save_changes,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#2fa572", "#106A43"),
            hover_color=("#25824e", "#0d5435")
        )
        save_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botón Deploy
        deploy_btn = ctk.CTkButton(
            footer_frame,
            text="🚀 Ejecutar Deployment",
            command=self.run_deployment,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#d32f2f", "#b71c1c"),
            hover_color=("#b71c1c", "#8b0000")
        )
        deploy_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botón Cancelar
        cancel_btn = ctk.CTkButton(
            footer_frame,
            text="❌ Cerrar",
            command=self.quit,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray20")
        )
        cancel_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    def save_changes(self):
        """Guarda los cambios en la configuración"""
        current_env = self.env_selector.get()
        
        # Actualizar datos
        self.config_data["environments"][current_env] = {
            "publishDir": self.publish_dir_entry.get().strip(),
            "ftpHost": self.ftp_host_entry.get().strip(),
            "ftpUser": self.ftp_user_entry.get().strip(),
            "remoteRoot": self.remote_root_entry.get().strip()
        }
        
        # Validar campos
        if not all([
            self.config_data["environments"][current_env]["publishDir"],
            self.config_data["environments"][current_env]["ftpHost"],
            self.config_data["environments"][current_env]["ftpUser"],
            self.config_data["environments"][current_env]["remoteRoot"]
        ]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        # Validar que el directorio existe
        publish_dir = self.config_data["environments"][current_env]["publishDir"]
        if not os.path.exists(publish_dir):
            result = messagebox.askyesno(
                "Advertencia",
                f"El directorio no existe:\n{publish_dir}\n\n¿Guardar de todas formas?"
            )
            if not result:
                return
        
        try:
            self.save_config()
            messagebox.showinfo("Éxito", "✅ Configuración guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def run_deployment(self):
        """Ejecuta el proceso de deployment"""
        current_env = self.env_selector.get()
        
        # Primero guardar cambios
        self.save_changes()
        
        # Pedir contraseña
        password_dialog = ctk.CTkInputDialog(
            text=f"Contraseña FTP para '{current_env}':",
            title="Autenticación FTP"
        )
        password = password_dialog.get_input()
        
        if not password:
            messagebox.showwarning("Cancelado", "Deployment cancelado")
            return
        
        # Confirmar
        result = messagebox.askyesno(
            "Confirmar Deployment",
            f"¿Ejecutar deployment en '{current_env}'?\n\n"
            f"Esto publicará tu proyecto .NET y lo subirá vía FTP."
        )
        
        if result:
            messagebox.showinfo(
                "Deployment Iniciado",
                "El deployment se ejecutará en VS Code.\n"
                "Revisa la terminal para ver el progreso."
            )
            
            # Aquí podrías ejecutar el script PowerShell directamente
            # Por ahora solo mostramos el mensaje
            self.withdraw()
            
            try:
                script_path = Path(__file__).parent / "deploy-somee.ps1"
                publish_dir = self.config_data["environments"][current_env]["publishDir"]
                
                subprocess.Popen([
                    "powershell",
                    "-ExecutionPolicy", "Bypass",
                    "-File", str(script_path),
                    "-publishDir", publish_dir,
                    "-Env", current_env,
                    "-Password", password
                ], shell=True)
            except Exception as e:
                messagebox.showerror("Error", f"Error al ejecutar deployment: {str(e)}")
                self.deiconify()

def main():
    """Función principal"""
    app = DeployConfigUI()
    app.mainloop()

if __name__ == "__main__":
    main()
