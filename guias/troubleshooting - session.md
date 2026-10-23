# Antecedentes: ambiente no listo (linux/Mac)
 ```bash
    open -a Docker
    docker info
    docker run --rm hello-world
    docker context ls
    docker context use desktop-linux
```

# Troubleshooting · Sesión 1 · Labs 1B y 1C

Problemas 1 y 2: analista (Lab 1B). Problemas 3 y 4: diseñador de pruebas (Lab 1C).

## Problema 1 · «No se escribió salida/HU-01/criterios.feature»

**Síntoma:** el analista lee y lista archivos, pero termina sus dos intentos sin guardar nada:

```
ValueError: Criterios inválidos tras varios intentos:
- No se escribió salida/HU-01/criterios.feature.
```

**Causa:** el modelo **razona antes de actuar**, y ese razonamiento consume tokens del mismo presupuesto que la respuesta. Al generar la llamada a `escribir_archivo` con el Gherkin completo, se le acaban los tokens a media acción. La API responde con `stop_reason = "max_tokens"`. El bucle solo distingue `tool_use` de todo lo demás, así que trata el corte como si el agente hubiera terminado: el archivo nunca se escribe.

**Cómo confirmarlo:** corre este diagnóstico desde la raíz del repo, sin modificar ningún archivo:

```bash
python - <<'EOF'
from pathlib import Path
from anthropic.resources.messages import Messages
import agentes.analista as an

original = Messages.create
def create(self, *a, **k):
    r = original(self, *a, **k)
    print("     stop_reason:", r.stop_reason, "| bloques:", [b.type for b in r.content])
    return r
Messages.create = create

an.generar_criterios(Path("historias/HU-01-registrar-empleado.md").resolve())
EOF
```

Si la última llamada de cada intento muestra `stop_reason: max_tokens`, es este problema.

**Solución:** en `agentes/base.py`, dentro de `ejecutar_agente`, sube el límite en la llamada al modelo:

```python
resp = cliente.messages.create(model=os.environ["MODEL"], max_tokens=16000, system=sistema,   # antes: 8000
                               tools=[h.esquema() for h in herramientas], messages=mensajes)
```

> No subas mucho más de 16000. Arriba de ~21000 tokens, el SDK de Anthropic exige *streaming* y lanzará otro error.

**Mejora recomendada:** que el corte no pase en silencio. Justo después de guardar la respuesta en `mensajes`:

```python
if resp.stop_reason == "max_tokens":
    raise RuntimeError(f"{nombre}: la respuesta se cortó por max_tokens; súbelo o pide una salida más corta")
```

**Lección:** el agente no razonó mal; **se quedó sin espacio a media acción**, y el bucle no lo notó. Los errores no se silencian.

---

## Problema 2 · «El escenario N no tiene 'Dado'»

**Síntoma:** el analista ya escribe el archivo, pero el validador lo rechaza:

```
ValueError: Criterios inválidos tras varios intentos:
- El escenario 1 no tiene 'Dado'.
- El escenario 2 no tiene 'Dado'.
```

**Causa:** el modelo usó **`Antecedentes:`**, un bloque de pasos `Dado` compartidos por todos los escenarios, y posiblemente también **`Esquema del escenario:`**. Ambos son Gherkin válido, pero `validar_gherkin` revisa cada escenario por separado y no los reconoce. **Las instrucciones y el validador no estaban alineados:** el prompt no decía qué formato se esperaba, y el modelo eligió uno que el validador no acepta.

**Cómo confirmarlo:**

```bash
cat salida/HU-01/criterios.feature
```

Si ves `Antecedentes:` arriba de los escenarios, es este problema.

**Solución:** en `agentes/analista.py`, reemplaza el punto 2 de `SISTEMA` por:

```python
2. Guarda el Gherkin con la herramienta escribir_archivo en {destino}. La primera línea es
   `# language: es` y usas solo las palabras clave Característica, Escenario, Dado, Cuando,
   Entonces, Y. No uses Antecedentes ni Esquema del escenario: cada Escenario lleva su propio
   Dado, Cuando y Entonces.
