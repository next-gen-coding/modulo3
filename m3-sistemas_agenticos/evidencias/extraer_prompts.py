"""Genera evidencias/prompts.md con las instrucciones de cada agente, tal como están en el código.

Uso, desde la raíz de la fábrica:  python evidencias/extraer_prompts.py
"""
import ast
from pathlib import Path

ARCHIVOS = {"Analista": "agentes/analista.py", "Diseñador de pruebas": "agentes/disenador_pruebas.py",
            "Desarrollador": "agentes/desarrollador.py", "Despliegue": "agentes/despliegue.py",
            "Automatizador": "agentes/automatizador.py", "Triage": "agentes/triage.py"}
NOMBRES = ("SISTEMA", "INSTRUCCIONES", "TAREA", "PROMPT", "ESCRITURA", "PROGRAMAS")

salida = ["# Prompts de los agentes", "", "Extraídos del código con `evidencias/extraer_prompts.py`.", ""]
for agente, ruta in ARCHIVOS.items():
    salida += [f"## {agente} · `{ruta}`", ""]
    for nodo in ast.parse(Path(ruta).read_text(encoding="utf-8")).body:
        if isinstance(nodo, ast.Assign) and getattr(nodo.targets[0], "id", "") in NOMBRES:
            salida += [f"**{nodo.targets[0].id}**", "", "```text", str(ast.literal_eval(nodo.value)), "```", ""]
filtro = Path("flujos/flujo_s4.py").read_text(encoding="utf-8")
inicio = filtro.index('"Eres un filtro de seguridad.')
salida += ["## Filtro de historia · `flujos/flujo_s4.py`", "", "```text", filtro[inicio:filtro.index(")", inicio)], "```", "",
           "## CLAUDE.md de la app (`contexto/convenciones_app.md` → `app/CLAUDE.md`)", "",
           "Se copia completo antes de cada llamada a Claude Code; ver el archivo."]
Path("evidencias/prompts.md").write_text("\n".join(salida), encoding="utf-8")
print("evidencias/prompts.md:", len(salida), "líneas")
