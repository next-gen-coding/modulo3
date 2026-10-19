"""Reparto de las láminas en cuatro sesiones, con su bloque, su momento INSPIRA y su marca de tiempo.

Cada bloque abre con su lámina de apertura. Los bloques de contenido no pasan de 20 minutos y los
timeboxes de cada sesión se encadenan hasta sumar 2 h 30 min.
"""


def bloque(badge, tb, kicker, titulo, sub, notas, *ids, badge_laminas=None):
    b = badge_laminas or badge
    return [("apertura", badge, tb, kicker, titulo, sub, notas)] + [("lamina", i, b, tb) for i in ids]


S1 = [("portada", "Bienvenida, verificación de audio y pantalla. En este módulo cada estudiante construye su propia fábrica de "
                  "software: seis agentes que toman una historia de usuario y entregan una aplicación de gestión de empleados "
                  "probada de punta a punta. Hoy: qué es un agente y cómo validar lo que produce.")]
S1 += bloque("introduce", "0:00 · 10 min", "Bloque 1.0", "Bienvenida y objetivos", "Cinco objetivos, un caso práctico y el entorno listo.",
             "Reparto: objetivos 3 min, la fábrica y el dominio 3 min, agenda y Claude Code 2 min, entorno 2 min. El entorno se envió una semana antes: aquí solo se verifica.",
             "objetivo", "caso", "dominio", "agenda", "claude-code", "entorno", "s1-objetivo")
S1 += bloque("nutre", "0:10 · 15 min", "Bloque 1.1", "Qué es un agente", "Quién decide el siguiente paso: el código o el modelo.",
             "Workflow contra agente y el bucle. Pide a la clase un ejemplo de su trabajo para cada columna.",
             "s1-agente", "s1-bucle")
S1 += bloque("nutre", "0:25 · 15 min", "Bloque 1.2", "Componentes y ReAct", "Cinco piezas y el primer patrón de razonamiento, en código.",
             "Componentes con el código abierto; después ReAct: la idea, el diagrama, la ejecución en vivo y el código.",
             "s1-componentes", "react-idea", "p-react", "c-react")
S1 += bloque("nutre", "0:40 · 10 min", "Bloque 1.3", "Plan-and-Execute", "Primero un plan que se puede aprobar; después, los pasos.",
             "La idea, el diagrama y el código. Ejecuta el ejemplo y responde «no» la primera vez.",
             "plan-idea", "p-plan", "c-plan")
S1 += bloque("nutre", "0:50 · 20 min", "Bloque 1.4", "Salidas estructuradas y reflexión", "El agente propone; el código decide.",
             "Objetivo 2 del módulo: el contrato, los tres niveles de validación y la reflexión con tope.",
             "s1-patrones", "p-salidas", "c-salidas", "reflexion-idea", "p-reflexion", "c-reflexion")
S1 += [("descanso", "1:10 · 10 min", 10, "Volvemos con el Lab 1: tus dos primeros agentes.")]
S1 += bloque("practica", "1:20 · 20 min", "Laboratorio 1A", "El bucle", "Completa ejecutar_agente y prueba los permisos de las herramientas.",
             "Riesgos: falta .env (KeyError MODEL), ejecutar el archivo en vez del módulo, clave sin créditos.",
             "s1-lab")
S1 += bloque("practica", "1:40 · 20 min", "Laboratorio 1B", "Agente analista", "HU-01 → criterios.feature, validado.",
             "Muestra el ejemplo de criterios antes de que ejecuten el analista.", "s1-retos")
S1 += bloque("practica", "2:00 · 15 min", "Laboratorio 1C", "Agente diseñador", "Criterios → casos_prueba.json, validado.",
             "El contrato es el modelo Pydantic CasoPrueba; los casos e2e usan los data-testid de las convenciones.")
