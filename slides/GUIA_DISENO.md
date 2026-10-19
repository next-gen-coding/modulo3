# Sistema de diseño "Tec Editorial" — decks INSPIRA

Guía para crear los decks de los módulos 2 a 5 con la misma identidad, sin rehacer el diseño.

---

## Cómo se usa un deck

Se abre el `.html` en cualquier navegador. No necesita internet ni instalar nada.

| Tecla | Acción |
|---|---|
| `→` · `espacio` · doble clic | Avanzar (primero los pasos de animación de la slide) |
| `←` | Retroceder (paso a paso; al volver a una slide, llega en su estado final) |
| `↓` / `↑` | Saltar a la slide siguiente / anterior sin recorrer pasos |
| **`A`** | Reproducir la animación de la slide sola, en bucle (otra vez `A` la detiene) |
| `Inicio` / `Fin` | Primera / última slide |
| **`N`** | Mostrar u ocultar las notas del orador |
| **`D`** | Alternar modo oscuro (aula a oscuras o monitor con mucho brillo) |
| **`F`** | Pantalla completa |

El modo oscuro se recuerda entre sesiones. Al imprimir, el deck sale siempre en claro aunque lo tengas en oscuro.

Para generar el PDF: imprimir desde el navegador con orientación horizontal y márgenes en cero. Las notas del orador no se imprimen.

---

## Estructura de la carpeta

```
slides/
├── assets/
│   ├── tec-inspira.css     ← el diseño completo vive aquí
│   ├── deck.js             ← navegación, notas, cronómetro, cromo
│   └── logo-tec.png
├── _template.html          ← catálogo de slides: copia y pega
├── build_standalone.py     ← genera copias de archivo único
├── dist/                   ← salida del script (para enviar o imprimir)
└── m1-clase1-….html        ← los decks
```

Los decks **enlazan** el CSS y el JS en lugar de copiarlos. Ese es el punto: si mañana cambias un color o un tamaño en `tec-inspira.css`, los cinco módulos se actualizan solos.

---

## Crear el deck de un módulo nuevo

1. Copia `_template.html` como `m2-clase1-generacion-de-codigo.html` (mismo nivel que `assets/`, no dentro de otra carpeta).
2. Cambia el `<title>` y, sobre todo, el atributo del `<body>`:

   ```html
   <body data-deck="Módulo 2 · Clase 1 — Generación de código">
   ```

   Ese texto aparece en el pie, junto al logotipo, en todas las slides.
3. Copia del catálogo los bloques de slide que necesites y sustituye el contenido.
4. Cuando lo vayas a repartir, corre `python3 build_standalone.py` y usa lo que quede en `dist/`.

No hace falta declarar el logotipo, el folio ni la barra de progreso: `deck.js` los inyecta.

---

## Reglas de composición

**Una slide, una idea.** El objetivo son unas 60 palabras por slide. Si necesitas más, parte la slide: es gratis. Lo que no cabe, va a las notas del orador.

**Todas las slides llevan tres cosas.** Badge del momento INSPIRA, marca de tiempo y notas del orador. Si a una slide le falta el badge, es que no sabes qué momento pedagógico es, y eso se nota al impartir.

**El tiempo se declara y se respeta.** El `timebox` usa el formato `0:35 · 25 min` (hora de inicio dentro de la sesión y duración del bloque). Todas las slides de un mismo bloque comparten su timebox: así, al sumar los timeboxes distintos, obtienes la duración de la sesión.

**Los bloques de contenido no pasan de 20 minutos** y la slide de Significa va **a la mitad** del bloque, no al final. Es la pausa de sentido, no el cierre.

---

**Un deck, todos los profesores.** Los decks son comunes a todos los instructores del programa y no se personalizan. La presentación de cada instructor vive en su propio archivo (PPT, Keynote, PDF…); el deck de la Clase 1 de cada módulo trae, justo después de la portada, la slide marcador **"Conoce a tu instructor"**: al llegar ahí se cambia al archivo personal y se regresa al deck. Si un módulo nuevo necesita ese momento, copia esa slide tal cual.

## Los siete momentos

Cada momento tiene su color. Se aplica solo en el punto del badge y en detalles; el cuerpo del texto siempre es tinta sobre papel.

