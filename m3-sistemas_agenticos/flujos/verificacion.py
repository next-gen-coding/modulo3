"""Verificaciones deterministas: el código, no un agente, decide si un paso terminó bien.

Cada función devuelve (ok, log). El log regresa al agente responsable cuando algo falla.
"""
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

from agentes.base import APP, SALIDA


def _responde(url: str, intentos: int = 30) -> tuple[bool, str]:
    for _ in range(intentos):
        try:
            r = httpx.get(url, timeout=2)
            if r.status_code < 400:
                return True, f"{url} -> {r.status_code}"
        except httpx.HTTPError:
            pass
        time.sleep(1)
    return False, f"{url} no respondió en {intentos} s"


def _correr(comando: list[str], cwd: Path, timeout: int = 600) -> tuple[bool, str]:
    r = subprocess.run(comando, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode == 0, (r.stdout + r.stderr)[-4000:]


def verificar_backend() -> tuple[bool, str]:
    """Arranca el backend en el puerto 8010, consulta /api/salud y lo detiene."""
    if not (APP / "backend" / "main.py").exists():
        return False, "No existe app/backend/main.py"
    proceso = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8010"],
                               cwd=APP / "backend", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        ok, log = _responde("http://127.0.0.1:8010/api/salud", intentos=20)
    finally:
        proceso.terminate()
        salida = proceso.communicate(timeout=10)[0]
    return ok, log if ok else f"{log}\n{salida[-3000:]}"


def verificar_frontend() -> tuple[bool, str]:
    """Instala dependencias si faltan y comprueba que `npm run build` termina sin errores."""
    carpeta = APP / "frontend"
    if not (carpeta / "package.json").exists():
        return False, "No existe app/frontend/package.json"
    if not (carpeta / "node_modules").exists():
        ok, log = _correr(["npm", "install"], carpeta)
        if not ok:
            return False, log
    return _correr(["npm", "run", "build"], carpeta)


def verificar_app() -> tuple[bool, str]:
    ok_b, log_b = verificar_backend()
    ok_f, log_f = verificar_frontend()
    return ok_b and ok_f, f"## Backend\n{log_b}\n\n## Frontend\n{log_f}"


def redesplegar() -> tuple[bool, str]:
    """Reconstruye los contenedores sin pasar por un agente (para después de una corrección)."""
    ok, log = _correr(["docker", "compose", "up", "-d", "--build"], APP)
    return (verificar_despliegue() if ok else (False, log))


def verificar_despliegue() -> tuple[bool, str]:
    resultados = [_responde(u, intentos=60) for u in
                  ("http://localhost:8000/api/salud", "http://localhost:8080", "http://localhost:8080/api/salud")]
    return all(ok for ok, _ in resultados), "\n".join(log for _, log in resultados)


def verificar_pruebas_escritas(hu: str, ids_casos: list[str]) -> tuple[bool, str]:
    """Las pruebas se pueden recolectar y cada caso de prueba tiene al menos un test (trazabilidad)."""
    ok, log = _correr([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"], APP, timeout=120)
    if not ok:
        return False, log
    texto = "".join(p.read_text(encoding="utf-8") for p in (APP / "tests").rglob("test_*.py"))
    faltan = [i for i in ids_casos if i not in texto]
    return not faltan, log if not faltan else f"Casos sin test: {', '.join(faltan)}"


def ejecutar_pruebas(hu: str) -> tuple[bool, str]:
    """Corre todas las pruebas (API y E2E) contra la app desplegada y resume los fallos."""
    reporte = SALIDA / hu / "resultados.xml"
    entorno = {**os.environ, "URL_API": "http://localhost:8000", "URL_WEB": "http://localhost:8080"}
    r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "--tb=short", f"--junitxml={reporte}"],
                       cwd=APP, capture_output=True, text=True, timeout=900, env=entorno)
    fallos = []
    if reporte.exists():
        for caso in ET.parse(reporte).getroot().iter("testcase"):
            for problema in list(caso.findall("failure")) + list(caso.findall("error")):
                fallos.append(f"- {caso.get('classname')}::{caso.get('name')}\n  {(problema.get('message') or '')[:400]}")
    resumen = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "sin salida"
    return r.returncode == 0, f"{resumen}\n" + "\n".join(fallos)
