"""Patrón de flujo: Evaluador-optimizador. Un generador produce y un juez independiente decide.

Lo que distingue al patrón en el código: un CICLO en el grafo (evaluar → generar) con un tope,
y un evaluador que no es el mismo agente. Aquí el juez es pytest: pruebas escritas a partir de las
reglas de negocio. El código generado nunca se ejecuta con exec(): solo pytest, en un subproceso con tiempo límite.

Uso:  python -m ejemplos.s2_flujos.evaluador
En tu fábrica:  flujos/flujo_s2.py → construir → verificar → construir (con el log del error)
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from ejemplos.comun import modelo, paso, titulo, guardar_grafo

MAX_INTENTOS = 3

# Pruebas es un texto que contiene un archivo de pytest completo.
# Las pruebas son la especificación: salen de contexto/reglas_negocio.md, no del generador
PRUEBAS = '''
import pytest
from correo import validar_correo

def test_acepta_y_normaliza():
    assert validar_correo("  Ana.Lopez@Empresa.com ") == "ana.lopez@empresa.com"

def test_rechaza_otro_dominio():
    with pytest.raises(ValueError, match="Usa el correo corporativo @empresa.com"):
        validar_correo("ana@gmail.com")

def test_rechaza_dominio_parecido():
    with pytest.raises(ValueError):
        validar_correo("ana@empresa.com.mx")
'''

#Memoria del ciclo
#codigo	la versión más reciente del código
#error	la salida de pytest si falló (vacío si pasó); es la crítica que regresa al generador
#intentos el contador del tope
#aprobado el veredicto del juez
# No requiere que todos los campos est+en presentes
class Estado(TypedDict, total=False):
    codigo: str
    error: str
    intentos: int
    aprobado: bool


def generar(s: Estado) -> Estado:
    #Le digo que escribir y en que formato
    prompt = ("Escribe en Python la función validar_correo(correo: str) -> str para el correo corporativo "
              "de un empleado. Responde solo con un bloque ```python```.")
    #Verificación, si ya había fallado anteriormente, le agrego la retro del juez al prompt para que lo corrija.
    if s.get("error"):                                         # la crítica del juez vuelve como contexto
        #Reescribe todo el código no toma en cuenta el anteior
        prompt += f"\n\nTu versión anterior falló estas pruebas; corrígela:\n{s['error'][-2500:]}"
        #Esta versión, toma en cuenta la anteror
        #prompt += f"\n\nTu versión anterior:\n```python\n{s['codigo']}\n```\n\nFalló estas pruebas; corrígela:\n{s['error'][-2500:]}"
    #Obtiene el código nuevo
    texto = modelo().invoke(prompt).text
    #La expresión regular busca lo que está entre ```python y el cierre ```:
    codigo = re.search(r"```python\n(.*?)```", texto, re.S) # (.*?) Captura todo lo que haya, lo mínimo posible, hasta…, re.S permita que incluya saltos de linea
    #Dame el número de intentos, si no hay, es el primero
    intentos = s.get("intentos", 0) + 1
    paso(f"generador · intento {intentos}/{MAX_INTENTOS}", "escribió una nueva versión")
    return {"codigo": codigo.group(1) if codigo else texto, "intentos": intentos}


def evaluar(s: Estado) -> Estado:
    with tempfile.TemporaryDirectory() as carpeta:
        #Escribe el código y sus pruebas de forma deterministica
        Path(carpeta, "correo.py").write_text(s["codigo"], encoding="utf-8")
        Path(carpeta, "test_correo.py").write_text(PRUEBAS, encoding="utf-8")
        #Executa pytext como un subproceso
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", carpeta],
                           #captura salida de pytest en stdout, esstablece un timeout limite de 60seg.
                           capture_output=True, text=True, timeout=60)
    resumen = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
    paso("evaluador · pytest", ("✓ " if r.returncode == 0 else "✗ ") + resumen)
    return {"aprobado": r.returncode == 0, "error": "" if r.returncode == 0 else r.stdout}


def decidir(s: Estado) -> Literal["generar", "__end__"]:
    if s["aprobado"] or s["intentos"] >= MAX_INTENTOS:          # ← el tope es parte del patrón
        return END
    return "generar"


grafo = StateGraph(Estado)
grafo.add_node("generar", generar)
grafo.add_node("evaluar", evaluar)
grafo.add_edge(START, "generar")
grafo.add_edge("generar", "evaluar")
grafo.add_conditional_edges("evaluar", decidir)   # ← el ciclo: si falla, regresa a generar
app = grafo.compile()

if __name__ == "__main__":
    import sys
    titulo("Evaluador-optimizador · el grafo")
    guardar_grafo(app, "evaluador", abrir="--abrir" in sys.argv)
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()
    titulo("Evaluador-optimizador")
    final = app.invoke({})
    print("\nAprobado" if final["aprobado"] else "\nSin aprobar: lo decide una persona")
    print(final["codigo"])
