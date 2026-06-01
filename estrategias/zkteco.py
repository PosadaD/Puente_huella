# estrategias/zkteco.py
# Implementación para lectores ZKTeco - VERSIÓN CORREGIDA

import time
import base64
from PIL import Image
import io

try:
    from pyzkfp import ZKFP2
    ZKFP_AVAILABLE = True
except ImportError:
    ZKFP_AVAILABLE = False
    print("⚠️  pyzkfp no instalado. Usando modo simulación.")

class ZKTecoStrategy:
    """Estrategia para lectores de huellas ZKTeco"""
    
    def __init__(self):
        self.zkfp2 = None
        self.simulation_mode = not ZKFP_AVAILABLE
        self.device_count = 0
        
    def initialize(self):
        """Inicializa el dispositivo ZKTeco - CORREGIDO"""
        if self.simulation_mode:
            print("🔧 Modo simulación activado - No se requiere hardware")
            self.device_count = 1
            return True
            
        try:
            self.zkfp2 = ZKFP2()
            
            # ✅ CORREGIDO: Cambiado Initialize() por Init()
            self.zkfp2.Init()
            print("✅ ZKFP2 inicializado correctamente")
            
            # Obtener número de dispositivos conectados
            self.device_count = self.zkfp2.GetDeviceCount()
            print(f"📟 Dispositivos encontrados: {self.device_count}")
            
            if self.device_count > 0:
                # Abrir el primer dispositivo (índice 0)
                self.zkfp2.OpenDevice(0)
                print(f"✅ Conectado al dispositivo 0")
                
                # Opcional: Obtener información del dispositivo
                try:
                    width = self.zkfp2.GetImageWidth()
                    height = self.zkfp2.GetImageHeight()
                    print(f"📏 Resolución del sensor: {width}x{height}")
                except:
                    pass
                
                return True
            else:
                print("❌ No se encontraron dispositivos ZKTeco conectados")
                self.device_count = 0
                return False
                
        except Exception as e:
            print(f"❌ Error al inicializar: {e}")
            self.device_count = 0
            return False
    
    def get_device_count(self):
        """Devuelve el número de dispositivos conectados"""
        return self.device_count
    
    def capture_fingerprint(self, timeout=10):
        """Captura una huella digital - CORREGIDO"""
        if self.simulation_mode:
            return self._simulate_capture()
        
        try:
            start_time = time.time()
            
            # Encender luz verde mientras se espera
            try:
                self.zkfp2.Light('green')
            except:
                pass
            
            print(f"🔴 Esperando huella (max {timeout} segundos)...")
            
            while time.time() - start_time < timeout:
                # ✅ CORREGIDO: Usar correctamente AcquireFingerprint()
                capture = self.zkfp2.AcquireFingerprint()
                
                if capture:
                    # capture es una tupla: (template_bytes, image_bytes)
                    if isinstance(capture, tuple) and len(capture) >= 2:
                        template_bytes = capture[0]  # El template es el primer elemento
                        image_bytes = capture[1]      # La imagen es el segundo
                    else:
                        template_bytes = capture
                        image_bytes = None
                    
                    print("✅ Huella capturada correctamente")
                    
                    # Apagar luz
                    try:
                        self.zkfp2.Light('off')
                    except:
                        pass
                    
                    return {
                        'success': True,
                        'template_bytes': template_bytes,
                        'image': image_bytes
                    }
                
                time.sleep(0.1)  # Pequeña pausa para no saturar CPU
            
            # Timeout
            print("❌ Tiempo de espera agotado")
            return {
                'success': False,
                'error': 'Tiempo de espera agotado - No se detectó huella'
            }
            
        except Exception as e:
            print(f"❌ Error al capturar: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def identify_user(self, template_bytes):
        """Identifica un usuario - CORREGIDO"""
        if self.simulation_mode:
            return self._simulate_identify(template_bytes)
        
        try:
            # ✅ CORREGIDO: Usar DBIdentify() en lugar de Identify()
            fingerprint_id, score = self.zkfp2.DBIdentify(template_bytes)
            
            if fingerprint_id > 0:
                print(f"✅ Usuario identificado: ID={fingerprint_id}, Score={score}")
                return {
                    'success': True,
                    'user_id': fingerprint_id,
                    'score': score
                }
            else:
                print("❌ Huella no reconocida")
                return {
                    'success': False,
                    'error': 'Huella no reconocida'
                }
                
        except Exception as e:
            print(f"❌ Error en identificación: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def enroll_with_multiple_captures(self, user_id):
        """Registra un usuario con múltiples capturas - CORREGIDO"""
        if self.simulation_mode:
            return self._simulate_enroll(user_id)
        
        templates = []
        
        print(f"\n📝 Registrando usuario {user_id}")
        print("Coloca tu dedo en el lector cuando te indique\n")
        
        for i in range(3):  # 3 capturas
            print(f"✨ Captura {i+1} de 3")
            
            # Capturar huella
            result = self.capture_fingerprint()
            if not result['success']:
                return {
                    'success': False,
                    'error': f'Error en captura {i+1}: {result.get("error", "Desconocido")}'
                }
            
            templates.append(result['template_bytes'])
            print(f"✅ Captura {i+1} completada\n")
            
            if i < 2:
                print("🔄 Retira el dedo y espera 2 segundos...")
                time.sleep(2)
        
        # ✅ CORREGIDO: Usar DBMerge() y DBAdd()
        try:
            # Fusionar los 3 templates en uno
            regTemp, regTempLen = self.zkfp2.DBMerge(*templates)
            
            # Guardar en la base de datos del dispositivo
            result = self.zkfp2.DBAdd(user_id, regTemp)
            
            if result:
                print(f"✅ Usuario {user_id} registrado exitosamente en el dispositivo")
                return {
                    'success': True,
                    'user_id': user_id,
                    'template': regTemp
                }
            else:
                return {
                    'success': False,
                    'error': 'Error al guardar la huella en el dispositivo'
                }
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_user(self, user_id):
        """Elimina un usuario del dispositivo"""
        if self.simulation_mode:
            print(f"🗑️ Simulación: Usuario {user_id} eliminado")
            return True
        
        try:
            # ✅ Método correcto: DBDelete()
            result = self.zkfp2.DBDelete(user_id)
            return result
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False
    
    def control_light(self, color):
        """Controla la luz del lector - CORREGIDO"""
        if self.simulation_mode:
            print(f"💡 Simulación: Luz {color}")
            return
        
        try:
            # ✅ CORREGIDO: Usar Light() en lugar de EnableDevice()
            self.zkfp2.Light(color)  # 'green', 'red', 'white', 'off'
        except Exception as e:
            print(f"Error controlando luz: {e}")
    
    def terminate(self):
        """Limpia recursos y cierra conexiones"""
        if self.simulation_mode:
            return
        
        try:
            if self.zkfp2:
                # ✅ CORREGIDO: Terminate() está bien
                self.zkfp2.Terminate()
                print("🔌 Conexión con lector cerrada")
        except Exception as e:
            print(f"Error al terminar: {e}")
    
    # ================= MÉTODOS DE SIMULACIÓN =================
    
    def _simulate_capture(self):
        """Simula la captura de una huella"""
        import random
        import time
        
        time.sleep(1)
        
        if random.random() > 0.1:
            return {
                'success': True,
                'template_bytes': f"SIM_TEMPLATE_{random.randint(1, 9999)}",
                'image': None
            }
        else:
            return {
                'success': False,
                'error': 'Tiempo de espera agotado'
            }
    
    def _simulate_identify(self, template_bytes):
        """Simula la identificación de un usuario"""
        import random
        
        if random.random() > 0.5:
            user_id = random.choice([1001, 1002, 1003, 1004, 1005])
            return {
                'success': True,
                'user_id': user_id,
                'score': random.randint(75, 100)
            }
        else:
            return {
                'success': False,
                'error': 'Huella no reconocida'
            }
    
    def _simulate_enroll(self, user_id):
        """Simula el registro de un usuario"""
        import time
        
        for i in range(3):
            print(f"   Capturando dedo {i+1}...")
            time.sleep(1)
            print(f"   ✅ Captura {i+1} completada")
            if i < 2:
                print("   Retira el dedo...")
                time.sleep(1)
        
        return {
            'success': True,
            'user_id': user_id,
            'template': f"TEMPLATE_USER_{user_id}"
        }