```

Qué cambia y por qué:

| Antes | Ahora | Por qué |
| --- | --- | --- |
| «Escribe {destino}» | «Guarda… con la herramienta escribir_archivo» | Deja claro que el archivo se guarda con la herramienta, no en el texto de la respuesta |
| «usas las palabras clave…» | «usas **solo** las palabras clave…» | Convierte la lista en un límite, no en una sugerencia |
| (nada) | «No uses Antecedentes ni Esquema del escenario» | Alinea el prompt con lo que revisa el validador |

Antes de volver a ejecutar, borra la versión anterior:

```bash
rm salida/HU-01/criterios.feature
python -m agentes.analista historias/HU-01-registrar-empleado.md
```

**Lección:** el evaluador también puede estar mal calibrado. **Las instrucciones, el validador y la crítica tienen que decir lo mismo.** Si el validador exige algo, el prompt debe pedirlo desde el principio; no conviene que el modelo lo descubra en la reflexión.

---

## Problema 3 · Diseñador de pruebas: «Casos inválidos tras varios intentos»

**Síntoma:** el diseñador sí escribe `salida/HU-01/casos_prueba.json` (y dice cuántos casos escribió), pero agota sus intentos:

```
ValueError: Casos inválidos tras varios intentos:
- ...
```

Las líneas que siguen a `ValueError` dicen qué rechazó el validador. Léelas siempre: ahí está la causa.

**Cómo ver exactamente qué rechaza:** corre el validador sobre el archivo que ya existe. No llama a la API y es instantáneo:

```bash
python -c "
from pathlib import Path
from agentes.disenador_pruebas import validar_plan
print(*validar_plan(Path('salida/HU-01/casos_prueba.json').read_text(), Path('salida/HU-01/criterios.feature').read_text()), sep='\n')
"
```

**Las tres causas probables:**

| Causa | Qué verás | Por qué pasa |
| --- | --- | --- |
| **A. Valores que no son texto en `datos`** (la más común) | `'type': 'string_type', 'loc': ('casos', 4, 'datos', 'nombre'), 'msg': 'Input should be a valid string', 'input': None` | El esquema dice `datos: dict[str, str]`: todos los valores deben ser texto. El modelo escribe `201` en lugar de `"201"`, o `null` para un campo vacío. Pydantic no convierte números a texto automáticamente |
| **B. El nombre del escenario no coincide** | `Escenario sin casos: Registro exitoso con número asignado` | El validador compara el campo `escenario` con el nombre del `.feature` letra por letra. Si el modelo escribe `"Escenario: Registro exitoso"` o cambia una palabra, no coincide |
| **C. JSON envuelto en Markdown** | `'type': 'json_invalid'` | El modelo guardó el JSON entre `` ```json `` y `` ``` ``, y entonces ya no es JSON válido |

**Solución:** las tres se corrigen en el prompt, sin aflojar el esquema. `casos_prueba.json` es el contrato con el agente 5 (automatizador), así que conviene que sea estricto. En `agentes/disenador_pruebas.py`, reemplaza el punto 4 de `SISTEMA` por:

```python
4. Guarda con la herramienta escribir_archivo en {destino} un JSON puro (sin ```json) que cumpla
   exactamente este esquema:
{esquema}
   - En "datos" TODOS los valores son texto: "201", no 201; para un campo vacío usa "", nunca null.
   - En "escenario" copia el nombre del escenario EXACTAMENTE como aparece después de "Escenario:".
```

Antes de volver a ejecutar, borra la versión anterior:

```bash
rm salida/HU-01/casos_prueba.json
python -m agentes.disenador_pruebas salida/HU-01/criterios.feature
```

> Si además el modelo **cambia los nombres de los campos** (por ejemplo `casos_prueba` en lugar de `casos`), ve directo a la solución del Problema 4: la herramienta `guardar_casos` resuelve también este problema.

**Lección:** el modelo hizo un buen trabajo, pero el prompt no le decía las reglas que el validador iba a exigir. El esquema JSON sí dice `"type": "string"`, pero entre muchas líneas un detalle así se pierde. Escribirlo explícitamente en las instrucciones alinea las tres piezas: **prompt, validador y crítica**. Es la misma lección del problema 2.

---

## Problema 4 · Diseñador de pruebas: el modelo inventa su propio formato de JSON

**Síntoma:** el diseñador escribe `casos_prueba.json` en los dos intentos, pero el validador lo rechaza con un error enorme que empieza así:

```
ValueError: Casos inválidos tras varios intentos:
- El JSON no cumple el esquema: [{'type': 'missing', 'loc': ('historia',), 'msg': 'Field required', 'input': {'historia_usuario': 'HU-01', 'titulo': ..., 'casos_prueba': [ ... miles de caracteres ... ]
```

**Causa:** los casos pueden ser muy buenos, pero el modelo **inventó su propio formato** en lugar del contrato `PlanPruebas`:

| Lo que exige `PlanPruebas` | Lo que suele escribir el modelo |
| --- | --- |
| `historia` | `historia_usuario` |
| `casos` | `casos_prueba` |
| `escenario` (un texto) | `escenario_feature`, a veces una lista de escenarios |
| `nivel`: `"api"` o `"e2e"` | `tipo`: `"funcional"`, `"validacion"`, `"ui"` |
| `datos` (todo texto) | `datos_entrada`, a veces con números o listas |
| (nada más) | Campos extra: `titulo`, `prioridad`, `codigo_http_esperado`… |

Tres razones se combinan:

1. **El esquema que recibe es difícil de seguir.** El prompt le pasa el JSON Schema completo de Pydantic, largo y técnico. Con muchos casos que diseñar, el modelo prioriza el contenido y «mejora» el formato a su gusto.
2. **El contexto contamina.** Si en `salida/HU-01/` quedaron archivos de pruebas anteriores con otro formato, el agente los lee y los imita.
3. **La crítica de la reflexión es ilegible.** Los errores de Pydantic incluyen el campo `'input'` con **todo el JSON**, repetido varias veces. El dato importante («faltan `historia` y `casos`») queda enterrado, y el segundo intento repite el mismo formato.

**Cómo confirmarlo:** el error dice `'type': 'missing'` para `historia` o `casos`, y dentro de `'input'` aparecen nombres de campo distintos. Revisa también la carpeta:

```bash
ls salida/HU-01/
```

Solo debería haber `criterios.feature` (y `notas_s1.md`, si ya lo escribiste).

**Por qué no basta con el prompt:** se puede intentar con un ejemplo concreto del JSON en las instrucciones, pero en la práctica el modelo lo sigue solo a medias (por ejemplo, corrige `historia` pero mantiene `casos_prueba`). Pedir un formato en el prompt es una **petición**; con muchos casos que diseñar, el modelo prioriza el contenido.

**Solución (probada): el contrato va en el esquema de una herramienta.** En lugar de que el modelo escriba el JSON a mano con `escribir_archivo`, recibe una herramienta `guardar_casos` cuyos parámetros **son** `PlanPruebas`. El modelo llena campos, la herramienta valida y guarda, y si algo falla devuelve un error corto **en el mismo intento**. Es el mismo patrón de `ejemplos/s1_razonamiento/salidas_estructuradas.py`.

Cambios en `agentes/disenador_pruebas.py`:

**1. Importa `Herramienta`:**

```python
from agentes.base import RAIZ, Herramienta, ejecutar_agente, herramientas_archivos, rel
```

**2. Reemplaza el punto 4 de `SISTEMA`:**

```python
4. Guarda los casos llamando a la herramienta guardar_casos (no escribas el JSON a mano).
   - "nivel" solo puede ser "api" o "e2e".
   - En "datos" TODOS los valores son texto: "201", no 201; para un campo vacío usa "", nunca null.
   - En "escenario" copia el nombre del escenario EXACTAMENTE como aparece después de "Escenario:".
   - Si guardar_casos devuelve un error, corrige lo que indica y vuelve a llamarla.
```

**3. Agrega esta función antes de `disenar_casos`:**

```python
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
```

**4. En `disenar_casos`, cambia cómo se arman las herramientas y el prompt:**

```python
    lectura = [h for h in herramientas_archivos(lectura=[RAIZ / "contexto", carpeta], escritura=carpeta)
               if h.nombre != "escribir_archivo"]          # solo se escribe a través de guardar_casos
    herramientas = lectura + [herramienta_guardar_casos(destino)]
    sistema = SISTEMA.format(criterios=rel(criterios))
```

Qué logra cada pieza:

| Pieza | Efecto |
| --- | --- |
| Parámetros de `guardar_casos` = esquema de `CasoPrueba` | El formato correcto es la forma natural de responder: el modelo llena campos con nombre y tipo |
| Validación dentro de la herramienta | Si falta o sobra algo, el modelo recibe `casos.0.nivel: Field required` y corrige en el mismo intento |
| Quitar `escribir_archivo` | La única forma de guardar es la herramienta: no puede escribir un formato inventado |
| `validar_plan` al final (sin cambios) | Sigue comprobando que cada escenario tenga al menos un caso |

`agentes/base.py` no se toca.

Antes de volver a ejecutar, borra el JSON anterior y cualquier archivo ajeno de la carpeta:

```bash
rm salida/HU-01/casos_prueba.json
python -m agentes.disenador_pruebas salida/HU-01/criterios.feature
```

En la traza verás `guardar_casos(historia, casos)` en lugar de `escribir_archivo(ruta, contenido)`.

**Lección:**

- **Instrucción < ejemplo < contrato en la herramienta.** Pedir un formato en el prompt es una petición; ponerlo en el esquema de una herramienta lo convierte en la forma natural de responder.
- **La crítica tiene que ser corta y accionable.** Si el error está enterrado en miles de caracteres, el modelo no puede corregirlo.
- **El contexto contamina:** archivos viejos en la carpeta del agente influyen en lo que produce.

---

## Regla general para cualquier error de un agente

1. **Lee la traza y el mensaje completo del error:** las líneas `[analista · paso N]` o `[disenador · paso N]` dicen qué intentó hacer el agente, y las líneas después de `ValueError` dicen qué rechazó el validador.
2. **Mira el `stop_reason`** con el diagnóstico de arriba: `max_tokens` es un problema de límites, `end_turn` es un problema de instrucciones.
3. **Corrige al agente, no su resultado:** ajusta el prompt, el validador o los límites, y vuelve a ejecutar. Nunca edites a mano `criterios.feature` ni `casos_prueba.json`.