| Momento | Clase CSS | Color | Para qué |
|---|---|---|---|
| Introduce | `introduce` | terracota | El enganche, el WIIFM, la panorámica |
| Nutre | `nutre` | azul Tec | El contenido nuevo |
| Significa | `significa` | violeta | La pregunta poderosa, la conexión con su realidad |
| Practica | `practica` | verde | Laboratorios y ejercicios |
| Integra | `integra` | ocre | Recapitulación, checkpoints, validación |
| Reta | `reta` | naranja | La tarea fuera de la sesión |
| Acompaña | `acompana` | verde azulado | Descansos, canales de apoyo, asesorías |

```html
<div class="badge significa">Significa</div>
```

Los descansos se etiquetan como **Acompaña** (no inventes un momento "Descanso": no existe en el modelo).

---

## Piezas disponibles

| Necesitas | Usa |
|---|---|
| **Portada de la sesión** | `<section class="slide cover hero">` (ver abajo) |
| Apertura de bloque | `<section class="slide cover">` con `.kicker` + `<h1>` |
| Bloque destacado | `<div class="panel">` |
| Pregunta poderosa | `<div class="panel q">` |
| Dos columnas | `<div class="cols">` |
| Tres tarjetas | `<div class="cols3">` + `<div class="card">` |
| Cadena de pasos horizontal | `.flow` + `.fbox` + `.farrow` |
| Intercambio vertical | `.flowv` + `.frow` + `.fbox` (con `.api` / `.env`) |
| Ciclo | `.cycle` + `.cnode` |
| Capas apiladas | `.layers` + `.layer` + `.arrowdown` |
| Escalera de decisión | `.stairs` + `.stair` |
| Barras comparativas | `.barwrap` + `.bar` |
| Fichas de token | `.tokchip` |
| Descanso con reloj | `<section class="slide" data-timer="10">` + `.countdown` |

---

## Animaciones por pasos

Una slide puede construirse en varios pasos: cada `→` avanza uno y, al terminar, pasa a la siguiente slide. Los cuadritos junto al folio muestran cuántos pasos lleva y cuántos faltan. Al imprimir, cada slide sale en su estado final.

| Necesitas | Usa |
|---|---|
| Que algo aparezca en el paso n | `data-step="n"` (fundido hacia arriba) |
| … sin desplazamiento / emergente / barra que crece | añade `data-fx="fade"` · `"pop"` · `"grow"` |
| Que algo siempre visible se "encienda" en el paso n | `data-mark="n"` → recibe `.on` desde n y `.actual` en n |
| Estilos por paso en CSS | la slide recibe `.p1 … .pN` acumuladas: `.p2 .mi-cosa { … }` |
| Animación con JS | escucha `slide.addEventListener('paso', e => …)`; `e.detail.paso` y `e.detail.total`. Declara el total con `data-steps="N"` |

Reglas: dibuja el estado **como función del paso** (no acumules efectos), así retroceder e imprimir siempre dejan la slide coherente. Usa solo variables de color del sistema para que funcione en modo oscuro. Anota en las notas del orador qué muestra cada paso.

Ejemplos completos en `m1-clase1-arquitectura-llms.html`: siguiente token, pipeline, tokenización, embeddings, atención, generación autoregresiva, context window, temperature (con slider), top_p, frenos (max_tokens / stop sequences), el viaje cliente → servidor de una llamada a la API y la API stateless con backoff.

En `m1-clase2-prompt-engineering.html`: brecha METR (barras y contadores), anatomía del prompt coloreada por fragmentos, las 3 piezas de la petición, structured outputs (decodificación restringida), antes/después con dudas que se resuelven, dos roles sobre el mismo código, self-consistency + tree-of-thought y la escalera con costo relativo.

En `m1-clase3-tool-use-agentes.html`: traza del agente línea por línea, ciclo agéntico con ejemplo, perilla de autonomía, los 4 mensajes con el historial que crece, cadena de prompt injection, defensas en capas (queso suizo) y el loop del agente recorrido vuelta por vuelta.

