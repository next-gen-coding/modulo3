#!/usr/bin/env bash
# Corre un comando de la fábrica con un entorno limpio: quita las variables CLAUDE*/ANTHROPIC*
# que hereda la sesión de Claude Code (vacías) para que se usen las de m3-sistemas_agenticos/.env.
for v in $(env | grep -E '^(CLAUDE|ANTHROPIC)' | cut -d= -f1); do unset "$v"; done
cd "D:/agentic-course/modulo3/m3-sistemas_agenticos" || exit 1
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
exec .venv/Scripts/python.exe "$@"
