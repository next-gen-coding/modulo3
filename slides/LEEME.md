# Módulo 3 · Construcción de Sistemas Agénticos — presentación por sesión

Cuatro decks, uno por sesión, con el estilo «Tec Editorial» (`assets/tec-inspira.css` y `assets/deck.js`).

| Sesión | HTML | PowerPoint | Láminas |
| --- | --- | --- | --- |
| 1 · Arquitectura de agentes | `m3-sesion1-arquitectura-de-agentes.html` | `pptx/m3-sesion1-arquitectura-de-agentes.pptx` | 35 |
| 2 · Diseño de flujos complejos | `m3-sesion2-flujos-complejos.html` | `pptx/m3-sesion2-flujos-complejos.pptx` | 34 |
| 3 · Sistemas multi-agente | `m3-sesion3-sistemas-multiagente.html` | `pptx/m3-sesion3-sistemas-multiagente.pptx` | 36 |
| 4 · Seguridad en sistemas agénticos | `m3-sesion4-seguridad.html` | `pptx/m3-sesion4-seguridad.pptx` | 22 |

- Las láminas son las de la presentación completa (diagramas, código y notas del orador), con el estilo del sistema.
- Cada sesión abre con la portada de marca y cada bloque con su lámina de apertura.
- Toda lámina lleva el momento INSPIRA y la marca de tiempo de su bloque; los bloques de contenido no pasan de 20 minutos y cada sesión suma 2 h 30 min.
- `dist/` tiene los mismos HTML en un solo archivo (CSS, JS y logotipos incrustados), para enviar o imprimir.
- Teclas: `→` avanzar, `N` notas, `D` modo oscuro, `F` pantalla completa.

## Regenerar

```bash
python3 fuente/construir.py fuente/laminas        # HTML y dist/
for f in m3-sesion*.html; do
  python3 fuente/pptx/extraer.py "$f" "/tmp/${f%.html}.json"
  node fuente/pptx/construir.js "/tmp/${f%.html}.json" "pptx/${f%.html}.pptx" "${f%.html}"
done
```

`fuente/sesiones.py` define qué lámina va en qué bloque, con su momento y su tiempo. Los PowerPoint pasan la validación de esquema de Office (`validate.py`): títulos en Georgia, texto en Arial y código en Courier New.
