"""Patrón de flujo: Encadenamiento. Pasos fijos; la salida de uno es la entrada del siguiente.

Lo que distingue al patrón en el código: solo `add_edge` en línea recta, más una compuerta
(arista condicional) que impide avanzar si la validación falla. El orden lo decide el código, nunca el modelo.

Uso:  python -m ejemplos.s2_flujos.encadenamiento
En tu fábrica:  flujos/flujo_s2.py → analizar → disenar_casos → planificar → construir
"""
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from ejemplos.comun import guardar_grafo, historia, modelo, paso, titulo


class Estado(TypedDict, total=False):
    historia: str
    criterios: str
    error: str
    casos: str


def escribir_criterios(s: Estado) -> Estado:
    texto = modelo().invoke("Escribe 3 escenarios Gherkin (# language: es), breves, para:\n" + s["historia"]).text
    paso("1 · criterios", texto)
    return {"criterios": texto}


def compuerta(s: Estado) -> Literal["escribir_casos", "__end__"]:
    """Validación determinista entre pasos: si falla, el flujo no avanza."""
    faltan = [p for p in ("Escenario", "Dado", "Cuando", "Entonces") if p not in s["criterios"]]
    if faltan:
        paso("compuerta", f"✗ faltan {faltan}: se detiene")
        return END
    paso("compuerta", "✓ criterios válidos")
    return "escribir_casos"


def escribir_casos(s: Estado) -> Estado:
    texto = modelo().invoke("Convierte cada escenario en un caso de prueba (id, pasos, resultado esperado):\n"
                            + s["criterios"]).text
    paso("2 · casos", texto)
    return {"casos": texto}


grafo = StateGraph(Estado)
grafo.add_node("escribir_criterios", escribir_criterios)
grafo.add_node("escribir_casos", escribir_casos)
grafo.add_edge(START, "escribir_criterios")                       # ← una línea recta…
grafo.add_conditional_edges("escribir_criterios", compuerta)     # ← …con una compuerta en medio
grafo.add_edge("escribir_casos", END)
app = grafo.compile()


if __name__ == "__main__":
    import sys

    titulo("Encadenamiento · el grafo")
    guardar_grafo(app, "encadenamiento", abrir="--abrir" in sys.argv)
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()
    titulo("Encadenamiento")
    #Ejecuta el grafo con la historia de usuario HU-01
    app.invoke({"historia": historia("HU-01")})