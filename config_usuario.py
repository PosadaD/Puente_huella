# config_usuario.py
import os
import json
import socket

def auto_configurar():
    """Auto-detectar configuración óptima"""
    
    config = {
        "STRATEGY": "zkteco",
        "HOST": "0.0.0.0",
        "PORT": 8080,
        "CAPTURE_TIMEOUT": 10,
        "ENROLL_COUNT": 3
    }
    
    # Guardar configuración
    with open('config.py', 'w') as f:
        f.write(f"# Configuración auto-generada\n")
        for key, value in config.items():
            f.write(f"{key} = {repr(value)}\n")
    
    print("✅ Configuración generada automáticamente")
    return config

if __name__ == "__main__":
    auto_configurar()