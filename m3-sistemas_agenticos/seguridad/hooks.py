"""Hooks PreToolUse para los agentes que trabajan con Claude Code (agentes 3, 4 y 5).

Dos familias:
- Hooks de ROL (sesiones 2 y 3): cada agente escribe solo los archivos de su rol.
- Hooks de SEGURIDAD (sesión 4): lectura confinada, secretos protegidos, comandos permitidos
  y auditoría. Se apagan con DEFENSAS=0 para ver los ataques funcionar en clase.
"""
import fnmatch
import json
import os
import re
import time
from pathlib import Path

from claude_agent_sdk import HookMatcher

RAIZ = Path(__file__).resolve().parent.parent
PALABRAS_SECRETAS = (".env", "secretos", "printenv", "environ")


def _denegar(input_data: dict, motivo: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": input_data["hook_event_name"],
                                   "permissionDecision": "deny",
                                   "permissionDecisionReason": motivo}}


def _resolver(base: Path, ruta: str) -> Path:
    return (base / ruta).resolve()  # si `ruta` es absoluta, Path ignora `base`


# --- Hooks de rol -------------------------------------------------------
def confinar_escritura(base: Path, patrones: list[str]):
    """Write/Edit solo dentro de `base` y en rutas que coincidan con algún patrón glob."""
    async def hook(input_data, tool_use_id, context):
        ruta = input_data["tool_input"].get("file_path") or input_data["tool_input"].get("notebook_path", "")
        destino = _resolver(base, ruta)
        if not destino.is_relative_to(base.resolve()):
            return _denegar(input_data, f"Solo puedes escribir dentro de {base.name}/: {ruta}")
        relativa = destino.relative_to(base.resolve()).as_posix()
        if not any(fnmatch.fnmatch(relativa, p) for p in patrones):
            return _denegar(input_data, f"Tu rol no puede escribir {relativa}. Permitido: {', '.join(patrones)}")
        return {}
    return hook


# --- Hooks de seguridad (sesión 4) -----------------------------------------
def confinar_lectura(base: Path):
    """Read/Grep/Glob solo dentro de `base` y nunca archivos con secretos."""
    async def hook(input_data, tool_use_id, context):
        entrada = input_data["tool_input"]
        ruta = entrada.get("file_path") or entrada.get("path") or "."
        destino = _resolver(base, ruta)
        if not destino.is_relative_to(base.resolve()):
            return _denegar(input_data, f"Lectura fuera de {base.name}/ bloqueada: {ruta}")
        if any(p in destino.name.lower() for p in (".env", "secretos")) and not destino.name.endswith(".example"):
            return _denegar(input_data, f"Archivo con secretos bloqueado: {destino.name}")
        return {}
    return hook


def comandos_permitidos(base: Path, programas: set[str]):
    """Bash solo con programas de la lista; sin sustituciones, sin salir de `base`, sin tocar secretos."""
    async def hook(input_data, tool_use_id, context):
        comando = input_data["tool_input"].get("command", "")
        if "`" in comando or "$(" in comando:
            return _denegar(input_data, "Sustitución de comandos no permitida")
        if any(p in comando.lower() for p in PALABRAS_SECRETAS):
            return _denegar(input_data, "El comando menciona secretos o variables de entorno")
        for tramo in re.split(r"&&|\|\||;|\|", comando):
            partes = tramo.strip().split()
            if not partes:
                continue
            if partes[0] not in programas:
                return _denegar(input_data, f"Programa no permitido: {partes[0]}. Permitidos: {sorted(programas)}")
            if partes[0] == "cd" and len(partes) > 1 and not _resolver(base, partes[1]).is_relative_to(base.resolve()):
                return _denegar(input_data, f"No puedes salir de {base.name}/")
        return {}
    return hook


def auditar(agente: str):
    """Registra cada llamada a herramienta en auditoria.jsonl (una línea JSON por llamada)."""
    async def hook(input_data, tool_use_id, context):
        registro = {"ts": round(time.time(), 1), "agente": agente, "herramienta": input_data["tool_name"],
                    "entrada": str(input_data["tool_input"])[:300]}
        with open(RAIZ / "auditoria.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
        return {}
    return hook


def hooks_para(agente: str, base: Path, escritura: list[str], programas: set[str]) -> dict:
    """Arma los hooks de un agente: siempre los de rol; los de seguridad si DEFENSAS != 0."""
    previos = [HookMatcher(matcher="Write|Edit|MultiEdit|NotebookEdit", hooks=[confinar_escritura(base, escritura)])]
    if os.environ.get("DEFENSAS", "1") != "0":
        previos += [HookMatcher(matcher="Read|Grep|Glob", hooks=[confinar_lectura(base)]),
                    HookMatcher(matcher="Bash", hooks=[comandos_permitidos(base, programas)]),
                    HookMatcher(hooks=[auditar(agente)])]
    return {"PreToolUse": previos}
