"""Sesión 1 · La base de los agentes 1 y 2: herramientas de archivos y el bucle.

Un agente = modelo + instrucciones + herramientas + bucle. Los agentes 1 y 2
usan este mismo bucle; solo cambian sus instrucciones y sus herramientas.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "salida"
APP = RAIZ / "app"


def rel(ruta: Path) -> str:
    """Ruta relativa a la raíz del repositorio, como la ven los agentes."""
    return str(ruta.resolve().relative_to(RAIZ))


def hu_de(historia: Path) -> str:
    """'historias/HU-01-registrar-empleado.md' -> 'HU-01'."""
    return "-".join(historia.stem.split("-")[:2])


# --- Herramientas ------------------------------------------------------
@dataclass
class Herramienta:
    nombre: str
    descripcion: str
    parametros: dict  # propiedades JSON Schema; todas obligatorias
    funcion: Callable[..., str]

    def esquema(self) -> dict:
        return {"name": self.nombre, "description": self.descripcion,
                "input_schema": {"type": "object", "properties": self.parametros,
                                 "required": list(self.parametros)}}


def _dentro_de(ruta: str, bases: list[Path]) -> Path:
    """Resuelve la ruta y rechaza cualquier cosa fuera de las carpetas permitidas."""
    destino = (RAIZ / ruta).resolve()
    if not any(destino.is_relative_to(b.resolve()) for b in bases):
        permitidas = ", ".join(rel(b) + "/" for b in bases)
        raise PermissionError(f"Ruta no permitida: {ruta}. Solo: {permitidas}")
    return destino


def herramientas_archivos(lectura: list[Path], escritura: Path) -> list[Herramienta]:
    """Herramientas de archivos con permisos mínimos: leer en `lectura`, escribir solo en `escritura`."""
    def leer_archivo(ruta: str) -> str:
        return _dentro_de(ruta, lectura + [escritura]).read_text(encoding="utf-8")

    def listar_archivos(carpeta: str) -> str:
        base = _dentro_de(carpeta, lectura + [escritura])
        return "\n".join(rel(p) for p in sorted(base.rglob("*")) if p.is_file()) or "(vacía)"

    def escribir_archivo(ruta: str, contenido: str) -> str:
        destino = _dentro_de(ruta, [escritura])
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(contenido, encoding="utf-8")
        return f"Escrito {ruta} ({len(contenido)} caracteres)"

    texto = {"type": "string"}
    return [
        Herramienta("leer_archivo", "Lee un archivo de texto. Ejemplo: ruta='historias/HU-01-registrar-empleado.md'.",
                    {"ruta": texto}, leer_archivo),
        Herramienta("listar_archivos", "Lista los archivos de una carpeta. Ejemplo: carpeta='contexto'.",
                    {"carpeta": texto}, listar_archivos),
        Herramienta("escribir_archivo", ("Crea o reemplaza un archivo con el contenido completo. "
                                         f"Solo se permite dentro de {rel(escritura)}/."),
                    {"ruta": texto, "contenido": texto}, escribir_archivo),
    ]


# --- El bucle del agente -------------------------------------------------
def ejecutar_agente(sistema: str, herramientas: list[Herramienta], tarea: str,
                    max_pasos: int = 10, nombre: str = "agente") -> str:
    #Llama al modelo, ejecuta las herramientas que pida y repite hasta que responda sin pedir más.
    # Lab 1A · Escribe aquí el bucle del agente. Tu referencia: ejemplos/s1_razonamiento/react.py
    #
    # 1. Crea el cliente de Anthropic y un registro {nombre: herramienta} a partir de `herramientas`.
    # 2. Empieza la conversación: una lista `mensajes` con la tarea como mensaje del usuario.
    # 3. En cada vuelta, hasta `max_pasos`, llama al modelo con el sistema, los esquemas de las
    #    herramientas (h.esquema()) y los mensajes. El modelo se lee de os.environ["MODEL"].
    # 4. Agrega la respuesta del modelo a `mensajes` (rol "assistant").
    # 5. Si `stop_reason` no es "tool_use", devuelve el texto de los bloques de tipo "text": terminó.
    # 6. Si pidió herramientas, ejecuta cada bloque "tool_use" con registro[nombre].funcion(**input).
    #    Si lanza una excepción, NO la silencies: devuélvela como texto con "is_error": True.
    # 7. Envía todos los "tool_result" (con su tool_use_id) en un solo mensaje de rol "user"
    #    y vuelve al paso 3.
    # 8. Si se acaban los pasos, lanza RuntimeError(f"{nombre}: se alcanzó el límite de {max_pasos} pasos").
    cliente = Anthropic()
    registro = {h.nombre: h for h in herramientas}
    mensajes = [{"role": "user", "content": tarea}]
    
    for paso in range(max_pasos):
        resp = cliente.messages.create(model=os.environ["MODEL"], max_tokens=16000, system=sistema,
                                       tools=[h.esquema() for h in herramientas], messages=mensajes)
        mensajes.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        resultados = []
        for bloque in resp.content:
            if bloque.type != "tool_use":
                continue
            print(f"  [{nombre} · paso {paso}] {bloque.name}({', '.join(bloque.input)})")
            try:
                salida, error = registro[bloque.name].funcion(**bloque.input), False
            except Exception as e:
                salida, error = f"Error: {e}", True
            resultados.append({"type": "tool_result", "tool_use_id": bloque.id,
                               "content": salida, "is_error": error})
        mensajes.append({"role": "user", "content": resultados})
    raise NotImplementedError("Lab 1A: escribe el bucle del agente en agentes/base.py")