S1 += bloque("integra", "2:15 · 15 min", "Cierre", "Preguntas, quiz y entrega", "Dos estudiantes muestran su salida; quiz de 5 preguntas; commit del entregable.",
             "Preguntas que conectan el lab con los conceptos: ¿por qué tu analista no se cayó con el PermissionError? ¿Qué parte de tu fábrica es workflow y cuál agente?")

S2 = [("portada", "Bienvenida. Hoy la fábrica genera su primera aplicación con Claude Code. Idea central: un flujo complejo se diseña "
                  "como un grafo con estado explícito, con puntos donde decide una persona.")]
S2 += bloque("integra", "0:00 · 10 min", "Bloque 2.0", "Revisión del entregable 1", "Dos estudiantes muestran sus criterios y sus casos.",
             "Comenta los errores frecuentes: reglas inventadas, datos vagos, casos sin data-testid.", "s2-objetivo")
S2 += bloque("nutre", "0:10 · 15 min", "Bloque 2.1", "Patrones de flujo · 1", "El mapa de los cinco patrones, encadenamiento y enrutamiento.",
             "Cada patrón: la idea, el diagrama, la ejecución en vivo y el código. Primer contacto con LangGraph.",
             "s2-patrones", "encadenamiento-idea", "p-encadenamiento", "c-encadenamiento",
             "enrutamiento-idea", "p-enrutamiento", "c-enrutamiento")
S2 += bloque("nutre", "0:25 · 15 min", "Bloque 2.2", "Patrones de flujo · 2", "Paralelización, orquestador y trabajadores, y evaluador-optimizador.",
             "Unos cinco minutos por patrón. Compara paralelización con orquestador: ramas fijas contra Send.",
             "paralelizacion-idea", "p-paralelizacion", "c-paralelizacion", "orquestador-idea", "p-orquestador", "c-orquestador",
             "evaluador-idea", "p-evaluador", "c-evaluador")
S2 += bloque("nutre", "0:40 · 15 min", "Bloque 2.3", "El humano en el flujo", "Orquestar también es decidir quién decide en cada punto.",
             "Objetivo 3 del módulo: niveles de autonomía, qué debe ver la persona, interrupt y Command(resume).",
             "p-humano", "c-humano")
S2 += bloque("nutre", "0:55 · 15 min", "Bloque 2.4", "LangGraph y Claude Code", "El estado del flujo y Claude Code como agente programable.",
             "Demostración: ejecutar desarrollador.planificar(\"HU-01\") y leer el plan con la clase.",
             "s2-estado", "s2-codigo")
S2 += [("descanso", "1:10 · 10 min", 10, "Volvemos con el Lab 2: tu fábrica genera su primera app.")]
S2 += bloque("practica", "1:20 · 10 min", "Laboratorio 2A", "Leer el grafo", "Dibújalo en papel y compáralo con draw_mermaid().",
             "Imprimir el grafo con construir_grafo().get_graph().draw_mermaid().", "s2-lab", "s2-pasos")
S2 += bloque("practica", "1:30 · 25 min", "Laboratorio 2B", "Ejecutar la fábrica con HU-01", "Rechaza el primer plan con un comentario concreto; aprueba el segundo.",
             "Un buen comentario de rechazo es concreto: «guarda el correo en minúsculas y valida el formato en el backend».")
S2 += bloque("practica", "1:55 · 20 min", "Laboratorio 2C", "Revisar la app", "Levanta backend y front-end y marca qué criterios cumple.",
             "Registrar un empleado, repetir el correo en mayúsculas, probar un correo que no sea @empresa.com, revisar /docs.")
S2 += bloque("integra", "2:15 · 15 min", "Cierre", "Preguntas, quiz y entrega", "app/, app/CLAUDE.md y notas_s2.md en un commit.",
             "Preguntas que conectan: ¿qué patrón es construir → verificar? ¿Qué cambió en el plan después de tu comentario?")

