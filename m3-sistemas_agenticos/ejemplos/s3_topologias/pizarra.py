"""Topología: Pizarra (blackboard). Los agentes no se hablan: leen y escriben en un estado compartido.

Lo que distingue a la topología en el código:
  - cada agente declara QUÉ necesita leer y QUÉ campo escribe (REQUIERE / ESCRIBE),
  - un controlador en código mira la pizarra y activa al primer agente que ya puede trabajar,
  - nadie llama a nadie: agregar un agente nuevo es agregar una línea a la tabla.

Uso:  python -m ejemplos.s3_topologias.pizarra
En tu fábrica:  el estado de LangGraph es tu pizarra, y la carpeta salida/HU-xx/ es una pizarra en disco.
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from ejemplos.comun import historia, modelo, paso, titulo, guardar_grafo


class Pizarra(TypedDict, total=False):
    historia: str
    criterios: str
    casos: str
    endpoint: str
    pantalla: str


# agente: (lo que necesita leer, el campo que escribe, su tarea) — el orden NO importa
# Cada agente es una fila con tres cosas: qué lee de la pizarra, qué casilla escribe y su tarea.
AGENTES = {
    "pantalla": (["criterios", "endpoint"], "pantalla", "Describe el formulario React en 6 líneas."),
    "disenador": (["criterios"], "casos", "Escribe un caso de prueba por criterio."),
    "analista": (["historia"], "criterios", "Escribe 3 criterios Gherkin breves."),
    "backend": (["criterios"], "endpoint", "Propón el endpoint FastAPI en 6 líneas."),
}


"""
Es el corazón del patrón. Recorre la tabla y se queda con los agentes que cumplen dos condiciones:
all(p.get(c) for c in lee): todo lo que necesita leer ya está en la pizarra.
not p.get(escribe): su casilla sigue vacía, es decir, todavía no ha trabajado.
Si existe un empate, el primero en la lista se ejecuta primero
"""
def listo_para(p: Pizarra) -> list[str]:
    """Agentes cuyos insumos ya están en la pizarra y cuyo campo sigue vacío."""
    return [a for a, (lee, escribe, _) in AGENTES.items() if all(p.get(c) for c in lee) and not p.get(escribe)]

"""
El controlados imprime la pizarra y dice quien puede trabajar. No decide nada. 
Solo imprime qué casillas están llenas y quién puede trabajar, y devuelve {}, 
es decir, no cambia la pizarra. Pizarra.__annotations__ es la lista de campos de la clase.
Existe para ser el punto central del grafo al que todos regresan, y para que en la traza se vea el estado del tablero después de cada paso.
"""
def controlador(p: Pizarra) -> Pizarra:
    paso("pizarra", f"tiene {[c for c in Pizarra.__annotations__ if p.get(c)]} · pueden trabajar: {listo_para(p)}")
    return {}


def elegir(p: Pizarra) -> str:
    candidatos = listo_para(p)
    return candidatos[0] if candidatos else END        # ← el controlador decide mirando la pizarra

#Ejecuta su tarea y escribe lo que hizo en la pizarra
def agente(nombre: str):
    lee, escribe, tarea = AGENTES[nombre]

    def nodo(p: Pizarra) -> Pizarra:
        insumos = "\n\n".join(f"## {c}\n{p[c]}" for c in lee)
        texto = modelo(600).invoke(f"{tarea}\n\n{insumos}").text
        paso(f"{nombre} escribe '{escribe}'", texto, 140)
        return {escribe: texto}                         # ← solo escribe SU campo
    return nodo


grafo = StateGraph(Pizarra)
grafo.add_node("controlador", controlador)
for nombre in AGENTES:
    grafo.add_node(nombre, agente(nombre))
    grafo.add_edge(nombre, "controlador")               # todos regresan a la pizarra
grafo.add_edge(START, "controlador")
#Esta línea le dice a LangGraph: «cuando termine el nodo controlador, llama tú a elegir y ve al nodo cuyo nombre te devuelva».
grafo.add_conditional_edges("controlador", elegir, [*AGENTES, END])
app = grafo.compile()

if __name__ == "__main__":
    import sys
    #Guarda el grafo 
    titulo("Pizarra · el grafo")
    guardar_grafo(app, "pizarra", abrir="--abrir" in sys.argv)
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()

    titulo("Pizarra")
    app.invoke({"historia": historia("HU-01")})
