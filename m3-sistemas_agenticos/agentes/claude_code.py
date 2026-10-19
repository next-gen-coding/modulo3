"""Sesión 2 · Claude Code como agente programable (Claude Agent SDK).

Los agentes 3, 4 y 5 no usan el bucle de agentes/base.py: delegan en Claude Code,
que ya trae herramientas para leer, editar archivos y usar la terminal. Nosotros
decidimos su carpeta de trabajo, sus herramientas, sus permisos y su presupuesto.
"""
import asyncio
import os
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from seguridad.hooks import hooks_para

SOLO_LECTURA = ["Read", "Glob", "Grep"]
EDICION = ["Read", "Glob", "Grep", "Write", "Edit", "Bash"]


async def _consultar(prompt: str, opciones: ClaudeAgentOptions) -> ResultMessage:
    resultado = None
    async for mensaje in query(prompt=prompt, options=opciones):
        if isinstance(mensaje, ResultMessage):
            resultado = mensaje
    if resultado is None:
        raise RuntimeError("Claude Code terminó sin resultado")
    return resultado


def ejecutar_claude_code(prompt: str, *, agente: str, cwd: Path, herramientas: list[str],
                         escritura: list[str], programas: set[str], instrucciones: str) -> tuple[str, float]:
    """Ejecuta Claude Code sin interacción y devuelve (respuesta final, costo en USD)."""
    opciones = ClaudeAgentOptions(
        cwd=str(cwd),
        model=os.environ["MODEL"],
        system_prompt={"type": "preset", "preset": "claude_code", "append": instrucciones},
        setting_sources=["project"],              # carga el CLAUDE.md de cwd
        permission_mode="acceptEdits",            # edita sin pedir confirmación; los hooks ponen los límites
        allowed_tools=herramientas,
        disallowed_tools=["WebFetch", "WebSearch"],  # sin salida a internet: rompe la tríada letal
        hooks=hooks_para(agente, cwd, escritura, programas),
        max_turns=80,
        max_budget_usd=float(os.environ.get("PRESUPUESTO_USD", "2")),
    )
    print(f"  [{agente}] trabajando en {cwd.name}/ con Claude Code...")
    resultado = asyncio.run(_consultar(prompt, opciones))
    costo = resultado.total_cost_usd or 0.0
    print(f"  [{agente}] terminó en {resultado.num_turns} turnos · {costo:.2f} USD")
    if resultado.is_error:
        raise RuntimeError(f"{agente}: {resultado.subtype} · {resultado.result}")
    return resultado.result or "", costo
