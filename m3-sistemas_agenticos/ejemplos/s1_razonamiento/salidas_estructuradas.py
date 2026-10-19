"""Salidas estructuradas y validación con código: el modelo propone, el código decide.

Tres piezas que se repiten en toda la fábrica:
  1. Un CONTRATO: un modelo Pydantic con tipos, campos obligatorios y valores permitidos (Literal).
  2. Obtenerlo del modelo forzando una herramienta cuyo esquema ES el contrato (tool_choice).
  3. Validar en dos niveles con código: el esquema (Pydantic) y las reglas de negocio (una función).
     Si falla, el error regresa al modelo; si después de N intentos sigue fallando, decide una persona.

Uso:  python -m ejemplos.s1_razonamiento.salidas_estructuradas
En tu fábrica:  agentes/disenador_pruebas.py → PlanPruebas y validar_plan(); agentes/triage.py → Diagnostico
"""
import os
from datetime import date
from typing import Literal

from anthropic import Anthropic
from pydantic import BaseModel, ValidationError

from ejemplos.comun import paso, titulo

MAX_INTENTOS = 2


class AltaEmpleado(BaseModel):     # 1 · EL CONTRATO                  
    nombre: str
    correo: str
    puesto: str
    #Literal significa «solo uno de estos valores exactos». Si el modelo pone "TI", se rechaza.
    departamento: Literal["Tecnología", "Ventas", "Finanzas", "Recursos Humanos", "Operaciones"]
    fecha_ingreso: date
    #lo que el modelo no pudo saber con certeza
    #le da al modelo un lugar legítimo para decir «no lo sé». 
    # Sin él, un modelo que no sabe algo tiende a inventarlo para llenar el campo. 
    # Con él, la honestidad tiene dónde ir.
    dudas: list[str]                                 


def reglas_de_negocio(a: AltaEmpleado) -> list[str]:  # 3b · REGLAS que el esquema no expresa
    problemas = []
    if not a.correo.lower().endswith("@empresa.com"):
        problemas.append("Usa el correo corporativo @empresa.com")
    if a.fecha_ingreso > date.today():
        problemas.append("La fecha de ingreso no puede ser futura")
    if a.dudas:
        problemas.append(f"El modelo tiene dudas: {a.dudas}")
    return problemas


def extraer(correo_rh: str) -> AltaEmpleado | list[str]:
    cliente = Anthropic()
    herramienta = {"name": "registrar_alta", "description": "Registra los datos del empleado a dar de alta.",
                   "input_schema": AltaEmpleado.model_json_schema()}
    #El prompt tiene tres detalles importantes: 1) le dice al modelo que no invente datos, 
    # 2)le dice que tiene que tomar la fecha de hoy para registrar al empleado
    # y 2) le da un lugar legítimo para decir «no lo sé».
    tarea = (f"Hoy es {date.today()}. Extrae los datos del alta. No inventes: si un dato falta o es "
             f"ambiguo, anótalo en 'dudas'.\n\nCorreo de Recursos Humanos:\n{correo_rh}")
    problemas: list[str] = []
    for intento in range(1, MAX_INTENTOS + 1):
        #una herramienta que nunca se ejecuta. 
        # Su único propósito es su input_schema, que es el contrato traducido a JSON Schema. 
        # Es decir el schema de Pydantic AltaEmpleado. 
        # El modelo sabe que debe devolver {"nombre": "...", "correo": "...", ...}.
        #Al darle un tool_choice, el modelo no puede responder con texto libre: debe respetar el esquema.
        resp = cliente.messages.create(model=os.environ["MODEL"], max_tokens=800, tools=[herramienta],
                                       tool_choice={"type": "tool", "name": "registrar_alta"},   # 2 · FORZAR
                                       messages=[{"role": "user", "content": tarea}])
        datos = next(b.input for b in resp.content if b.type == "tool_use")
        try:
            #Obtento el schema validado (Pydantic) y luego lo paso por las reglas de negocio.
            #Ojo: Siempre son primero el esquema, luego las reglas de negocio. 
            alta = AltaEmpleado.model_validate(datos)                                         # 3a · ESQUEMA
            problemas = reglas_de_negocio(alta)                                               # 3b · REGLAS
        except ValidationError as e:
            #Si el esquema falla, e.g. está malformado, se da un error de ejecución. 
            #o NO se cumplio el contrato, ej. el departamento no es uno de los permitidos.
            # e.errors() es una lista de diccionarios, uno por campo que falló.
            # err['loc'] es la ubicación del error, por ejemplo ('departamento',).
            # '.'.join(map(str, ...)) la convierte en texto: "departamento". Para campos anidados quedaría algo como "direccion.ciudad".
            #err['msg'] es la explicación.
            problemas = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]
        #Si no hay problemas, se devuelve el objeto AltaEmpleado ya validado. Quien decide que terminó es el if, no el modelo.    
        paso(f"intento {intento}", "válido" if not problemas else f"problemas: {problemas}")
        if not problemas:
            return alta
        tarea += "\n\nTu respuesta anterior tiene estos problemas; corrígelos SOLO si el correo lo permite:\n- " \
                 + "\n- ".join(problemas)
    return problemas          # no se pudo: esto lo decide una persona, no el modelo


if __name__ == "__main__":
    correos = [
        "Hola, por favor da de alta a Ana López (ana.lopez@empresa.com), Analista de datos en el área "
        "de Tecnología. Entró el 06 de octubre de 2026.",
        "Porfa registra a Luis, su correo es luis.perez@gmail.com, va a ventas o finanzas, aún no sé, "
        "y empieza la próxima semana.",
    ]
    for texto in correos:
        titulo("Salidas estructuradas")
        print(texto)
        resultado = extraer(texto)
        if isinstance(resultado, AltaEmpleado):
            print("\n✓ Alta lista para la API:", resultado.model_dump_json(indent=2))
        else:
            print("\n✗ No se registra. Se envía a una persona de RH con estos problemas:", *resultado, sep="\n  - ")
