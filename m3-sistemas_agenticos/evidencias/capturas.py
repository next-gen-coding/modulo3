"""Toma las capturas de evidencia con Playwright (app desplegada en 8080/8000).

Uso, desde la raíz de la fábrica:  python evidencias/capturas.py
"""
import uuid
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

DESTINO = Path("evidencias/capturas")
DESTINO.mkdir(parents=True, exist_ok=True)
emp = httpx.post("http://localhost:8000/api/empleados", json={
    "nombre": "Ana Vacaciones", "correo": f"ana-{uuid.uuid4().hex[:6]}@empresa.com", "puesto": "Analista",
    "departamento": "Operaciones", "fecha_ingreso": "2024-03-10"}).json()
with sync_playwright() as p:
    pagina = p.chromium.launch().new_page(viewport={"width": 1280, "height": 900})
    pagina.goto(Path("flujos/salidas/grafo_flujo_s4.html").resolve().as_uri())
    pagina.wait_for_selector("svg", timeout=20000)
    pagina.screenshot(path=DESTINO / "01-grafo-flujo-s4.png", full_page=True)
    pagina.goto("http://localhost:8080")
    pagina.get_by_test_id(f"vacaciones-empleado-{emp['id']}").wait_for()
    pagina.screenshot(path=DESTINO / "04-directorio.png", full_page=True)
    pagina.get_by_test_id(f"vacaciones-empleado-{emp['id']}").click()
    pagina.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    pagina.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-31")
    pagina.get_by_test_id("vacaciones-solicitar").click()
    pagina.get_by_test_id("mensaje-exito").wait_for()
    pagina.screenshot(path=DESTINO / "05-ui-solicitud-exitosa.png", full_page=True)
    pagina.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-11")
    pagina.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-12")
    pagina.get_by_test_id("vacaciones-solicitar").click()
    pagina.get_by_test_id("mensaje-error").wait_for()
    pagina.screenshot(path=DESTINO / "06-ui-error-sin-dias-habiles.png", full_page=True)
print(sorted(f.name for f in DESTINO.iterdir()))
