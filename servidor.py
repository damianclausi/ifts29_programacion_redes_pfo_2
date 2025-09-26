from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import bcrypt


app = Flask(__name__)
DATABASE = 'tareas.db'


def init_db() -> None:
    """Inicializa la base de datos con la tabla de usuarios"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    conn.commit()
    conn.close()


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    except Exception as exc:  # pragma: no cover - logging only
        log_error(f"Error verificando contraseña: {exc}")
        return False


def fetch_user(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, usuario, password_hash FROM usuarios WHERE usuario = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    return row


def require_basic_auth():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return None
    user_row = fetch_user(auth.username)
    if not user_row:
        return None
    if not verify_password(auth.password, user_row['password_hash']):
        return None
    return user_row


def unauthorized_response():
    return (
        jsonify({'error': 'Credenciales inválidas o ausentes'}),
        401,
        {'WWW-Authenticate': 'Basic realm="Sistema de Tareas"'}
    )


@app.route('/registro', methods=['POST'])
def registro():
    try:
        data = request.get_json() or {}
        usuario = (data.get('usuario') or '').strip()
        contraseña = data.get('contraseña') or ''

        if len(usuario) < 3:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 3 caracteres'}), 400
        if len(contraseña) < 4:
            return jsonify({'error': 'La contraseña debe tener al menos 4 caracteres'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE usuario = ?', (usuario,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'El usuario ya existe'}), 400

        password_hash = hash_password(contraseña)
        cursor.execute('INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)', (usuario, password_hash))
        conn.commit()
        conn.close()

        return jsonify({'mensaje': 'Usuario registrado exitosamente', 'usuario': usuario}), 201
    except Exception as exc:
        log_error(f"Error en /registro: {exc}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        usuario = (data.get('usuario') or '').strip()
        contraseña = data.get('contraseña') or ''

        user_row = fetch_user(usuario)
        if not user_row or not verify_password(contraseña, user_row['password_hash']):
            return jsonify({'error': 'Credenciales inválidas'}), 401

        return jsonify({
            'mensaje': 'Credenciales válidas',
            'usuario': user_row['usuario'],
            'autenticacion': 'basic'
        }), 200
    except Exception as exc:
        log_error(f"Error en /login: {exc}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/tareas', methods=['GET'])
def tareas():
    user_row = require_basic_auth()
    if not user_row:
        return unauthorized_response()

    username = user_row['usuario']
    
    try:
        with open('tareas_bienvenida.html', 'r', encoding='utf-8') as html_file:
            html_content = html_file.read().replace('{{ usuario }}', username)
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return jsonify({'error': 'Archivo HTML no encontrado'}), 500


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    return jsonify({
        'mensaje': 'Autenticación básica: no hay sesión que cerrar. Cierra el cliente o limpia las credenciales.'
    }), 200


@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'ok',
        'message': 'Servidor funcionando correctamente',
        'version': '1.1',
        'autenticacion': 'basic',
        'endpoints': {
            'POST /registro': 'Registrar nuevo usuario',
            'POST /login': 'Validar credenciales',
            'GET /tareas': 'Página de tareas (basic auth)',
            'POST /logout': 'Mensaje informativo',
            'GET /status': 'Estado del servidor'
        }
    })


@app.errorhandler(404)
def not_found(error):  # pragma: no cover - rutas inválidas
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(405)
def method_not_allowed(error):  # pragma: no cover - métodos inválidos
    return jsonify({'error': 'Método no permitido para este endpoint'}), 405


@app.errorhandler(500)
def internal_error(error):  # pragma: no cover - errores generales
    return jsonify({'error': 'Error interno del servidor'}), 500


# =============================================================================
# UTILIDADES DE COLORES Y LOGGING
# =============================================================================

class ConsoleColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    INFO = "\033[36m"
    OK = "\033[32m"
    WARN = "\033[33m"
    ERROR = "\033[31m"
    TITLE = "\033[95m"


def log_info(message: str) -> None:
    print(f"{ConsoleColors.INFO}[INFO]{ConsoleColors.RESET} {message}")


def log_ok(message: str) -> None:
    print(f"{ConsoleColors.OK}[OK]{ConsoleColors.RESET} {message}")


def log_warn(message: str) -> None:
    print(f"{ConsoleColors.WARN}[WARN]{ConsoleColors.RESET} {message}")


def log_error(message: str) -> None:
    print(f"{ConsoleColors.ERROR}[ERROR]{ConsoleColors.RESET} {message}")


def log_title(message: str) -> None:
    print(f"\n{ConsoleColors.BOLD}{ConsoleColors.TITLE}{message}{ConsoleColors.RESET}")


def log_bullet(message: str) -> None:
    print(f"   {ConsoleColors.INFO}{message}{ConsoleColors.RESET}")


# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================

if __name__ == '__main__':
    init_db()
    log_title("Iniciando servidor Flask...")
    log_info("Endpoints disponibles:")
    log_bullet("GET /status - Estado del servidor")
    log_bullet("POST /registro - Registrar usuario")
    log_bullet("POST /login - Validar credenciales")
    log_bullet("GET /tareas - Información de tareas (requiere Basic Auth)")
    log_bullet("POST /logout - Mensaje informativo")
    log_ok("Base de datos SQLite inicializada")
    app.run(debug=True, host='0.0.0.0', port=5555)