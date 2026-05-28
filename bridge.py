from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

# Cargar configuración
from config import STRATEGY, PORT, HOST

# Importar la estrategia seleccionada
if STRATEGY == "zkteco":
    from estrategias.zkteco import ZKTecoStrategy as Strategy
# Aquí agregarás más estrategias en el futuro
# elif STRATEGY == "digital_persona":
#     from estrategias.digital_persona import DigitalPersonaStrategy as Strategy
else:
    raise Exception(f"Estrategia '{STRATEGY}' no soportada")

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde Next.js

# Inicializar el lector
print(f"🚀 Iniciando puente con estrategia: {STRATEGY}")
fingerprint = Strategy()
if not fingerprint.initialize():
    print("❌ Error: No se pudo inicializar el lector")
    print("Verifica que el lector esté conectado y los drivers instalados")
    exit(1)

# Archivo para persistencia de templates (base de datos local)
TEMPLATES_DB_FILE = "templates_db.json"

def load_templates_db():
    """Carga la base de datos local de templates."""
    if os.path.exists(TEMPLATES_DB_FILE):
        with open(TEMPLATES_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_templates_db(db):
    """Guarda la base de datos local de templates."""
    with open(TEMPLATES_DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

# Endpoints de la API

@app.route('/health', methods=['GET'])
def health():
    """Verifica que el puente esté funcionando."""
    return jsonify({
        "status": "ok",
        "strategy": STRATEGY,
        "device_count": fingerprint.get_device_count()
    })

@app.route('/scan', methods=['POST'])
def scan():
    """
    Endpoint principal para registrar entrada/salida.
    Tu Next.js llama a este endpoint cuando un empleado coloca su dedo.
    """
    try:
        # 1. Capturar huella
        capture = fingerprint.capture_fingerprint()
        if not capture['success']:
            return jsonify(capture), 400
        
        # 2. Identificar al usuario
        identification = fingerprint.identify_user(capture['template_bytes'])
        
        if not identification['success']:
            return jsonify(identification), 404
        
        # 3. Devolver el user_id a Next.js
        return jsonify({
            "success": True,
            "user_id": str(identification['user_id']),
            "score": identification.get('score', 0)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/enroll', methods=['POST'])
def enroll():
    """
    Registra una nueva huella en el dispositivo.
    Tu panel de administración de Next.js llama a este endpoint.
    Espera: { "user_id": "123" }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"success": False, "error": "Se requiere user_id"}), 400
        
        # Convertir a entero (el SDK espera int)
        user_id = int(user_id)
        
        # Realizar enrollment con múltiples capturas
        result = fingerprint.enroll_with_multiple_captures(user_id)
        
        if result['success']:
            # Guardar el template en la base de datos local para persistencia
            db = load_templates_db()
            db[str(user_id)] = result['template']
            save_templates_db(db)
            
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Elimina un usuario del dispositivo."""
    try:
        result = fingerprint.delete_user(user_id)
        if result:
            # También eliminar de la DB local
            db = load_templates_db()
            if str(user_id) in db:
                del db[str(user_id)]
                save_templates_db(db)
            return jsonify({"success": True, "message": f"Usuario {user_id} eliminado"})
        else:
            return jsonify({"success": False, "error": "Error al eliminar"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/test/light/<color>', methods=['POST'])
def test_light(color):
    """Prueba la luz del lector (green, red, white)."""
    if color in ['green', 'red', 'white']:
        fingerprint.control_light(color)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Color inválido"}), 400

if __name__ == '__main__':
    print(f"""
    ╔══════════════════════════════════════╗
    ║   🔐 Puente de Huellas Digitales     ║
    ║                                      ║
    ║   Estrategia: {STRATEGY:<24}║
    ║   Puerto: {PORT:<30}║
    ║                                      ║
    ║   Endpoints disponibles:             ║
    ║   GET  /health                       ║
    ║   POST /scan                         ║
    ║   POST /enroll                       ║
    ║   DELETE /delete/&lt;id&gt;               ║
    ║   POST /test/light/&lt;color&gt;          ║
    ╚══════════════════════════════════════╝
    """)
    
    try:
        app.run(host=HOST, port=PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Cerrando puente...")
        fingerprint.terminate()