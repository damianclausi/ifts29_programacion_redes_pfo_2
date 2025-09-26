#!/usr/bin/env python3
"""
Cliente de Consola para el Sistema de Gestión de Tareas - PFO 2

Este cliente permite:
- Registrar nuevos usuarios
- Iniciar sesión y abrir automáticamente la página web protegida
- Cerrar la sesión activa
- Salir limpiamente del sistema

Autor: Sistema de Gestión de Tareas
Versión: 1.1
"""

import sys
import os
import tempfile
import subprocess
import shutil
import requests
from requests.auth import HTTPBasicAuth
import getpass
from urllib.parse import urljoin

try:
    import termios
    import tty
except ImportError:  # pragma: no cover - Windows fallback
    termios = None
    tty = None


class ClienteConsola:
    """Cliente de consola para el API REST de tareas"""
    
    def __init__(self, base_url="http://localhost:5555"):
        """Inicializa el cliente con la URL base del servidor"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.logged_in = False
        self.username = None
        self._temp_files = []
        self.auth = None

    def _tag(self, etiqueta, color):
        """Genera un tag coloreado"""
        return f"{color}{etiqueta}{Colores.RESET}"

    def _info(self, mensaje):
        print(f"{self._tag('[INFO]', Colores.INFO)} {mensaje}")

    def _ok(self, mensaje):
        print(f"{self._tag('[OK]', Colores.OK)} {mensaje}")

    def _warn(self, mensaje):
        print(f"{self._tag('[WARN]', Colores.WARN)} {mensaje}")

    def _error(self, mensaje):
        print(f"{self._tag('[ERROR]', Colores.ERROR)} {mensaje}")

    def _tip(self, mensaje):
        print(f"{self._tag('[TIP]', Colores.TIP)} {mensaje}")

    def _divider(self, ancho=50, caracter='='):
        print(f"{Colores.HIGHLIGHT}{caracter * ancho}{Colores.RESET}")

    def _section(self, titulo):
        self._divider(len(titulo) + 8, caracter='=')
        print(f"{Colores.BOLD}{Colores.TITLE}  {titulo}{Colores.RESET}")
        self._divider(len(titulo) + 8, caracter='=')

    def _subsection(self, titulo):
        print(f"\n{Colores.BOLD}{Colores.HIGHLIGHT}{titulo}{Colores.RESET}")
        print(f"{Colores.HIGHLIGHT}{'-' * len(titulo)}{Colores.RESET}")

    def _prompt(self, mensaje):
        return input(f"{Colores.PROMPT}{mensaje}{Colores.RESET}").strip()

    def _prompt_password(self, mensaje):
        prompt = f"{Colores.PROMPT}{mensaje}{Colores.RESET}"

        # Fallback cuando no hay soporte para termios/tty o no es un TTY interactivo
        if termios is None or tty is None or not sys.stdin.isatty() or not sys.stdout.isatty():
            try:
                return getpass.getpass(prompt)
            except Exception:
                return self._prompt(mensaje)

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        password_chars = []

        sys.stdout.write(prompt)
        sys.stdout.flush()

        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)

                if ch in ('\n', '\r'):
                    sys.stdout.write('\n')
                    break

                if ch == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt

                if ch == '\x04':  # Ctrl+D
                    raise EOFError

                if ch in ('\x7f', '\b'):  # Retroceso
                    if password_chars:
                        password_chars.pop()
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                    continue

                if ch.isprintable():
                    password_chars.append(ch)
                    sys.stdout.write('*')
                    sys.stdout.flush()

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ''.join(password_chars)



    def mostrar_banner(self):
        """Muestra el banner del cliente"""
        self._divider()
        print(f"{Colores.BOLD}{Colores.TITLE}CLIENTE DE CONSOLA - SISTEMA DE TAREAS{Colores.RESET}")
        self._divider()
        print(f"{Colores.BOLD}{Colores.INFO}Servidor:{Colores.RESET} {self.base_url}")
        print(f"{Colores.BOLD}PFO 2 - IFTS 29 - Programación de Redes{Colores.RESET}")
        self._divider()
    
    def verificar_servidor(self):
        """Verifica si el servidor está disponible"""
        try:
            url = urljoin(self.base_url, "status")
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self._ok(f"Servidor conectado: {data.get('message', 'OK')}")
                return True
            else:
                self._error(f"Conexión fallida (código {response.status_code})")
                return False
        except Exception as e:
            self._error(f"No se puede conectar al servidor: {e}")
            self._tip(f"Verifica que el servidor esté ejecutándose en {self.base_url}")
            return False
    
    def registrar_usuario(self):
        """Registra un nuevo usuario"""
        self._subsection("REGISTRO DE NUEVO USUARIO")
        
        try:
            username = self._prompt("Nombre de usuario: ")
            if not username:
                self._error("El nombre de usuario no puede estar vacío")
                return
            
            password = self._prompt_password("Contraseña: ")
            if not password:
                self._error("La contraseña no puede estar vacía")
                return
            
            url = urljoin(self.base_url, "registro")
            data = {"usuario": username, "contraseña": password}
            
            response = self.session.post(url, json=data, timeout=10)
            
            if response.status_code == 201:
                self._ok("Usuario registrado exitosamente")
                self._tip("Ya puedes iniciar sesión")
            elif response.status_code == 400:
                data = response.json()
                self._error(data.get('error', 'Usuario ya existe'))
            else:
                self._error(f"Error del servidor (código {response.status_code})")
                
        except Exception as e:
            self._warn(f"Error de conexión: {e}")
    
    def iniciar_sesion(self):
        """Inicia sesión con un usuario existente"""
        self._subsection("INICIAR SESIÓN")
        
        try:
            username = self._prompt("Nombre de usuario: ")
            if not username:
                self._error("El nombre de usuario no puede estar vacío")
                return
            
            password = self._prompt_password("Contraseña: ")
            if not password:
                self._error("La contraseña no puede estar vacía")
                return
            
            url = urljoin(self.base_url, "login")
            data = {"usuario": username, "contraseña": password}
            
            response = self.session.post(url, json=data, timeout=10)
            payload = {}
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            
            if response.status_code == 200:
                self.logged_in = True
                self.username = payload.get('usuario', username)
                self.auth = (self.username, password)
                self._ok(f"Sesión iniciada como: {self.username}")
                self.abrir_pagina_web()
            elif response.status_code == 401:
                self.auth = None
                self._error(payload.get('error', 'Credenciales inválidas'))
            else:
                self.auth = None
                self._error(f"Error del servidor (código {response.status_code})")
                
        except Exception as e:
            self._warn(f"Error de conexión: {e}")
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        if not self.logged_in:
            self._error("No hay sesión activa")
            return
        
        try:
            url = urljoin(self.base_url, "logout")
            response = self.session.post(url, timeout=10)
            
            if response.status_code == 200:
                self._info(f"Sesión cerrada para: {self.username}")
                self.logged_in = False
                self.username = None
                self.auth = None
                # Limpiar archivos temporales al cerrar sesión
                self._limpiar_archivos_temporales()
            else:
                self._warn("Error al cerrar sesión")
                
        except Exception as e:
            self._warn(f"Error de conexión: {e}")
    
    def _abrir_navegador(self, destino, es_url=False):
        """Abre un recurso en el navegador usando WSL"""
        try:
            if not es_url:
                try:
                    # Convertir ruta de WSL a Windows
                    destino_windows = subprocess.check_output(["wslpath", "-w", destino], text=True).strip()
                    # Escapar espacios y caracteres especiales para cmd
                    destino_windows = destino_windows.replace('"', '\\"')
                    comando = f'cmd.exe /c start "" "{destino_windows}"'
                    subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                except Exception as e:
                    self._warn(f"Error convirtiendo ruta WSL: {e}")
                    # Fallback: copiar archivo a directorio accesible desde Windows
                    try:
                        # Usar directorio home que es accesible desde Windows
                        home_dir = os.path.expanduser("~")
                        new_path = os.path.join(home_dir, "pagina_tareas.html")
                        shutil.copy2(destino, new_path)
                        destino_windows = subprocess.check_output(["wslpath", "-w", new_path], text=True).strip()
                        comando = f'cmd.exe /c start "" "{destino_windows}"'
                        subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        self._temp_files.append(new_path)  # Para limpieza posterior
                        return True
                    except Exception:
                        pass
            else:
                # Para URLs, usar directamente
                comando = f'cmd.exe /c start "" "{destino}"'
                subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True

        except Exception as e:
            self._warn(f"No se pudo abrir el navegador automáticamente: {e}")
            self._info(f"Destino disponible en: {destino}")
            self._tip("Puedes abrirlo manualmente")
            return False

        self._warn("No se encontró un método compatible para abrir el navegador automáticamente")
        self._info(f"Destino disponible en: {destino}")
        self._tip("Copia y pega el enlace en tu navegador")
        return False
    
    def abrir_pagina_web(self):
        """Abre la página web de tareas en el navegador"""
        if not self.logged_in or not self.auth:
            self._error("Debes iniciar sesión primero")
            return
        
        url_tareas = f"{self.base_url}/tareas"
        self._subsection("ABRIENDO PÁGINA DE TAREAS")
        
        try:
            usuario, contraseña = self.auth
            headers = {'Accept': 'text/html'}
            response = self.session.get(
                url_tareas,
                headers=headers,
                timeout=10,
                auth=HTTPBasicAuth(usuario, contraseña)
            )
            
            if response.status_code == 200:
                # Intentar abrir directamente la URL con autenticación embebida
                self._info("Abriendo página web con autenticación")
                try:
                    # Intentar abrir la URL directamente con autenticación embebida
                    url_con_auth = f"http://{usuario}:{contraseña}@localhost:5555/tareas"
                    comando = f'cmd.exe /c start "" "{url_con_auth}"'
                    subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self._ok("Página abierta en el navegador")
                    self._info("Si el navegador solicita credenciales:")
                    self._info(f"  Usuario: {usuario}")
                    self._info("  Contraseña: (la que usaste para iniciar sesión)")
                    return
                except Exception:
                    self._warn("Error abriendo URL directa, usando archivo temporal")
                
                # Crear archivo temporal (fallback)
                temp_dir = os.path.expanduser("~")
                temp_filename = "tareas_sistema.html"
                temp_path = os.path.join(temp_dir, temp_filename)
                
                with open(temp_path, 'w', encoding='utf-8') as temp_file:
                    # Agregar información de autenticación al HTML
                    html_content = response.text
                    # Insertar información útil al inicio del body
                    auth_info = f"""
                    <div style="background: #e7f3ff; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2196F3;">
                        <strong>Sesión activa:</strong> {usuario}<br>
                        <small>Archivo generado por el cliente de consola en WSL</small>
                    </div>
                    """
                    html_content = html_content.replace('<body>', f'<body>{auth_info}')
                    temp_file.write(html_content)
                
                self._ok("Página obtenida correctamente")
                
                # Intentar abrir en el navegador de forma no-bloqueante
                if self._abrir_navegador(temp_path):
                    self._info("Página abierta en el navegador")
                    self._tip(f"Archivo guardado en: {temp_path}")
                else:
                    self._warn("No se pudo abrir automáticamente")
                    self._tip(f"Abre manualmente: {temp_path}")
                
                # Guardar la ruta para limpieza posterior
                self._temp_files.append(temp_path)
                
            elif response.status_code == 401:
                self._error("Credenciales inválidas o acceso no autorizado")
                self._tip("Intenta iniciar sesión nuevamente")
                self.logged_in = False
                self.username = None
                self.auth = None
            else:
                self._error(f"Error del servidor (código {response.status_code})")
                try:
                    data = response.json()
                    self._info(f"Mensaje: {data.get('error', 'Error desconocido')}")
                except:
                    pass
                    
        except Exception as e:
            self._warn(f"Error al generar la página: {e}")
            self._tip("Como alternativa, puedes acceder manualmente a:")
            self._info(f"   {url_tareas}")
            self._info("   (pero necesitarás iniciar sesión desde el navegador)")
            if self.auth:
                usuario, _ = self.auth
                self._info(f"   Usuario: {usuario}")
                self._info("   Contraseña: (la que usaste en el cliente)")

    def _limpiar_archivos_temporales(self):
        """Limpia archivos temporales creados"""
        if hasattr(self, '_temp_files') and self._temp_files:
            for temp_path in self._temp_files:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass
            self._temp_files = []

    def mostrar_menu(self):
        """Muestra el menú principal"""
        estado = f"[{self.username}]" if self.logged_in else "[No autenticado]"
        color_estado = Colores.OK if self.logged_in else Colores.WARN
        print(f"\n{Colores.BOLD}{color_estado}{estado}{Colores.RESET} {Colores.BOLD}MENÚ PRINCIPAL{Colores.RESET}")
        print(f"{Colores.HIGHLIGHT}{'-' * 40}{Colores.RESET}")
        print(f"{Colores.BOLD}1.{Colores.RESET} Registrar nuevo usuario")
        print(f"{Colores.BOLD}2.{Colores.RESET} Iniciar sesión")
        if self.logged_in:
            print(f"{Colores.BOLD}3.{Colores.RESET} Cerrar sesión")
        print(f"{Colores.BOLD}0.{Colores.RESET} Salir")
        print(f"{Colores.HIGHLIGHT}{'-' * 40}{Colores.RESET}")
    
    def ejecutar(self):
        """Ejecuta el cliente de consola"""
        self.mostrar_banner()
        
        # Verificar conexión con el servidor
        if not self.verificar_servidor():
            print()
            self._warn("No se puede continuar sin conexión al servidor")
            sys.exit(1)
        
        print()
        self._ok("Cliente iniciado correctamente")
        
        while True:
            self.mostrar_menu()
            
            try:
                opcion = self._prompt("\nSelecciona una opción: ")
                
                if opcion == "0":
                    if self.logged_in:
                        self.cerrar_sesion()
                    self._limpiar_archivos_temporales()
                    print()
                    self._info("Hasta luego")
                    break
                elif opcion == "1":
                    self.registrar_usuario()
                elif opcion == "2":
                    if not self.logged_in:
                        self.iniciar_sesion()
                    else:
                        self._info("Ya tienes una sesión activa")
                elif opcion == "3":
                    if self.logged_in:
                        self.cerrar_sesion()
                    else:
                        self._error("No hay sesión activa para cerrar")
                else:
                    self._error("Opción inválida")
                    
            except KeyboardInterrupt:
                print("\n")
                self._warn("Interrupción del usuario")
                if self.logged_in:
                    self.cerrar_sesion()
                self._limpiar_archivos_temporales()
                self._info("Hasta luego")
                break
            except EOFError:
                print("\n")
                self._warn("Fin de entrada")
                self._limpiar_archivos_temporales()
                break


# =============================================================================
# UTILIDADES DE COLORES PARA CONSOLA
# =============================================================================

class Colores:
    """Códigos ANSI para colorear la salida en consola"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    INFO = "\033[36m"
    OK = "\033[32m"
    WARN = "\033[33m"
    ERROR = "\033[31m"
    TITLE = "\033[95m"
    HIGHLIGHT = "\033[94m"
    PROMPT = "\033[96m"
    TIP = "\033[35m"


# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================

def main():
    """Función principal"""
    # Permitir URL personalizada como parámetro
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "http://localhost:5555"
    
    cliente = ClienteConsola(url)
    cliente.ejecutar()

if __name__ == "__main__":
    main()