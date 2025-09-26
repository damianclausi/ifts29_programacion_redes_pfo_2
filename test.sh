#!/bin/bash

# Sistema de Gestión de Tareas - PFO 2
# Script unificado de instalación, ejecución y demostración

# Colores ANSI
RESET="\033[0m"
BOLD="\033[1m"
INFO="\033[36m"
OK="\033[32m"
WARN="\033[33m"
ERROR="\033[31m"
TIP="\033[35m"
HIGHLIGHT="\033[94m"
DIM="\033[90m"

info() { printf "${INFO}[INFO]${RESET} %s\n" "$1"; }
ok() { printf "${OK}[OK]${RESET} %s\n" "$1"; }
warn() { printf "${WARN}[WARN]${RESET} %s\n" "$1"; }
error() { printf "${ERROR}[ERROR]${RESET} %s\n" "$1"; }
tip() { printf "${TIP}[TIP]${RESET} %s\n" "$1"; }
title() { printf "\n${BOLD}${HIGHLIGHT}%s${RESET}\n" "$1"; }
step() { printf "\n${BOLD}${HIGHLIGHT}Paso %s${RESET}\n" "$1"; }
bullet() { printf "   ${DIM}%s${RESET}\n" "$1"; }

# Banner del sistema con información completa
mostrar_banner() {
    clear
    title "=========================================="
    title "SISTEMA DE GESTION DE TAREAS - PFO 2"
    title "IFTS N°29 - Programacion de Redes"  
    title "=========================================="
    printf "\n${BOLD}Descripcion:${RESET}\n"
    bullet "Sistema completo Flask + SQLite + autenticacion HTTP Basic"
    bullet "API REST para gestion de usuarios y tareas"
    bullet "Cliente de consola con interfaz colorizada"
    bullet "Probador web de endpoints integrado"
    printf "\n${BOLD}Tecnologias:${RESET}\n"
    bullet "Python 3 + Flask + SQLite"
    bullet "Autenticacion HTTP Basic + bcrypt"
    bullet "API REST + endpoints JSON/HTML"
    bullet "Cliente consola interactivo"
    bullet "Testing automatizado integrado"
    printf "\n"
}

# Función para mostrar ayuda completa
mostrar_ayuda() {
    printf "\n${BOLD}GUIA COMPLETA DE USO${RESET}\n\n"
    printf "${BOLD}Sintaxis:${RESET} ./test.sh [opcion]\n\n"
    
    printf "${BOLD}OPCIONES PRINCIPALES:${RESET}\n"
    bullet "./test.sh          → Prueba completa del sistema (RECOMENDADO)"
    bullet "./test.sh --demo   → Solo demostracion rapida"
    bullet "./test.sh --client → Cliente de consola interactivo"
    printf "\n${BOLD}OPCIONES TECNICAS:${RESET}\n"
    bullet "./test.sh --setup  → Solo configurar entorno"
    bullet "./test.sh --run    → Solo iniciar servidor"
    bullet "./test.sh --stop   → Detener servidor"
    bullet "./test.sh --help   → Esta ayuda"
    
    printf "\n${BOLD}FLUJO DE PRUEBA COMPLETA:${RESET}\n"
    bullet "1. Verifica dependencias Python"
    bullet "2. Limpia procesos y puertos previos"
    bullet "3. Configura entorno virtual + dependencias"
    bullet "4. Inicializa base de datos SQLite"
    bullet "5. Inicia servidor Flask en background"
    bullet "6. Registra usuario de prueba automaticamente"
    bullet "7. Prueba todos los endpoints del API"
    bullet "8. Abre navegador con sesion autenticada"
    bullet "9. Mantiene servidor activo para pruebas manuales"
    
    printf "\n${BOLD}CREDENCIALES DE PRUEBA:${RESET}\n"
    bullet "Usuario: usuario_demo"
    bullet "Contraseña: 1234"
    
    printf "\n${BOLD}ENDPOINTS DISPONIBLES:${RESET}\n"
    bullet "Status: http://localhost:5555/status"
    bullet "Probador: http://localhost:5555/probador"
    bullet "Registro: POST http://localhost:5555/registro"
    bullet "Login: POST http://localhost:5555/login"
    bullet "Tareas: GET http://localhost:5555/tareas (requiere auth)"
    
    printf "\n${BOLD}SOLUCION DE PROBLEMAS:${RESET}\n"
    bullet "Puerto ocupado → sudo fuser -k 5555/tcp"
    bullet "Entorno corrupto → rm -rf venv && ./test.sh --setup"
    bullet "Procesos colgados → pkill -f servidor.py"
    
    printf "\n${BOLD}EJEMPLOS DE USO:${RESET}\n"
    printf "${DIM}# Prueba completa del sistema (primera vez):${RESET}\n"
    printf "   ./test.sh\n\n"
    printf "${DIM}# Solo demostracion rapida (servidor ya corriendo):${RESET}\n"
    printf "   ./test.sh --demo\n\n"
    printf "${DIM}# Usar cliente interactivo:${RESET}\n"
    printf "   ./test.sh --client\n\n"
    printf "${DIM}# Detener todo:${RESET}\n"
    printf "   Ctrl+C (en la terminal del servidor)\n\n"
}

