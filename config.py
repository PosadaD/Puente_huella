# config.py
# Configuración del puente de huellas

# Estrategia del lector: "zkteco" para ZKTeco
# En el futuro: "digital_persona", "secugen", etc.
STRATEGY = "zkteco"

# Configuración del servidor
HOST = "0.0.0.0"  # 0.0.0.0 permite conexiones desde cualquier IP en tu red
PORT = 8080

# Configuración del lector
CAPTURE_TIMEOUT = 10  # segundos para esperar huella
ENROLL_COUNT = 3      # veces que se captura para registrar