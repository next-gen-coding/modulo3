import subprocess
import time

# Arrancar servidor fresco
print("Iniciando servidor en puerto 8011...")
subprocess.run(['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8011'])