En `m1-clase4-claude-code.html`: contadores del punch, capas del módulo que se desbloquean, la arquitectura como cebolla alrededor del loop, una terminal simulada que cicla modos con Shift+Tab, la compuerta de exclusión, la barra de la ventana de contexto con /init · @archivo · /context · /compact · /clear, TDD rojo → verde y el arco del módulo.

**Código:** dentro de `<pre>`, con `<span class="kw">` (palabras clave), `.fn` (funciones), `.str` (cadenas) y `.com` (comentarios).

**Texto:** `.big` para destacar, `.muted` para secundario, `.huge` para una cifra o frase sola. `<strong>` se pinta en azul Tec.

---

## La portada de marca

La slide 1 de cada sesión usa `class="slide cover hero"` y retoma el banner publicitario del certificado: fondo oscuro, logotipo en blanco y la jerarquía **Certificado → nombre del programa → filete → título de la sesión**.

```html
<section class="slide cover hero">
  <div class="badge introduce">Introduce</div>
  <div class="timebox">0:00 · Apertura</div>
  <p class="eyebrow">Certificado</p>
  <h1 class="programa">Next-Gen Coding: Desarrollo de Software con IA Generativa (Virtual)</h1>
  <h2 class="sesion">Título de la sesión</h2>
  <div class="kicker">Módulo X · Nombre del módulo</div>
  …
</section>
```

`deck.js` cambia el logotipo a su versión blanca y aclara el pie automáticamente mientras la portada está en pantalla; al avanzar, todo vuelve al papel claro. No hay que hacer nada más.

El nombre del programa se escribe **completo y tal cual aparece en la ficha de inscripción**: *Next-Gen Coding: Desarrollo de Software con IA Generativa (Virtual)*. Es el nombre que el participante vio al inscribirse y el que llevará su credencial.

Solo la portada va en oscuro. Las aperturas de bloque siguen en papel claro para no encarecer la impresión ni castigar la legibilidad en pantalla compartida.

---

## Decisiones de diseño (por si te preguntan)

**Papel cálido y apagado, no blanco.** El curso se imparte en Aula Virtual: el deck se ve por pantalla compartida durante sesiones de hasta tres horas. Un fondo casi blanco provoca *halación* —el brillo del fondo invade los trazos oscuros y reduce el contraste percibido— y fatiga la vista, sobre todo en monitores con el brillo alto. El papel `#EDE8DC` emite un **15% menos de luz** que un blanco casi puro y mantiene todos los colores por encima de WCAG AA.

**Texto de cuerpo en peso 500, no 400.** El trazo delgado se adelgaza todavía más al proyectarse o al recomprimirse en una videollamada. El peso medio se sostiene mejor sin volverse pesado. Por la misma razón el sistema **no** usa `-webkit-font-smoothing: antialiased`, que en macOS afina los trazos.

**Modo oscuro disponible (tecla D).** Para aulas a oscuras o equipos con brillo alto. Solo remapea las variables de color, con su propia paleta verificada en AA; la composición no cambia y al imprimir siempre sale en claro.

**Serif en los títulos.** El logotipo del Tec es una serif; los títulos la acompañan en lugar de contradecirla. El cuerpo va en sans para leerse a distancia.

**Filetes en lugar de tarjetas redondeadas.** Las reglas finas y los bloques con barra lateral son el vocabulario de la composición editorial. Las cajas redondeadas con sombra son el del *dashboard*, y es lo que hace que un deck parezca hecho en piloto automático.

**Azul institucional exacto.** `#0033A0`, muestreado del archivo del logotipo, no aproximado a ojo.

**Contraste verificado.** Todos los colores de texto superan 4.5:1 sobre el fondo (WCAG AA), incluidos los siete colores de momento y el resaltado de sintaxis.

---

## Al terminar un deck, revisa

- [ ] Todas las slides tienen badge, timebox y notas del orador.
- [ ] La suma de los timeboxes distintos da la duración de la sesión.
- [ ] Ningún bloque de contenido pasa de 20 minutos.
- [ ] Cada bloque tiene su Significa a la mitad.
- [ ] Ninguna slide pasa de ~90 palabras.
- [ ] Se ve bien en pantalla completa (`F`) a 1600×900.
- [ ] `python3 build_standalone.py` corre sin advertencias.
