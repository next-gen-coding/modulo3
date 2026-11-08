"""Comprobacion independiente de HU-10 contra las tablas de ejemplo de las reglas.

Es la revision humana del resultado (como abrir la app y probarla): no forma parte de app/ ni de la fabrica.
Uso, desde la raiz de la fabrica y con la app desplegada:  python evidencias/comprobar_hu10.py
Otra URL de la API:  URL_API=http://localhost:8011 python evidencias/comprobar_hu10.py
"""
import os
import uuid

import httpx

c = httpx.Client(base_url=os.environ.get("URL_API", "http://localhost:8000") + "/api", timeout=15,
                 follow_redirects=True)
fallas = 0

ANTIGUEDAD = "Necesitas al menos un año de antigüedad para solicitar vacaciones"
SIN_HABILES = "El periodo no incluye días hábiles"
EXCEDE = "La solicitud excede tus días disponibles: te quedan {}"
ORDEN = "La fecha de fin no puede ser anterior a la de inicio"
MISMO_ANIO = "Las vacaciones se solicitan dentro de un mismo año"
NO_EXISTE = "Empleado no encontrado"


def empleado(fecha_ingreso: str = "2024-03-10") -> int:
    """Registra un empleado nuevo (correo unico) y devuelve su id."""
    datos = {"nombre": "Prueba Vacaciones", "correo": f"vac-{uuid.uuid4().hex[:10]}@empresa.com",
             "puesto": "Analista", "departamento": "Operaciones", "fecha_ingreso": fecha_ingreso}
    r = c.post("/empleados", json=datos)
    r.raise_for_status()
    return r.json()["id"]


def pedir(eid: int, inicio: str, fin: str) -> httpx.Response:
    """Solicita vacaciones para el empleado eid."""
    return c.post(f"/empleados/{eid}/vacaciones", json={"fecha_inicio": inicio, "fecha_fin": fin})


def revisar(nombre: str, r: httpx.Response, codigo: int, **esperado) -> None:
    """Compara el codigo HTTP y los campos esperados; imprime OK o FALLA."""
    global fallas
    try:
        cuerpo = r.json()
    except ValueError:
        cuerpo = {}
    ok = r.status_code == codigo and all(cuerpo.get(k) == v for k, v in esperado.items())
    fallas += not ok
    print("OK   " if ok else "FALLA", f"{nombre} -> {r.status_code} {r.text[:150]}")


# Regla 1 - Antiguedad
revisar("R1 ingreso 2025-12-21, inicio 2026-12-21 (aniversario exacto)",
        pedir(empleado("2025-12-21"), "2026-12-21", "2026-12-31"), 201, dias_habiles=8, dias_disponibles=4)
revisar("R1 ingreso 2025-12-21, inicio 2026-12-18 (le faltan dias)",
        pedir(empleado("2025-12-21"), "2026-12-18", "2026-12-18"), 422, detail=ANTIGUEDAD)
revisar("R1 ingreso 2024-03-10, inicio 2026-07-06",
        pedir(empleado("2024-03-10"), "2026-07-06", "2026-07-10"), 201, dias_habiles=5)
revisar("R1 ingreso 2024-02-29, inicio 2025-02-28 (aniversario es 1 de marzo)",
        pedir(empleado("2024-02-29"), "2025-02-28", "2025-02-28"), 422, detail=ANTIGUEDAD)
revisar("R1 ingreso 2024-02-29, inicio 2025-03-03",
        pedir(empleado("2024-02-29"), "2025-03-03", "2025-03-03"), 201, dias_habiles=1, dias_disponibles=11)

# Regla 3 - Tope anual de 12 dias habiles
e = empleado()
revisar("R3 usados 0, pide 6-10 jul (5)", pedir(e, "2026-07-06", "2026-07-10"), 201, dias_habiles=5, dias_disponibles=7)
revisar("R3 usados 5, pide 13-21 jul (7, exacto)", pedir(e, "2026-07-13", "2026-07-21"), 201, dias_habiles=7, dias_disponibles=0)
revisar("R3 usados 12, pide 1", pedir(e, "2026-08-03", "2026-08-03"), 422, detail=EXCEDE.format(0))
e = empleado()
revisar("R3 usados 0, pide 3-6 ago (4)", pedir(e, "2026-08-03", "2026-08-06"), 201, dias_habiles=4, dias_disponibles=8)
revisar("R3 usados 4, pide 10-20 ago (9)", pedir(e, "2026-08-10", "2026-08-20"), 422, detail=EXCEDE.format(8))
g = c.get(f"/empleados/{e}/vacaciones", params={"anio": 2026})
revisar("GET saldo 2026 (usados 4)", g, 200, anio=2026, dias_por_anio=12, dias_usados=4, dias_disponibles=8)
sol = g.json().get("solicitudes", [{}])
global_ok = len(sol) == 1 and set(sol[0]) == {"id", "empleado_id", "fecha_inicio", "fecha_fin", "dias_habiles"} \
    and sol[0].get("empleado_id") == e and sol[0].get("dias_habiles") == 4
fallas += not global_ok
print("OK   " if global_ok else "FALLA", "GET solicitudes con id, empleado_id, fecha_inicio, fecha_fin, dias_habiles")

# Regla 2 - Dias habiles (sin sabados, domingos ni festivos)
revisar("R2 2026-09-14..18, festivo 16 sep", pedir(empleado(), "2026-09-14", "2026-09-18"), 201, dias_habiles=4)
revisar("R2 2026-03-16..20, festivo 16 mar", pedir(empleado(), "2026-03-16", "2026-03-20"), 201, dias_habiles=4)
revisar("R2 2027-03-15..19, festivo 15 mar", pedir(empleado(), "2027-03-15", "2027-03-19"), 201, dias_habiles=4)
revisar("R2 2026-07-11..12, fin de semana", pedir(empleado(), "2026-07-11", "2026-07-12"), 422, detail=SIN_HABILES)
revisar("R2 2026-04-04..05, fin de semana", pedir(empleado(), "2026-04-04", "2026-04-05"), 422, detail=SIN_HABILES)

# Otras validaciones
revisar("404 empleado inexistente", pedir(999999, "2026-07-06", "2026-07-10"), 404, detail=NO_EXISTE)
revisar("fin anterior a inicio", pedir(empleado(), "2026-07-10", "2026-07-06"), 422, detail=ORDEN)
revisar("cruza de anio", pedir(empleado(), "2026-12-28", "2027-01-08"), 422, detail=MISMO_ANIO)

print(f"\nResultado: {fallas} fallas")
