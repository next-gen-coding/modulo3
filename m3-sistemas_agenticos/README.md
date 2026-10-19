# Fábrica de software con agentes · Módulo 3

Una cadena de seis agentes que convierte una historia de usuario en una aplicación de gestión de empleados desplegada y probada:

| # | Agente | Entrada | Salida | Sesión |
| --- | --- | --- | --- | --- |
| 1 | Analista | Historia de usuario | `salida/HU-xx/criterios.feature` | 1 |
| 2 | Diseñador de pruebas | Criterios | `salida/HU-xx/casos_prueba.json` | 1 |
| 3 | Desarrollador (Claude Code) | Criterios y casos | `app/backend`, `app/frontend` | 2 |
| 4 | Despliegue (Claude Code) | Código | Contenedores con Docker Compose | 3 |
| 5 | Automatizador (Claude Code) | Casos de prueba | `app/tests` (pytest + Playwright) | 3 |
| 6 | Flujo E2E con triage | Pruebas y app desplegada | `salida/HU-xx/reporte.md` | 4 |

## Requisitos

Python 3.12, Node 20 o superior, Docker Desktop, Claude Code y una clave de API de Anthropic con créditos.

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
playwright install chromium
cp .env.example .env        # escribe ANTHROPIC_API_KEY y MODEL
```

## Uso

```bash
# Sesión 1: agentes por separado
python -m agentes.analista historias/HU-01-registrar-empleado.md
python -m agentes.disenador_pruebas salida/HU-01/criterios.feature

# Sesiones 2 a 4: la fábrica completa, cada vez con más agentes
python -m flujos.flujo_s2 historias/HU-01-registrar-empleado.md
python -m flujos.flujo_s3 historias/HU-01-registrar-empleado.md
python -m flujos.flujo_s4 historias/HU-01-registrar-empleado.md
```

Los patrones de cada sesión también tienen un ejemplo corto y ejecutable en [`ejemplos/`](ejemplos/README.md), por ejemplo `python -m ejemplos.s2_flujos.enrutamiento`.

La aplicación queda en http://localhost:8080 y la documentación de la API en http://localhost:8000/docs.
