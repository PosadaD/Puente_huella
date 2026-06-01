# build_exe.py
import os
import sys
import shutil
import subprocess

print("🔨 CONSTRUYENDO EJECUTABLE DEL PUENTE DE HUELLAS")
print("="*50)

# 1. Limpiar builds anteriores
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('BridgeHuellas.spec'):
    os.remove('BridgeHuellas.spec')

# 2. Instalar PyInstaller si no está
try:
    import PyInstaller
    print("✅ PyInstaller ya instalado")
except ImportError:
    print("📦 Instalando PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# 3. Construir el ejecutable
print("\n🔧 Construyendo ejecutable...")
subprocess.check_call([
    sys.executable, "-m", "PyInstaller",
    "--onefile",           # Un solo archivo
    "--name", "BridgeHuellas",
    "--console",           # Mostrar consola
    "--add-data", f"estrategias{os.pathsep}estrategias",
    "--add-data", f"config.py{os.pathsep}.",
    "--hidden-import", "flask",
    "--hidden-import", "flask_cors",
    "--hidden-import", "jinja2",
    "--hidden-import", "werkzeug",
    "bridge.py"
])

# 4. Crear versión sin consola (background)
print("\n🔧 Construyendo versión silenciosa...")
subprocess.check_call([
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--name", "BridgeHuellas_Background",
    "--noconsole",         # Sin ventana (corre en fondo)
    "--add-data", f"estrategias{os.pathsep}estrategias",
    "--add-data", f"config.py{os.pathsep}.",
    "--hidden-import", "flask",
    "--hidden-import", "flask_cors",
    "bridge.py"
])

# 5. Crear archivo ZIP para distribuir
print("\n📦 Creando paquete de distribución...")
shutil.make_archive(
    'PuenteHuellas_Windows',
    'zip',
    'dist'
)

print("\n" + "="*50)
print("✅ ¡COMPLETADO!")
print("\n📁 Archivos creados:")
print("   - dist/BridgeHuellas.exe (con consola - para debug)")
print("   - dist/BridgeHuellas_Background.exe (sin consola - para usuarios)")
print("   - PuenteHuellas_Windows.zip (para distribuir)")
print("\n💡 El usuario solo necesita descargar y hacer doble clic en el .exe")