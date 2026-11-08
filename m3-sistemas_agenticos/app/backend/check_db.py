#!/usr/bin/env python
import sqlite3
import os
from pathlib import Path

# Ruta a la BD
datos_dir = Path(__file__).parent / "datos"
db_path = datos_dir / "empleados.db"

if not db_path.exists():
    print(f"BD no existe: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ver todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tablas en la BD:")
for table in tables:
    print(f"  - {table[0]}")
    # Ver estructura de cada tabla
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"    {col[1]} ({col[2]})")

conn.close()
