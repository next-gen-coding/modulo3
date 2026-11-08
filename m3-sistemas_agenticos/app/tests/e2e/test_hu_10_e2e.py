"""Tests E2E para HU-10: Solicitar vacaciones."""
import uuid
import httpx
import pytest


@pytest.fixture
def client():
    """Cliente HTTP para crear datos previos."""
    return httpx.Client(base_url="http://localhost:8000")


def crear_empleado(client, numero_empleado, nombre, correo, puesto, departamento, fecha_ingreso):
    """Crea un empleado y retorna el id."""
    resp = client.post(
        "/api/empleados",
        json={
            "numero_empleado": numero_empleado,
            "nombre": nombre,
            "correo": correo,
            "puesto": puesto,
            "departamento": departamento,
            "fecha_ingreso": fecha_ingreso,
            "estado": "Activo",
        }
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def crear_solicitud_vacaciones(client, emp_id, fecha_inicio, fecha_fin):
    """Crea una solicitud de vacaciones."""
    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
    )
    return resp


def test_cp_hu10_20(page, url_web, client):
    """CP-HU10-20: Mostrar el formulario de vacaciones y registrar solicitud con éxito."""
    correo = f"cp20-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1020, "test1", correo, "Ingeniero", "IT", "2024-01-15")

    page.goto(f"{url_web}/")
    page.get_by_test_id(f"vacaciones-empleado-{emp_id}").click()

    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-solicitar").click()

    mensaje = page.get_by_test_id("mensaje-exito").text_content()
    assert "Solicitud registrada: 5 días hábiles. Te quedan 7 días disponibles." in mensaje


def test_cp_hu10_21(page, url_web, client):
    """CP-HU10-21: Mostrar días disponibles cuando hay solicitudes anteriores."""
    correo = f"cp21-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1021, "test2", correo, "Analista", "IT", "2024-01-15")

    # Crear una solicitud de 5 días
    crear_solicitud_vacaciones(client, emp_id, "2026-02-02", "2026-02-06")

    page.goto(f"{url_web}/")
    page.get_by_test_id(f"vacaciones-empleado-{emp_id}").click()

    disponibles = page.get_by_test_id("vacaciones-disponibles").text_content()
    assert "7" in disponibles


def test_cp_hu10_22(page, url_web, client):
    """CP-HU10-22: Mostrar error en la pantalla cuando se excede el tope anual."""
    correo = f"cp22-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1022, "test3", correo, "Developer", "IT", "2024-01-15")

    # Usar 12 días (todos disponibles)
    crear_solicitud_vacaciones(client, emp_id, "2026-07-06", "2026-07-23")

    page.goto(f"{url_web}/")
    page.get_by_test_id(f"vacaciones-empleado-{emp_id}").click()

    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-solicitar").click()

    mensaje = page.get_by_test_id("mensaje-error").text_content()
    assert "La solicitud excede tus días disponibles: te quedan 0" in mensaje


def test_cp_hu10_23(page, url_web, client):
    """CP-HU10-23: Mostrar error en la pantalla cuando no cumple antigüedad."""
    correo = f"cp23-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1023, "test4", correo, "QA", "IT", "2025-12-21")

    page.goto(f"{url_web}/")
    page.get_by_test_id(f"vacaciones-empleado-{emp_id}").click()

    page.get_by_test_id("vacaciones-fecha-inicio").fill("2025-12-18")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2025-12-20")
    page.get_by_test_id("vacaciones-solicitar").click()

    mensaje = page.get_by_test_id("mensaje-error").text_content()
    assert "Necesitas al menos un año de antigüedad para solicitar vacaciones" in mensaje
