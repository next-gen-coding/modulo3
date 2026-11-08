#!/usr/bin/env python
from main import app
from database import init_db, SessionLocal
from models import Vacacion

# Intentar inicializar la BD
init_db()

# Ver si la tabla existe
db = SessionLocal()
try:
    resultado = db.query(Vacacion).all()
    print('OK: Tabla de vacaciones existe')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
