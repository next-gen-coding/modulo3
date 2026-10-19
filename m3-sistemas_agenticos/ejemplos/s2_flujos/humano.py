"""El humano en el flujo: el agente propone, el código clasifica el riesgo y una persona aprueba lo irreversible.

Lo que distingue al patrón en el código:
  - `interrupt(...)` pausa el grafo y le muestra a la persona EXACTAMENTE qué se va a hacer,
  - un checkpointer (`InMemorySaver`) guarda el estado mientras la persona decide,
  - `Command(resume=...)` reanuda el flujo con su respuesta, en el mismo `thread_id`.
Tres niveles de autonomía en un mismo flujo: lo de bajo riesgo se ejecuta solo, lo irreversible
espera aprobación, y lo que el código no puede clasificar se escala a una persona.

Uso:  python -m ejemplos.s2_flujos.humano
En tu fábrica:  flujos/flujo_s2.py → aprobar_plan y pedir_aclaracion
"""
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import BaseModel

from ejemplos.comun import EMPLEADOS, paso, titulo, modelo, guardar_grafo

"""
contrato con el modelo: describe una acción
   Accion convierte texto libre en acciones revisables, y "otra" le da al modelo una forma honesta de decir «no sé qué es esto». 
   El expediente separa las acciones en bandejas según su nivel de autonomía y guarda una bitácora de todo lo que pasó.
   La bitácora es parte del expediente
"""
class Accion(BaseModel):
    tipo: Literal["cambiar_puesto", "dar_de_baja", "otra"]
    numero_empleado: str
    detalle: str

#contrato con el modelo: la lista de acciones, que es lo que el modelo devuelve
class Acciones(BaseModel):
    acciones: list[Accion]

#El "expediente" 
class Estado(TypedDict, total=False):
    solicitud: str
    automaticas: list[dict]
    con_aprobacion: list[dict]
    bitacora: list[str]


def interpretar(s: Estado) -> Estado:
    """El agente propone acciones estructuradas; todavía no ejecuta nada."""
    a = modelo().with_structured_output(Acciones).invoke(
        f"Directorio: {EMPLEADOS}\n\nConvierte esta solicitud de RR. HH. en acciones:\n{s['solicitud']}")
    # El CÓDIGO clasifica el riesgo, no el modelo
    auto = [x.model_dump() for x in a.acciones if x.tipo == "cambiar_puesto"]
    riesgo = [x.model_dump() for x in a.acciones if x.tipo != "cambiar_puesto"]
    paso("agente propone", f"{len(auto)} automáticas · {len(riesgo)} requieren a una persona")
    return {"automaticas": auto, "con_aprobacion": riesgo, "bitacora": []}


def ejecutar_automaticas(s: Estado) -> Estado:
    log = [f"AUTO · {x['tipo']} {x['numero_empleado']}: {x['detalle']}" for x in s["automaticas"]]
    for linea in log:
        paso("ejecuta sin pedir permiso", linea)
    return {"bitacora": s["bitacora"] + log}


def aprobar(s: Estado) -> Estado:
    log = list(s["bitacora"])
    for x in s["con_aprobacion"]:
        #Recorre el directorio y devuelve el primer empleado cuyo número coincide. 
        # Si no encuentra ninguno, devuelve None (el segundo argumento de next).
        empleado = next((e for e in EMPLEADOS if e["numero"] == x["numero_empleado"]), None)
        """
        interrupt(paquete) pausa el grafo y le entrega a la persona exactamente qué se va a hacer y a quién. 
        Al reanudar, devuelve su respuesta. Pero el nodo se vuelve a ejecutar desde el principio, 
        así que nada irreversible puede ir antes de un interrupt.
        """
        decision = interrupt({                                   # ← pausa: la persona ve qué y a quién
            "accion": x["tipo"], "empleado": empleado or "NO ENCONTRADO", "detalle": x["detalle"],
            "pregunta": "¿Apruebas? (si / no)"})
        estado = "APROBADA" if str(decision).strip().lower() == "si" else "RECHAZADA"
        log.append(f"{estado} por una persona · {x['tipo']} {x['numero_empleado']}: {x['detalle']}")
    return {"bitacora": log}


def hay_riesgo(s: Estado) -> Literal["aprobar", "__end__"]:
    return "aprobar" if s["con_aprobacion"] else END


grafo = StateGraph(Estado)
grafo.add_node("interpretar", interpretar)
grafo.add_node("ejecutar_automaticas", ejecutar_automaticas)
grafo.add_node("aprobar", aprobar)
grafo.add_edge(START, "interpretar")
grafo.add_edge("interpretar", "ejecutar_automaticas")
grafo.add_conditional_edges("ejecutar_automaticas", hay_riesgo)
grafo.add_edge("aprobar", END)
app = grafo.compile(checkpointer=InMemorySaver())   # ← sin checkpointer no se puede pausar y reanudar

if __name__ == "__main__":
    #Dibujar el grafo
    import sys
    titulo("Human in the Loop (HITL) · el grafo")
    guardar_grafo(app, "HITL", abrir="--abrir" in sys.argv)
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()
        
    #Ejecutar HITL
    titulo("El humano en el flujo")
    config = {"configurable": {"thread_id": "solicitud-1"}}
    resultado = app.invoke({"solicitud": "Jorge Díaz (EMP-0004) pasa a ser Líder técnico. "
                                         "Además, da de baja a Luis Pérez (EMP-0002) a partir de hoy."}, config)
    while "__interrupt__" in resultado:                              # el flujo está en pausa
        pregunta = resultado["__interrupt__"][0].value
        print(f"\n⏸  {pregunta['accion']} · {pregunta['empleado']}\n   {pregunta['detalle']}")
        respuesta = input(f"   {pregunta['pregunta']} ")
        """
        Ejemplo, si contestaste Si: Command(resume="si") le dice a LangGraph: 
        «sigue donde te quedaste y entrégale esta respuesta al interrupt que estaba esperando». 
        Dentro del nodo, interrupt devuelve ese "si".
        """
        resultado = app.invoke(Command(resume=respuesta), config)    # ← se reanuda donde quedó
    print("\nBitácora:", *resultado["bitacora"], sep="\n  ")