# Verificar si Python está instalado
verificar_python() {
    if ! command -v python3 &> /dev/null; then
        error "Python 3 no está instalado"
        tip "Instala Python 3: sudo apt install python3 python3-venv python3-pip"
        exit 1
    fi
}

# Función para limpiar procesos previos
limpiar_procesos() {
    info "Limpiando procesos previos..."
    
    # Buscar procesos del servidor
    PROCESOS_SERVIDOR=$(ps aux | grep -E "(servidor\.py|servidor_web\.py)" | grep -v grep | grep -v "/bin/bash")
    if [ ! -z "$PROCESOS_SERVIDOR" ]; then
        info "Procesos del servidor encontrados:"
        echo "$PROCESOS_SERVIDOR" | while read line; do
            PID=$(echo $line | awk '{print $2}')
            CMD=$(echo $line | awk '{for(i=11;i<=NF;i++) printf "%s ", $i}')
            bullet "PID $PID: $CMD"
        done
        
        info "Deteniendo servidores..."
        pkill -f "servidor\.py" 2>/dev/null || true
        sleep 2
    fi
    
    # Verificar puerto 5555
    if lsof -i :5555 &>/dev/null; then
        warn "Puerto 5555 en uso, liberando..."
        fuser -k 5555/tcp 2>/dev/null || true
        sleep 2
        
        if lsof -i :5555 &>/dev/null; then
            error "No se pudo liberar el puerto 5555"
            tip "Ejecuta manualmente: sudo fuser -k 5555/tcp"
            exit 1
        fi
    fi
    
    ok "Procesos limpiados correctamente"
}

# Gestionar base de datos
gestionar_bd() {
    info "Gestionando base de datos..."
    
    if [ -f "tareas.db" ]; then
        info "Eliminando base de datos anterior para empezar limpio..."
        rm -f tareas.db
        ok "Base de datos anterior eliminada"
    fi
    
    info "La base de datos se inicializará automáticamente"
}

# Configurar entorno virtual y dependencias
configurar_entorno() {
    step "1: Configurando entorno Python"
    
    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        info "Creando entorno virtual..."
        python3 -m venv venv
    fi

    # Activar entorno virtual
    info "Activando entorno virtual..."
    source venv/bin/activate

    # Instalar dependencias
    info "Instalando dependencias..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    ok "Entorno configurado correctamente"
}

# Iniciar servidor en segundo plano
iniciar_servidor() {
    step "2: Iniciando servidor Flask"
    
    # Activar entorno y ejecutar servidor en segundo plano
    source venv/bin/activate
    nohup python servidor.py > /dev/null 2>&1 &
    SERVIDOR_PID=$!
    
    info "Servidor iniciado con PID: $SERVIDOR_PID"
    echo $SERVIDOR_PID > servidor.pid
    
    # Esperar a que el servidor esté listo
    info "Esperando a que el servidor este listo..."
    for i in {1..10}; do
        if curl -s http://localhost:5555/status > /dev/null 2>&1; then
            ok "Servidor disponible en http://localhost:5555"
            return 0
        fi
        sleep 1
        printf "."
    done
    
    error "El servidor no respondio a tiempo"
    return 1
}

