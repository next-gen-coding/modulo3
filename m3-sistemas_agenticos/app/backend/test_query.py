#!/usr/bin/env python
from datetime import date
from database import SessionLocal, init_db
from models import Empleado, Vacacion
from sqlalchemy import func

init_db()
db = SessionLocal()

try:
    empleado = db.query(Empleado).filter(Empleado.id == 1).first()
    print(f"Empleado: {empleado.nombre if empleado else 'No encontrado'}")

    # Prueba la query con func.strftime
    fecha_inicio = date(2026, 7, 6)
    resultado = db.query(Vacacion).filter(
        Vacacion.empleado_id == 1,
        func.strftime('%Y', Vacacion.fecha_inicio) == str(fecha_inicio.year)
    ).all()
    print(f"Vacaciones encontradas: {len(resultado)}")
    print("OK: Query exitosa")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