S3 = [("portada", "Bienvenida. Idea central: varios agentes se justifican cuando la tarea se divide en especialidades con contextos, "
                  "herramientas o permisos distintos. Verifica que Docker Desktop corre y que los puertos 8000 y 8080 están libres.")]
S3 += bloque("integra", "0:00 · 10 min", "Bloque 3.0", "Revisión del entregable 2", "La tabla de criterios cumplidos: ¿qué falló y por qué?",
             "Lo que falló en la tabla manual es justo lo que las pruebas automáticas de hoy deben atrapar.", "s3-objetivo")
S3 += bloque("nutre", "0:10 · 15 min", "Bloque 3.1", "Topologías · 1", "Cuándo usar varios agentes, supervisor y jerárquica.",
             "Todas las topologías usan la misma pieza de LangGraph, Command; la diferencia está en qué nodos la usan.",
             "s3-cuando", "s3-topologias", "supervisor-idea", "t-supervisor", "c-supervisor", "jerarquica-idea", "t-jerarquica", "c-jerarquica")
S3 += bloque("nutre", "0:25 · 15 min", "Bloque 3.2", "Topologías · 2", "Traspasos, red y pizarra.",
             "Compara supervisor.py con red.py: misma pieza, distinta distribución del poder de decisión.",
             "traspasos-idea", "t-traspasos", "c-traspasos", "red-idea", "t-red", "c-red", "pizarra-idea", "t-pizarra", "c-pizarra")
S3 += bloque("nutre", "0:40 · 10 min", "Bloque 3.3", "¿Qué arquitectura elijo?", "Tres preguntas, en orden, y un ejercicio en parejas.",
             "Objetivo 4 del módulo. Se califica la justificación, no la etiqueta.", "t-decision")
S3 += bloque("nutre", "0:50 · 10 min", "Bloque 3.4", "Roles, permisos y contratos", "Cada agente toca solo lo suyo.",
             "La razón principal para tener varios agentes en la fábrica es separar permisos.", "s3-protocolos")
S3 += bloque("nutre", "1:00 · 10 min", "Bloque 3.5", "MCP", "Herramientas que cualquier agente descubre.",
             "Demostración con mcp_cliente.py y con Claude Code (claude mcp add). Al terminar, claude mcp remove directorio.",
             "p-mcp", "c-mcp")
S3 += [("descanso", "1:10 · 10 min", 10, "Volvemos con el Lab 3: dos agentes en paralelo.")]
S3 += bloque("practica", "1:20 · 10 min", "Laboratorio 3A", "Leer los agentes 4 y 5", "Instrucciones, permisos y la rama paralela de flujo_s3.",
             "Pregunta: ¿por qué el automatizador puede trabajar al mismo tiempo que el despliegue?", "s3-lab")
S3 += bloque("practica", "1:30 · 30 min", "Laboratorio 3B", "Ejecutar con HU-02", "La fábrica extiende la app y la despliega.",
             "Aprobar el plan solo si extiende el código de HU-01 sin romperlo.", "s3-sdk")
S3 += bloque("practica", "2:00 · 15 min", "Laboratorio 3C", "Inspeccionar", "Contenedores, pruebas y auditoría por agente.",
             "Comparar las pruebas con la tabla manual de la sesión 2 y buscar en auditoria.jsonl un intento fuera de rol.")
S3 += bloque("integra", "2:15 · 15 min", "Cierre", "Preguntas, quiz y entrega", "docker-compose.yml, app/tests/ y notas_s3.md en un commit.",
             "Preguntas que conectan: ¿qué topología es tu fábrica? ¿Qué denegación encontraste en la auditoría?")

S4 = [("portada", "Bienvenida. Idea central: un agente convierte texto en acciones con credenciales reales, así que cualquier texto que "
                  "lea es una posible orden. Antes de la sesión, ejecuta el ataque con y sin defensas.")]
S4 += bloque("integra", "0:00 · 10 min", "Bloque 4.0", "Revisión del entregable 3", "Resultados de pytest y denegaciones de la auditoría.",
             "Las denegaciones encontradas son la mejor entrada al tema de hoy.", "s4-objetivo")
