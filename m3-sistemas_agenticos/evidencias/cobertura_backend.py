"""Mide la cobertura del backend: levanta la API en un hilo (puerto 8012) y corre tests/api contra ella.

Uso, desde la raíz de la fábrica:  python -m coverage run --source=app/backend evidencias/cobertura_backend.py
                                   python -m coverage report
"""
import os
import sys
import threading
import time
from pathlib import Path

import uvicorn

BACKEND = Path(__file__).resolve().parent.parent / "app" / "backend"
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))
import main  # noqa: E402

servidor = uvicorn.Server(uvicorn.Config(main.app, port=8012, log_level="warning"))
threading.Thread(target=servidor.run, daemon=True).start()
while not servidor.started:
    time.sleep(0.1)
os.environ["URL_API"] = "http://127.0.0.1:8012"
import pytest  # noqa: E402
codigo = pytest.main([str(BACKEND.parent / "tests" / "api"), "-q", "-p", "no:cacheprovider"])
servidor.should_exit = True
time.sleep(1)
sys.exit(codigo)
