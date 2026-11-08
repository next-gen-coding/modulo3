#!/usr/bin/env python
import sys
print("Python version:", sys.version)

try:
    print("Importando main...")
    import main
    print("✓ main importado correctamente")
    print("App:", main.app)
    print("OK")
except Exception as e:
    print(f"✗ Error al importar main: {e}")
    import traceback
    traceback.print_exc()
