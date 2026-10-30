"""Sesión 3 · Cinco agentes orquestados: al flujo de la sesión 2 se suman despliegue y automatización,
que trabajan en paralelo.

Uso:  python -m flujos.flujo_s3 historias/HU-01-registrar-empleado.md
"""
import sys
from typing import Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from agentes.automatizador import automatizar as agente_automatizador
from agentes.despliegue import desplegar as agente_despliegue
from agentes.disenador_pruebas import PlanPruebas
from flujos import flujo_s2 as s2
from flujos.verificacion import verificar_despliegue, verificar_pruebas_escritas
from pathlib import Path
from flujos.util import dibuja_grafo


class Estado(s2.Estado, total=False):
    despliegue_ok: bool
    log_despliegue: str
    pruebas_ok: bool
    log_pruebas: str


def desplegar(s: Estado) -> Estado:
    errores = ""
    for intento in (1, 2):                                             # Agente 4 + verificación determinista
        _, costo = agente_despliegue(errores)
        ok, log = verificar_despliegue()
        if ok:
            break
        errores = log
    return {"despliegue_ok": ok, "log_despliegue": log, "costo_usd": costo,
            "bitacora": [f"Despliegue: {'OK' if ok else 'FALLA'}"]}


def automatizar(s: Estado) -> Estado:
    ids = [c.id for c in PlanPruebas.model_validate_json(Path(s["casos"]).read_text(encoding="utf-8")).casos]
    errores = ""
    for intento in (1, 2):                                             # Agente 5 + verificación determinista
        _, costo = agente_automatizador(s["hu"], errores)
        ok, log = verificar_pruebas_escritas(s["hu"], ids)
        if ok:
            break
        errores = log
    return {"pruebas_ok": ok, "log_pruebas": log, "costo_usd": costo,
            "bitacora": [f"Pruebas automatizadas: {'OK' if ok else 'FALLA'} ({len(ids)} casos)"]}


def despues_de_verificar(s: Estado) -> list[str] | Literal["construir", "fin"]:
    if s["app_ok"]:
        return ["desplegar", "automatizar"]                            # dos ramas en paralelo
    return "construir" if s["intentos"] < s2.MAX_INTENTOS else "fin"


def listo(s: Estado) -> Estado:
    return {"bitacora": ["Despliegue y pruebas listos"]}               # punto de unión de las ramas


def construir_grafo():
    g = StateGraph(Estado)
    for nombre, fn in [("analizar", s2.analizar), ("pedir_aclaracion", s2.pedir_aclaracion),
                       ("disenar_casos", s2.disenar), ("planificar", s2.planificar),
                       ("aprobar_plan", s2.aprobar_plan), ("construir", s2.construir),
                       ("verificar", s2.verificar), ("desplegar", desplegar), ("automatizar", automatizar),
                       ("listo", listo), ("fin", s2.fin)]:
        g.add_node(nombre, fn)
    g.add_edge(START, "analizar")
    g.add_conditional_edges("analizar", s2.despues_de_analizar)
    g.add_conditional_edges("pedir_aclaracion", s2.despues_de_aclarar)
    g.add_edge("disenar_casos", "planificar")
    g.add_edge("planificar", "aprobar_plan")
    g.add_conditional_edges("aprobar_plan", s2.despues_de_aprobar)
    g.add_edge("construir", "verificar")
    g.add_conditional_edges("verificar", despues_de_verificar, ["desplegar", "automatizar", "construir", "fin"])
    g.add_edge(["desplegar", "automatizar"], "listo")                  # espera a que terminen ambas ramas
    g.add_edge("listo", "fin")
    g.add_edge("fin", END)
    app = g.compile(checkpointer=InMemorySaver())
    #YA DIBUJA EL GRAFO ! 
    dibuja_grafo(app,"flujo_s3")
    return app

if __name__ == "__main__":
    s2.ejecutar(construir_grafo(), sys.argv[1])
