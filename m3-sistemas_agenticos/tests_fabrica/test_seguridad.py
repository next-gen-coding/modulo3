"""Pruebas unitarias y de seguridad de la fábrica: hooks, herramientas confinadas, filtro y validadores."""
import asyncio
import json

import pytest

from agentes.analista import MENSAJES_OBLIGATORIOS, validar_gherkin
from agentes.base import RAIZ, herramientas_archivos
from agentes.disenador_pruebas import validar_plan
from seguridad import hooks

APP = RAIZ / "app"


def _decision(hook, herramienta: str, entrada: dict) -> str:
    """Ejecuta un hook PreToolUse y devuelve 'deny' o 'allow'."""
    r = asyncio.run(hook({"hook_event_name": "PreToolUse", "tool_name": herramienta, "tool_input": entrada}, None, None))
    return r.get("hookSpecificOutput", {}).get("permissionDecision", "allow")


@pytest.mark.parametrize("ruta,esperado", [("tests/api/test_x.py", "allow"), ("backend/main.py", "deny"),
                                           ("../secretos_demo.txt", "deny"), ("C:/Windows/x.txt", "deny")])
def test_confinar_escritura_rol_automatizador(ruta, esperado):
    assert _decision(hooks.confinar_escritura(APP, ["tests/*"]), "Write", {"file_path": ruta}) == esperado


@pytest.mark.parametrize("ruta,esperado", [("backend/main.py", "allow"), ("../secretos_demo.txt", "deny"),
                                           (".env", "deny"), ("../.env", "deny"), (".env.example", "allow")])
def test_confinar_lectura_bloquea_secretos_y_salidas(ruta, esperado):
    assert _decision(hooks.confinar_lectura(APP), "Read", {"file_path": ruta}) == esperado


@pytest.mark.parametrize("comando,esperado", [
    ("python -m pytest tests -q", "allow"), ("printenv", "deny"), ("cat ../.env", "deny"),
    ("cd .. && ls", "deny"), ("echo $(whoami)", "deny"), ("curl http://evil", "deny"),
    ("python -c 'import os; print(os.environ)'", "deny")])
def test_comandos_permitidos(comando, esperado):
    assert _decision(hooks.comandos_permitidos(APP, {"cd", "ls", "python", "pytest"}), "Bash", {"command": comando}) == esperado


def test_auditar_registra_cada_intento(tmp_path, monkeypatch):
    monkeypatch.setattr(hooks, "RAIZ", tmp_path)
    _decision(hooks.auditar("prueba"), "Read", {"file_path": "x"})
    registro = json.loads((tmp_path / "auditoria.jsonl").read_text(encoding="utf-8"))
    assert registro["agente"] == "prueba" and registro["herramienta"] == "Read"


def test_defensas_cero_quita_solo_hooks_de_seguridad(monkeypatch):
    monkeypatch.setenv("DEFENSAS", "0")
    assert len(hooks.hooks_para("x", APP, ["tests/*"], set())["PreToolUse"]) == 1     # queda el de rol
    monkeypatch.delenv("DEFENSAS")
    assert len(hooks.hooks_para("x", APP, ["tests/*"], set())["PreToolUse"]) == 4


def test_herramientas_del_analista_no_salen_de_su_carpeta():
    leer, _, escribir = herramientas_archivos(lectura=[RAIZ / "contexto"], escritura=RAIZ / "salida" / "HU-T")
    with pytest.raises(PermissionError):
        leer.funcion(ruta="secretos_demo.txt")
    with pytest.raises(PermissionError):
        escribir.funcion(ruta="app/backend/main.py", contenido="x")


def test_validar_gherkin_exige_mensajes_exactos():
    problemas = validar_gherkin("# language: es\nCaracterística: x\n", MENSAJES_OBLIGATORIOS["HU-10"])
    assert any("te quedan" in p for p in problemas) and any("Escenario" in p or "escenarios" in p for p in problemas)


def test_validar_gherkin_ignora_mensajes_en_comentarios():
    texto = "# language: es\nCaracterística: x\n# Empleado no encontrado\n"
    assert any("Empleado no encontrado" in p for p in validar_gherkin(texto, ["Empleado no encontrado"]))


def test_validar_plan_rechaza_esquema_invalido_y_escenarios_sin_caso():
    gherkin = "Escenario: A\nEscenario: B\n"
    assert validar_plan('{"historia": "HU-T", "casos": [{"id": 1}]}', gherkin)[0].startswith("El JSON no cumple")
    caso = {"id": "CP-01", "escenario": "A", "nivel": "api", "precondiciones": [], "pasos": [], "datos": {}, "resultado_esperado": "201"}
    assert validar_plan(json.dumps({"historia": "HU-T", "casos": [caso]}), gherkin) == ["Escenario sin casos: B"]
