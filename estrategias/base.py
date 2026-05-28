from abc import ABC, abstractmethod

class FingerprintStrategy(ABC):
    """Interfaz base para todos los lectores de huellas."""

    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa y conecta el lector. Retorna True si es exitoso."""
        pass

    @abstractmethod
    def get_device_count(self) -> int:
        """Retorna el número de dispositivos conectados."""
        pass

    @abstractmethod
    def capture_fingerprint(self, timeout: int = 10) -> dict:
        """
        Captura una huella.
        Retorna: {'success': bool, 'template': str, 'image': bytes, 'error': str}
        'template' es el template en formato hex (para guardar en DB)
        """
        pass

    @abstractmethod
    def identify_user(self, fingerprint_template: bytes) -> dict:
        """
        Identifica a un usuario comparando la huella capturada con la DB del dispositivo.
        Retorna: {'success': bool, 'user_id': int, 'score': int, 'error': str}
        """
        pass

    @abstractmethod
    def enroll_user(self, user_id: int, fingerprint_template: bytes) -> bool:
        """Registra una nueva huella en el dispositivo asociándola a un user_id."""
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario de la base de datos del dispositivo."""
        pass

    @abstractmethod
    def control_light(self, color: str) -> bool:
        """Controla la luz del lector (green, red, white)."""
        pass

    @abstractmethod
    def terminate(self):
        """Libera los recursos del dispositivo."""
        pass