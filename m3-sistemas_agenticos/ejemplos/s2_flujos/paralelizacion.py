"""Patrón de flujo: Paralelización. Ramas independientes corren a la vez y se unen al final.

Lo que distingue al patrón en el código:
  1. dos `add_edge` que salen del MISMO nodo (abanico),
  2. `add_edge([rama_a, rama_b], "unir")`, que espera a ambas (unión),
  3. un reductor (`Annotated[list, operator.add]`) porque las dos ramas escriben el mismo campo.
Mide el tiempo: debería tardar casi lo mismo que la rama más lenta, no la suma de las dos.

Uso:  python -m ejemplos.s2_flujos.paralelizacion
En tu fábrica:  flujos/flujo_s3.py → despues_de_verificar() devuelve ["desplegar", "automatizar"]
"""
import operator
import time
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from ejemplos.comun import historia, modelo, paso, titulo, guardar_grafo


class Estado(TypedDict, total=False):
    historia: str
    casos: Annotated[list[str], operator.add]   # ← sin reductor, LangGraph rechazaría dos escrituras a la vez
    #Es decir, al ser un Annotated le dije a langhgraph que agregue las respuestas, esto evita sobreescritura
    resumen: str


def casos_api(s: Estado) -> Estado:
    inicio = time.perf_counter()
    texto = modelo().invoke("Escribe 3 casos de prueba de la API (método, ruta, código esperado) para:\n"
                            + s["historia"]).text
    paso(f"rama API · {time.perf_counter() - inicio:.1f} s", texto)
    return {"casos": [f"API:\n{texto}"]}


def casos_ui(s: Estado) -> Estado:
    inicio = time.perf_counter()
    texto = modelo().invoke("Escribe 3 casos de prueba de la pantalla (qué hace la persona, qué ve) para:\n"
                            + s["historia"]).text
    paso(f"rama UI · {time.perf_counter() - inicio:.1f} s", texto)
    return {"casos": [f"UI:\n{texto}"]}


def unir(s: Estado) -> Estado:
    paso("unir", f"llegaron {len(s['casos'])} bloques de casos")
    return {"resumen": "\n\n".join(s["casos"])}


grafo = StateGraph(Estado)
grafo.add_node("casos_api", casos_api)
grafo.add_node("casos_ui", casos_ui)
grafo.add_node("unir", unir)
grafo.add_edge(START, "casos_api")                  # ← abanico: dos aristas desde el mismo origen
grafo.add_edge(START, "casos_ui")
grafo.add_edge(["casos_api", "casos_ui"], "unir")   # ← unión: espera a las dos ramas
grafo.add_edge("unir", END)
app = grafo.compile()

if __name__ == "__main__":
    import sys

    titulo("Paralelizacion · el grafo")
    guardar_grafo(app, "paralelizacion", abrir="--abrir" in sys.argv)
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()

    titulo("Paralelización")
    inicio = time.perf_counter()
    app.invoke({"historia": historia("HU-01")})
    print(f"\nTiempo total: {time.perf_counter() - inicio:.1f} s")