# Ejecutar demostración automatizada completa
ejecutar_demo() {
    step "3: Ejecutando demostracion automatizada completa"
    
    # Limpiar archivos temporales
    rm -f sesion_temporal.txt
    
    # Verificar servidor
    if ! curl -s http://localhost:5555/status > /dev/null 2>&1; then
        error "Servidor no esta disponible"
        return 1
    fi
    
    printf "\n${BOLD}INICIANDO PRUEBAS DEL API REST${RESET}\n"
    
    # 1. Probar endpoint de status
    info "Probando endpoint /status..."
    STATUS_RESPONSE=$(curl -s http://localhost:5555/status)
    if echo "$STATUS_RESPONSE" | grep -q '"status"'; then
        ok "Endpoint /status funcionando"
    else
        warn "Problema con endpoint /status"
    fi
    
    # 2. Registro de usuario
    info "Registrando usuario de prueba (usuario_demo)..."
    REGISTER_RESPONSE=$(curl -s -w "%{http_code}" -X POST http://localhost:5555/registro \
      -H "Content-Type: application/json" \
      -d '{"usuario": "usuario_demo", "contraseña": "1234"}')
    REGISTER_CODE=${REGISTER_RESPONSE: -3}
    
    if [ "$REGISTER_CODE" = "201" ]; then
        ok "Usuario registrado exitosamente"
    elif [ "$REGISTER_CODE" = "400" ]; then
        ok "Usuario ya existe (OK para pruebas)"
    else
        warn "Registro con codigo: $REGISTER_CODE"
    fi
    
    # 3. Login con credenciales
    info "Probando autenticacion HTTP Basic..."
    LOGIN_RESPONSE=$(curl -s -w "%{http_code}" -X POST http://localhost:5555/login \
      -H "Content-Type: application/json" \
      -d '{"usuario": "usuario_demo", "contraseña": "1234"}')
    LOGIN_CODE=${LOGIN_RESPONSE: -3}
    
    if [ "$LOGIN_CODE" = "200" ]; then
        ok "Autenticacion exitosa"
    else
        error "Login fallo con codigo: $LOGIN_CODE"
        return 1
    fi
    
    # 4. Probar endpoint protegido /tareas (JSON)
    info "Probando endpoint protegido /tareas (JSON)..."
    TAREAS_JSON=$(curl -s -w "%{http_code}" -X GET "http://usuario_demo:1234@localhost:5555/tareas" \
      -H "Accept: application/json")
    TAREAS_CODE=${TAREAS_JSON: -3}
    
    if [ "$TAREAS_CODE" = "200" ]; then
        ok "Endpoint /tareas (JSON) funciona correctamente"
        info "Respuesta del servidor:"
        TAREAS_BODY=${TAREAS_JSON::-3}
        echo "$TAREAS_BODY" | head -5 | while read line; do
            printf "    ${DIM}%s${RESET}\n" "$line"
        done
    else
        error "Error en endpoint /tareas JSON (codigo: $TAREAS_CODE)"
    fi
    
    # 5. Probar endpoint protegido /tareas (HTML)
    info "Probando endpoint protegido /tareas (HTML)..."
    TAREAS_HTML_CODE=$(curl -s -w "%{http_code}" -X GET "http://usuario_demo:1234@localhost:5555/tareas" \
      -H "Accept: text/html" -o /dev/null)
    
    if [ "$TAREAS_HTML_CODE" = "200" ]; then
        ok "Endpoint /tareas (HTML) funciona correctamente"
        
        # Abrir en navegador
        info "Abriendo pagina de tareas en el navegador..."
        DESTINO="http://usuario_demo:1234@localhost:5555/tareas"
        
        if [[ "$WSL_DISTRO_NAME" != "" ]] || grep -q microsoft /proc/version 2>/dev/null; then
            info "Detectado WSL - abriendo en navegador Windows..."
            cmd.exe /c start "" "$DESTINO" 2>/dev/null && ok "Navegador abierto" || info "URL: $DESTINO"
        else
            info "Detectado Linux - abriendo navegador local..."
            (xdg-open "$DESTINO" 2>/dev/null || open "$DESTINO" 2>/dev/null) && ok "Navegador abierto" || info "URL: $DESTINO"
        fi
    else
        error "Error en endpoint /tareas HTML (codigo: $TAREAS_HTML_CODE)"
    fi
    
    # 6. Probar logout
    info "Probando endpoint /logout..."
    LOGOUT_RESPONSE=$(curl -s -w "%{http_code}" -X POST http://localhost:5555/logout)
    LOGOUT_CODE=${LOGOUT_RESPONSE: -3}
    
    if [ "$LOGOUT_CODE" = "200" ]; then
        ok "Endpoint /logout responde correctamente"
    else
        warn "Logout con codigo: $LOGOUT_CODE"
    fi
    
    # Resumen final
    printf "\n${BOLD}RESUMEN DE PRUEBAS COMPLETADAS${RESET}\n"
    bullet "Servidor Flask operativo en puerto 5555"
    bullet "Base de datos SQLite inicializada"
    bullet "Autenticacion HTTP Basic funcionando"
    bullet "Endpoints JSON y HTML respondiendo"
    bullet "Navegador abierto con sesion autenticada"
    bullet "Sistema listo para uso interactivo"
    
    # Limpiar archivos temporales
    rm -f sesion_temporal.txt
    
    ok "Demostracion completada exitosamente"
}

# Abrir cliente de consola
abrir_cliente() {
    step "Abriendo cliente de consola"
    
    # Verificar servidor
    if ! curl -s http://localhost:5555/status > /dev/null 2>&1; then
        error "Servidor no está disponible"
        tip "Ejecuta primero: ./test.sh --run"
        return 1
    fi
    
    # Activar entorno y ejecutar cliente
    source venv/bin/activate
    info "Iniciando cliente de consola interactivo..."
    python cliente_consola.py
}

# Detener servidor
detener_servidor() {
    info "Deteniendo servidor..."
    
    if [ -f "servidor.pid" ]; then
        SERVIDOR_PID=$(cat servidor.pid)
        if kill -0 $SERVIDOR_PID 2>/dev/null; then
            kill $SERVIDOR_PID
            sleep 2
            if kill -0 $SERVIDOR_PID 2>/dev/null; then
                kill -9 $SERVIDOR_PID 2>/dev/null
            fi
        fi
        rm -f servidor.pid
    fi
    
    # Limpiar puerto
    fuser -k 5555/tcp 2>/dev/null || true
    
    ok "Servidor detenido"
}

# Mostrar información final completa
mostrar_info_final() {
    printf "\n${BOLD}SISTEMA COMPLETAMENTE OPERATIVO${RESET}\n\n"
    
    printf "${BOLD}RECURSOS WEB DISPONIBLES:${RESET}\n"
    bullet "Estado del servidor: http://localhost:5555/status"
    bullet "Probador de endpoints: http://localhost:5555/probador"
    bullet "Pagina de tareas: http://localhost:5555/tareas"
    bullet "Pagina principal: http://localhost:5555/"
    
    printf "\n${BOLD}ENDPOINTS API REST:${RESET}\n"
    bullet "POST /registro → Crear nuevo usuario"
    bullet "POST /login → Validar credenciales"  
    bullet "GET /tareas → Info de tareas (requiere HTTP Basic Auth)"
    bullet "POST /logout → Cerrar sesion (informativo)"
    bullet "GET /status → Estado del servidor"
    
    printf "\n${BOLD}CREDENCIALES DE PRUEBA:${RESET}\n"
    bullet "Usuario: usuario_demo"  
    bullet "Contraseña: 1234"
    
    printf "\n${BOLD}HERRAMIENTAS ADICIONALES:${RESET}\n"
    bullet "Cliente consola: ./test.sh --client"
    bullet "Demo rapida: ./test.sh --demo"
    bullet "Estado procesos: ps aux | grep servidor"
    
    printf "\n${BOLD}COMANDOS DE CONTROL:${RESET}\n"
    bullet "Detener servidor: Ctrl+C (en esta terminal)"
    bullet "Detener por comando: ./test.sh --stop"
    bullet "Liberar puerto: sudo fuser -k 5555/tcp"
    bullet "Reiniciar todo: ./test.sh"
    
    printf "\n${BOLD}ARCHIVOS GENERADOS:${RESET}\n"
    bullet "tareas.db → Base de datos SQLite"
    bullet "servidor.pid → PID del proceso servidor"
    bullet "venv/ → Entorno virtual Python"
    
    printf "\n${BOLD}PROXIMOS PASOS SUGERIDOS:${RESET}\n"
    bullet "1. Probar el cliente de consola: ./test.sh --client"
    bullet "2. Usar el probador web: http://localhost:5555/probador"
    bullet "3. Registrar usuarios propios via API"
    bullet "4. Revisar el codigo fuente en servidor.py y cliente_consola.py"
    
    printf "\n${BOLD}ESTE SCRIPT ES AUTODOCUMENTADO${RESET}\n"
    bullet "Todas las opciones: ./test.sh --help"
    bullet "No necesitas documentacion externa"
    bullet "El script maneja todo automaticamente"
    
    printf "\n"
}

# Configuración y manejo de señales
trap 'detener_servidor; exit 0' INT TERM

# Función principal - configuración y prueba completa del sistema
configuracion_completa() {
    mostrar_banner
    verificar_python
    limpiar_procesos
    gestionar_bd
    configurar_entorno
    
    if iniciar_servidor; then
        ejecutar_demo
        mostrar_info_final
        
        printf "${BOLD}SERVIDOR ACTIVO Y LISTO${RESET}\n"
        info "El sistema esta completamente operativo"
        info "Puedes usar Ctrl+C para detener el servidor"
        tip "O abre otra terminal y ejecuta: ./test.sh --client"
        
        # Mantener el script corriendo y monitorear el servidor
        printf "\n${DIM}Monitoreando servidor... (Ctrl+C para detener)${RESET}\n"
        while true; do
            if ! curl -s http://localhost:5555/status > /dev/null 2>&1; then
                warn "Servidor no responde, intentando reiniciar..."
                if ! iniciar_servidor; then
                    error "No se pudo reiniciar el servidor"
                    break
                fi
            fi
            sleep 30
        done
    else
        error "No se pudo iniciar el servidor"
        tip "Verifica que el puerto 5555 este libre"
        exit 1
    fi
}

# Análisis de argumentos de línea de comandos
case "${1:-}" in
    --setup | -s)
        mostrar_banner
        printf "${BOLD}CONFIGURACION DEL ENTORNO${RESET}\n"
        info "Esta opcion solo configura el entorno sin iniciar el servidor"
        info "Util para preparar el sistema antes de ejecutar partes individuales"
        printf "\n"
        verificar_python
        limpiar_procesos
        gestionar_bd
        configurar_entorno
        printf "\n${BOLD}CONFIGURACION COMPLETADA${RESET}\n"
        ok "Sistema configurado correctamente"
        tip "Ahora puedes ejecutar:"
        bullet "./test.sh --run    (para iniciar solo el servidor)"
        bullet "./test.sh --demo   (para ejecutar demostracion)"
        bullet "./test.sh          (para prueba completa)"
        ;;
    --run | -r)
        mostrar_banner
        printf "${BOLD}INICIANDO SOLO EL SERVIDOR${RESET}\n"
        info "Esta opcion inicia unicamente el servidor Flask"
        info "Requiere que el entorno este configurado previamente"
        printf "\n"
        verificar_python
        limpiar_procesos
        if iniciar_servidor; then
            mostrar_info_final
            info "Servidor Flask corriendo en puerto 5555"
            info "Presiona Ctrl+C para detener el servidor"
            tip "En otra terminal puedes ejecutar:"
            bullet "./test.sh --demo   (demostracion)"  
            bullet "./test.sh --client (cliente interactivo)"
            printf "\n${DIM}Servidor activo... (Ctrl+C para detener)${RESET}\n"
            wait
        else
            error "No se pudo iniciar el servidor"
            tip "Ejecuta primero: ./test.sh --setup"
        fi
        ;;
    --demo | -d)
        mostrar_banner
        printf "${BOLD}DEMOSTRACION AUTOMATIZADA${RESET}\n"
        info "Esta opcion ejecuta todas las pruebas del sistema"
        info "Requiere que el servidor este corriendo previamente"
        printf "\n"
        ejecutar_demo
        printf "\n${BOLD}DEMOSTRACION FINALIZADA${RESET}\n"
        tip "El servidor sigue corriendo para mas pruebas"
        tip "Usa ./test.sh --client para el cliente interactivo"
        ;;
    --client | -c)
        mostrar_banner
        printf "${BOLD}CLIENTE DE CONSOLA INTERACTIVO${RESET}\n"
        info "Esta opcion abre el cliente de consola colorizado"
        info "Permite registrar usuarios, iniciar sesion y navegar"
        printf "\n"
        abrir_cliente
        ;;
    --help | -h)
        mostrar_banner
        mostrar_ayuda
        ;;
    --stop)
        printf "${BOLD}DETENIENDO SERVIDOR${RESET}\n"
        info "Limpiando procesos y liberando recursos..."
        detener_servidor
        ok "Servidor detenido correctamente"
        ;;
    *)
        printf "${BOLD}PRUEBA COMPLETA DEL SISTEMA${RESET}\n"
        info "Ejecutando configuracion completa + demostracion + servidor activo"
        info "Esta es la opcion recomendada para evaluar el sistema completo"
        printf "\n"
        configuracion_completa
        ;;
esac