S4 += bloque("nutre", "0:10 · 20 min", "Bloque 4.1", "Riesgos de un sistema agéntico", "OWASP Top 10 agéntico, dentro de tu fábrica.",
             "Para cada riesgo, pide a la clase el archivo de su fábrica donde aparece y el que lo mitiga.", "s4-frase", "s4-owasp")
S4 += bloque("nutre", "0:30 · 15 min", "Bloque 4.2", "Tríada letal y defensas por capas", "Diseñar para romper al menos una de las tres piezas.",
             "¿Por qué un hook es más confiable que una frase en el prompt?", "s4-triada", "s4-capas", "s4-hooks")
S4 += bloque("nutre", "0:45 · 10 min", "Bloque 4.3", "El flujo end to end", "Si una prueba falla, el triage decide quién corrige.",
             "El triage enruta, no corrige; gana quien siga el criterio de aceptación.", "s4-e2e")
S4 += [("descanso", "0:55 · 10 min", 10, "Volvemos con el Lab 4: probar todo, atacar y defender.")]
S4 += bloque("practica", "1:05 · 25 min", "Laboratorio 4A", "La fábrica completa con HU-03", "Seis agentes de punta a punta y el reporte E2E.",
             "Aprobar el plan solo si respeta «no se puede editar a un empleado dado de baja».", "s4-lab")
S4 += bloque("practica", "1:30 · 25 min", "Laboratorio 4B", "Atacar y defender", "HU-99 y un contexto envenenado, con y sin defensas.",
             "Los ataques apuntan solo a secretos_demo.txt, nunca al .env real.")
S4 += bloque("reta", "1:55 · 20 min", "Laboratorio 4C y evaluación", "Reporte de seguridad y reto HU-10", "Tabla de ataques, checklist de producción, examen y reto.",
             "Presenta la evaluación: examen de conceptos (40 %) y reto en código con HU-10 (60 %).",
             "evaluacion", "reto", "rubrica")
S4 += bloque("integra", "2:15 · 15 min", "Cierre del módulo", "Demostraciones y retrospectiva", "Dos o tres fábricas completas y el checklist de producción.",
             "Abre espacio para preguntas sobre el reto y recuerda la fecha de entrega.", "cierre")

SESIONES = [
    dict(n=1, titulo="Arquitectura de agentes", promesa="Qué puede ver un agente, qué puede hacer y cuándo se detiene.",
         archivo="m3-sesion1-arquitectura-de-agentes.html", etiqueta="Módulo 3 · Sesión 1 — Arquitectura de agentes",
         titulo_html="M3 · Sesión 1 · Arquitectura de agentes", laminas=S1),
    dict(n=2, titulo="Diseño de flujos complejos", promesa="Un grafo con estado explícito, y una persona donde hace falta.",
         archivo="m3-sesion2-flujos-complejos.html", etiqueta="Módulo 3 · Sesión 2 — Diseño de flujos complejos",
         titulo_html="M3 · Sesión 2 · Diseño de flujos complejos", laminas=S2),
    dict(n=3, titulo="Sistemas multi-agente", promesa="Dividir el trabajo solo cuando las especialidades lo justifican.",
         archivo="m3-sesion3-sistemas-multiagente.html", etiqueta="Módulo 3 · Sesión 3 — Sistemas multi-agente",
         titulo_html="M3 · Sesión 3 · Sistemas multi-agente", laminas=S3),
    dict(n=4, titulo="Seguridad en sistemas agénticos", promesa="Limitar lo que el agente puede hacer, aunque lo engañen.",
         archivo="m3-sesion4-seguridad.html", etiqueta="Módulo 3 · Sesión 4 — Seguridad en sistemas agénticos",
         titulo_html="M3 · Sesión 4 · Seguridad en sistemas agénticos", laminas=S4),
]
