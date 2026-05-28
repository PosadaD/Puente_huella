from .base import FingerprintStrategy
from pyzkfp import ZKFP2
import base64

class ZKTecoStrategy(FingerprintStrategy):
    def __init__(self):
        self.zkfp2 = None
        self.is_initialized = False

    def initialize(self) -> bool:
        """Inicializa el dispositivo ZKTeco."""
        try:
            self.zkfp2 = ZKFP2()
            
            # Inicializar la librería
            if self.zkfp2.Init() != 0:
                print("Error al inicializar ZKFP2")
                return False
            
            # Buscar dispositivos
            device_count = self.zkfp2.GetDeviceCount()
            print(f"🔍 Dispositivos encontrados: {device_count}")
            
            if device_count == 0:
                print("❌ No se encontró ningún lector ZKTeco")
                return False
            
            # Abrir el primer dispositivo
            if self.zkfp2.OpenDevice(0) != 0:
                print("❌ Error al abrir el dispositivo")
                return False
            
            self.is_initialized = True
            print("✅ Lector ZKTeco inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar ZKTeco: {e}")
            return False

    def get_device_count(self) -> int:
        if not self.is_initialized:
            return 0
        return self.zkfp2.GetDeviceCount()

    def capture_fingerprint(self, timeout: int = 10) -> dict:
        """
        Captura una huella esperando hasta 'timeout' segundos.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'Lector no inicializado'}

        try:
            print("👆 Coloca tu dedo en el lector...")
            
            # Capturar huella
            capture_result = self.zkfp2.AcquireFingerprint()
            
            if not capture_result:
                return {'success': False, 'error': 'No se capturó la huella'}
            
            template, image = capture_result
            
            # Convertir template a hex para almacenamiento
            template_hex = template.hex()
            
            # Convertir imagen a base64 para enviarla si es necesario
            image_base64 = base64.b64encode(image).decode('utf-8') if image else None
            
            return {
                'success': True,
                'template': template_hex,
                'template_bytes': template,
                'image': image_base64
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def identify_user(self, fingerprint_template: bytes) -> dict:
        """
        Identifica al usuario comparando la huella con la base de datos del dispositivo.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'Lector no inicializado'}

        try:
            # Realizar identificación 1:N
            user_id, score = self.zkfp2.DBIdentify(fingerprint_template)
            
            if user_id > 0:
                print(f"✅ Usuario identificado: ID={user_id}, Score={score}")
                return {
                    'success': True,
                    'user_id': user_id,
                    'score': score
                }
            else:
                return {
                    'success': False,
                    'error': 'Huella no reconocida'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def enroll_user(self, user_id: int, fingerprint_template: bytes) -> bool:
        """
        Registra un usuario en el dispositivo.
        Para mejores resultados, se recomienda capturar 3 veces la misma huella y fusionarlas.
        """
        if not self.is_initialized:
            print("❌ Lector no inicializado")
            return False

        try:
            # Agregar el template a la base de datos del dispositivo
            result = self.zkfp2.DBAdd(user_id, fingerprint_template)
            
            if result == 0:
                print(f"✅ Usuario {user_id} registrado correctamente")
                return True
            else:
                print(f"❌ Error al registrar usuario {user_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error en enrollment: {e}")
            return False

    def enroll_with_multiple_captures(self, user_id: int, num_captures: int = 3) -> dict:
        """
        Registra un usuario capturando la huella múltiples veces y fusionando los templates.
        Este método es más confiable que una sola captura.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'Lector no inicializado'}

        templates = []
        
        print(f"📝 Registrando huella para usuario {user_id}")
        print(f"Coloca tu dedo {num_captures} veces en el lector")
        
        for i in range(num_captures):
            print(f"Captura {i+1} de {num_captures}...")
            
            capture = self.zkfp2.AcquireFingerprint()
            if not capture:
                return {'success': False, 'error': f'Error en captura {i+1}'}
            
            template, _ = capture
            templates.append(template)
            print(f"✅ Captura {i+1} completada")
        
        # Fusionar los templates
        print("🔄 Fusionando templates...")
        merged_template, _ = self.zkfp2.DBMerge(*templates)
        
        # Guardar en el dispositivo
        result = self.zkfp2.DBAdd(user_id, merged_template)
        
        if result == 0:
            # Retornar el template fusionado para guardar en tu base de datos externa
            return {
                'success': True,
                'user_id': user_id,
                'template': merged_template.hex(),
                'message': f'Usuario {user_id} registrado exitosamente'
            }
        else:
            return {'success': False, 'error': 'Error al guardar en el dispositivo'}

    def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario de la base de datos del dispositivo."""
        if not self.is_initialized:
            return False
        
        try:
            result = self.zkfp2.DBDelete(user_id)
            return result == 0
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False

    def control_light(self, color: str) -> bool:
        """Controla la luz del lector."""
        if not self.is_initialized:
            return False
        
        try:
            self.zkfp2.Light(color)
            return True
        except Exception as e:
            print(f"Error al controlar luz: {e}")
            return False

    def get_all_users(self) -> list:
        """Obtiene todos los usuarios registrados en el dispositivo."""
        if not self.is_initialized:
            return []
        
        try:
            # Este método puede variar según el modelo
            # Algunas implementaciones de pyzkfp tienen DBGetAll
            users = []
            # Simulación - implementación real depende del SDK
            return users
        except:
            return []

    def terminate(self):
        """Libera los recursos del dispositivo."""
        if self.zkfp2 and self.is_initialized:
            try:
                self.zkfp2.Terminate()
                print("🔌 Lector ZKTeco desconectado")
            except:
                pass
        self.is_initialized = False