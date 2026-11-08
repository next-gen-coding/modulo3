"""Tests API para HU-10: Solicitar vacaciones."""
import uuid
from datetime import datetime
import httpx
import pytest


@pytest.fixture
def client(url_api):
    """Cliente HTTP para la API."""
    return httpx.Client(base_url=url_api)


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


def test_cp_hu10_01(client):
    """CP-HU10-01: Solicitar vacaciones dentro del tope anual."""
    correo = f"cp01-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1001, "Juan", correo, "Ingeniero", "IT", "2024-01-15")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["dias_habiles"] == 5
    assert data["dias_disponibles"] == 7


def test_cp_hu10_02(client):
    """CP-HU10-02: Usar exactamente los días disponibles en el año."""
    correo = f"cp02-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1002, "Maria", correo, "Analista", "IT", "2024-01-15")

    # Crear una solicitud de 5 días primero
    client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-02-02", "fecha_fin": "2026-02-06"}
    )

    # Segunda solicitud de 7 días (exactamente lo que le queda)
    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-07-13", "fecha_fin": "2026-07-21"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["dias_habiles"] == 7
    assert data["dias_disponibles"] == 0


def test_cp_hu10_03(client):
    """CP-HU10-03: El periodo incluye festivos."""
    correo = f"cp03-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1003, "Carlos", correo, "Gerente", "IT", "2024-01-15")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-03-16", "fecha_fin": "2026-03-20"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["dias_habiles"] == 4


def test_cp_hu10_04(client):
    """CP-HU10-04: El periodo incluye fines de semana."""
    correo = f"cp04-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1004, "Rosa", correo, "Developer", "IT", "2024-01-15")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-03-21", "fecha_fin": "2026-04-01"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["dias_habiles"] == 8


def test_cp_hu10_05(client):
    """CP-HU10-05: Solicitar en el mes de diciembre con festivo incluido."""
    correo = f"cp05-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1005, "Luis", correo, "QA", "IT", "2024-01-15")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["dias_habiles"] == 8


def test_cp_hu10_06(client):
    """CP-HU10-06: Rechazar solicitud sin cumplir un año."""
    correo = f"cp06-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1006, "Ana", correo, "Ingeniero", "IT", "2025-12-21")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2025-12-18", "fecha_fin": "2025-12-20"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "Necesitas al menos un año de antigüedad para solicitar vacaciones"


def test_cp_hu10_07(client):
    """CP-HU10-07: Permitir solicitud exactamente en el primer aniversario."""
    correo = f"cp07-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1007, "Diego", correo, "Manager", "IT", "2025-12-21")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-23"}
    )

    assert resp.status_code == 201


def test_cp_hu10_08(client):
    """CP-HU10-08: Rechazar solicitud un día antes del primer aniversario."""
    correo = f"cp08-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1008, "Sofia", correo, "Developer", "IT", "2025-12-21")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-12-20", "fecha_fin": "2026-12-22"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "Necesitas al menos un año de antigüedad para solicitar vacaciones"


def test_cp_hu10_09(client):
    """CP-HU10-09: El aniversario de 29 de febrero se toma el 1 de marzo."""
    correo = f"cp09-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1009, "Pedro", correo, "QA", "IT", "2024-02-29")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2025-02-28", "fecha_fin": "2025-03-02"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "Necesitas al menos un año de antigüedad para solicitar vacaciones"


def test_cp_hu10_10(client):
    """CP-HU10-10: Permitir solicitud el 1 de marzo cuando el empleado ingresó el 29 de febrero."""
    correo = f"cp10-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1010, "Laura", correo, "Ingeniero", "IT", "2024-02-29")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2025-03-03", "fecha_fin": "2025-03-07"}
    )

    assert resp.status_code == 201


def test_cp_hu10_11(client):
    """CP-HU10-11: Rechazar cuando la fecha de fin es anterior a la de inicio."""
    correo = f"cp11-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1011, "Pablo", correo, "Developer", "IT", "2024-01-15")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-07-15", "fecha_fin": "2026-07-10"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "La fecha de fin no puede ser anterior a la de inicio"


def test_cp_hu10_12(client):
    """CP-HU10-12: Rechazar cuando las fechas están en años diferentes."""
    correo = f"cp12-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1012, "Elena", correo, "Analista", "IT", "2024-01-15")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2025-12-20", "fecha_fin": "2026-01-10"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "Las vacaciones se solicitan dentro de un mismo año"


def test_cp_hu10_13(client):
    """CP-HU10-13: Rechazar periodo que no incluye días hábiles (solo fines de semana)."""
    correo = f"cp13-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1013, "Marcos", correo, "QA", "IT", "2024-01-15")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-04-04", "fecha_fin": "2026-04-05"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp_hu10_14(client):
    """CP-HU10-14: Rechazar cuando se solicitan más días de los disponibles."""
    correo = f"cp14-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1014, "Isabel", correo, "Ingeniero", "IT", "2024-01-15")

    # Usar 12 días (todos los disponibles)
    client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-23"}
    )

    # Intentar usar 5 más
    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-08-03", "fecha_fin": "2026-08-07"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "La solicitud excede tus días disponibles: te quedan 0"


def test_cp_hu10_15(client):
    """CP-HU10-15: Rechazar cuando se piden más días de los que quedan."""
    correo = f"cp15-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1015, "Juan2", correo, "Analista", "IT", "2024-01-15")

    # Usar 4 días
    client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-02-02", "fecha_fin": "2026-02-05"}
    )

    # Intentar usar 9 días más (pide 9, le quedan 8)
    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-17"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "La solicitud excede tus días disponibles: te quedan 8"


def test_cp_hu10_16(client):
    """CP-HU10-16: Rechazar solicitud para empleado que no existe."""
    resp = client.post(
        "/api/empleados/999/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"}
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Empleado no encontrado"


def test_cp_hu10_17(client):
    """CP-HU10-17: Validar que existe el empleado antes de validar el formato de fechas."""
    resp = client.post(
        "/api/empleados/998/vacaciones",
        json={"fecha_inicio": "2026-07-15", "fecha_fin": "2026-07-10"}
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Empleado no encontrado"


def test_cp_hu10_18(client):
    """CP-HU10-18: Validar el orden de las fechas antes de la antigüedad."""
    correo = f"cp18-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1018, "Veronica", correo, "Developer", "IT", "2025-12-21")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2026-07-15", "fecha_fin": "2026-07-10"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "La fecha de fin no puede ser anterior a la de inicio"


def test_cp_hu10_19(client):
    """CP-HU10-19: Validar que el mismo año antes de validar antigüedad."""
    correo = f"cp19-{uuid.uuid4()}@test.com"
    emp_id = crear_empleado(client, 1019, "Victor", correo, "QA", "IT", "2025-12-21")

    resp = client.post(
        f"/api/empleados/{emp_id}/vacaciones",
        json={"fecha_inicio": "2025-12-20", "fecha_fin": "2026-01-10"}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"] == "Las vacaciones se solicitan dentro de un mismo año"
