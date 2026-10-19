"""Sesión 1 · Agente 2, diseñador de pruebas: criterios de aceptación -> casos de prueba.

Uso:  python -m agentes.disenador_pruebas salida/HU-01/criterios.feature
"""
import json
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ValidationError

from agentes.analista import escenarios
from agentes.base import RAIZ, Herramienta, ejecutar_agente, herramientas_archivos, rel


class CasoPrueba(BaseModel):
    id: str                          # CP-01, CP-02...
    escenario: str                   # nombre exacto del escenario Gherkin que cubre
    nivel: Literal["api", "e2e"]     # api: se prueba con HTTP; e2e: se prueba en el navegador
    precondiciones: list[str]
    pasos: list[str]
    datos: dict[str, str]
    resultado_esperado: str


class PlanPruebas(BaseModel):
    historia: str
    casos: list[CasoPrueba]


SISTEMA = """Eres diseñador de pruebas de software. A partir de criterios de aceptación en Gherkin
escribes casos de prueba que luego otra persona automatizará.

Cómo trabajas:
1. Lee {criterios} y contexto/convenciones_app.md (ahí están la API y los data-testid de la pantalla).
2. Para cada escenario escribe al menos un caso de nivel "api". Si el escenario involucra la pantalla,
   escribe además uno de nivel "e2e" cuyos pasos mencionen los data-testid que se usan.
3. Usa datos concretos. Para correos usa el dominio corporativo empresa.com.
4. Guarda los casos llamando a la herramienta guardar_casos (no escribas el JSON a mano).
   - "nivel" solo puede ser "api" o "e2e".
   - En "datos" TODOS los valores son texto: "201", no 201; para un campo vacío usa "", nunca null.
   - En "escenario" copia el nombre del escenario EXACTAMENTE como aparece después de "Escenario:".
   - Si guardar_casos devuelve un error, corrige lo que indica y vuelve a llamarla.
5. Responde al final con una sola línea: cuántos casos escribiste."""


def validar_plan(texto: str, gherkin: str) -> list[str]:
    """Evaluador determinista: JSON válido y cada escenario cubierto por al menos un caso."""
    try:
        plan = PlanPruebas.model_validate_json(texto)
    except ValidationError as e:
        return [f"El JSON no cumple el esquema: {e.errors()[:3]}"]
    cubiertos = {c.escenario.strip() for c in plan.casos}
    problemas = [f"Escenario sin casos: {e}" for e in escenarios(gherkin) if e not in cubiertos]
    ids = [c.id for c in plan.casos]
    if len(ids) != len(set(ids)):
        problemas.append("Hay ids de caso repetidos.")
    return problemas


def herramienta_guardar_casos(destino: Path) -> Herramienta:
    """El contrato viaja en el esquema de la herramienta: el modelo llena campos, no escribe JSON a mano."""
    def guardar_casos(historia: str, casos: list) -> str:
        try:
            plan = PlanPruebas.model_validate({"historia": historia, "casos": casos})
        except ValidationError as e:  # el error regresa al modelo como texto, corto y accionable
            raise ValueError("Los casos no cumplen el esquema: " + "; ".join(
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()[:5]))
        destino.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
        return f"Guardados {len(plan.casos)} casos en {rel(destino)}"
    return Herramienta(
        "guardar_casos",
        "Guarda el plan de pruebas en casos_prueba.json y lo valida; si hay errores, los devuelve para que "
        "corrijas. Ejemplo: historia='HU-01', casos=[{'id': 'CP-01', 'escenario': 'Alta exitosa', 'nivel': 'api', "
        "'precondiciones': [], 'pasos': ['...'], 'datos': {'correo': 'ana@empresa.com'}, 'resultado_esperado': '...'}].",
        {"historia": {"type": "string"},
         "casos": {"type": "array", "items": CasoPrueba.model_json_schema()}},
        guardar_casos)


def disenar_casos(criterios: Path, max_intentos: int = 2) -> Path:
    carpeta = criterios.parent
    destino = carpeta / "casos_prueba.json"
    lectura = [h for h in herramientas_archivos(lectura=[RAIZ / "contexto", carpeta], escritura=carpeta)
               if h.nombre != "escribir_archivo"]          # solo se escribe a través de guardar_casos
    herramientas = lectura + [herramienta_guardar_casos(destino)]
    sistema = SISTEMA.format(criterios=rel(criterios))
    gherkin = criterios.read_text(encoding="utf-8")
    tarea = f"Diseña los casos de prueba para {rel(criterios)}."
    for intento in range(1, max_intentos + 1):
        print(f"Diseñador de pruebas · intento {intento}")
        ejecutar_agente(sistema, herramientas, tarea, nombre="disenador")
        problemas = validar_plan(destino.read_text(encoding="utf-8"), gherkin) if destino.exists() \
            else [f"No se escribió {rel(destino)}."]
        if not problemas:
            return destino
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Casos inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = disenar_casos(Path(sys.argv[1]).resolve())
    plan = PlanPruebas.model_validate_json(ruta.read_text(encoding="utf-8"))
    print(f"\nListo: {rel(ruta)} · {len(plan.casos)} casos "
          f"({sum(c.nivel == 'api' for c in plan.casos)} api, {sum(c.nivel == 'e2e' for c in plan.casos)} e2e)")