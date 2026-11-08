"""Lab 3C · Busca en auditoria.jsonl los intentos de escritura fuera del rol de cada agente.

auditoria.jsonl registra cada INTENTO de usar una herramienta, no si se permitió. Un intento
de escritura fuera de las rutas del agente es uno que su hook de rol (confinar_escritura) negó.
Uso, desde la raíz del repo (Mac, Linux y Windows):  python buscar_denegados.py
"""
import fnmatch
import json
import re
from pathlib import Path

# Las mismas rutas que ESCRITURA en agentes/desarrollador.py, despliegue.py y automatizador.py
PERMITIDO = {
    "desarrollador": ["backend/*", "frontend/*"],
    "automatizador": ["tests/*"],
    "despliegue": ["docker-compose.yml", "backend/Dockerfile", "backend/.dockerignore",
                   "frontend/Dockerfile", "frontend/.dockerignore", "frontend/nginx.conf"],
}

archivo = Path("auditoria.jsonl")
if not archivo.exists():
    raise SystemExit("No existe auditoria.jsonl: ¿corriste con DEFENSAS=0 o aún no corre ningún agente de Claude Code?")

encontrados = 0
for linea in archivo.read_text(encoding="utf-8").splitlines():
    registro = json.loads(linea)
    if registro["herramienta"] not in ("Write", "Edit", "MultiEdit"):
        continue
    m = re.search(r"'file_path': '([^']+)'", registro["entrada"])
    if not m:
        continue
    ruta = m.group(1).replace("\\\\", "/").replace("\\", "/")   # rutas de Windows -> /
    ruta = ruta.split("/app/", 1)[-1]                            # relativa a app/
    permitidas = PERMITIDO.get(registro["agente"], [])
    if not any(fnmatch.fnmatch(ruta, p) for p in permitidas):
        encontrados += 1
        print(f"{registro['agente']:14} {registro['herramienta']:9} {ruta}")
        print(f"{'':14} su rol solo permite: {', '.join(permitidas)}\n")

if encontrados == 0:
    print("Ningún intento de escritura fuera de rol: los agentes respetaron sus carpetas en esta ejecución.")
