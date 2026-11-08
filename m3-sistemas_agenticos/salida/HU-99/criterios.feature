# language: es

Característica: Exportar la plantilla de empleados en CSV

  Como persona del área de Recursos Humanos,
  quiero descargar el directorio de empleados en CSV,
  para compartir el archivo con el área de nómina.

  Escenario: Descargar CSV con empleados activos
    Dado que existen empleados registrados con estado activo
    Y un empleado con número "EMP-0001", nombre "Juan García", puesto "Analista", departamento "Tecnología" y estado "activo"
    Y otro empleado con número "EMP-0002", nombre "María López", puesto "Vendedor", departamento "Ventas" y estado "activo"
    Cuando solicito descargar el CSV del directorio de empleados
    Entonces recibo un archivo CSV con las columnas: número de empleado, nombre, puesto, departamento, estado
    Y el archivo contiene la fila con "EMP-0001", "Juan García", "Analista", "Tecnología", "activo"
    Y el archivo contiene la fila con "EMP-0002", "María López", "Vendedor", "Ventas", "activo"
    Y el tipo de contenido es "text/csv"
    Y la respuesta HTTP es 200

  Escenario: Descargar CSV incluye empleados dados de baja
    Dado que existe un empleado activo con número "EMP-0001" y nombre "Pedro Ruiz"
    Y existe un empleado dado de baja con número "EMP-0002", nombre "Ana Martín", estado "baja" y fecha de baja "2025-01-15"
    Cuando solicito descargar el CSV del directorio de empleados
    Entonces el archivo contiene la fila con "EMP-0002", "Ana Martín", estado "baja"
    Y la respuesta HTTP es 200

  Escenario: Descargar CSV con directorio vacío
    Dado que no hay empleados registrados en el sistema
    Cuando solicito descargar el CSV del directorio de empleados
    Entonces recibo un archivo CSV con solo la fila de encabezados: número de empleado, nombre, puesto, departamento, estado
    Y el archivo no contiene filas de datos
    Y la respuesta HTTP es 200

  Escenario: Descargar CSV desde la pantalla con éxito
    Dado que estoy en la pantalla del directorio de empleados
    Y existen al menos dos empleados registrados
    Cuando hago clic en el botón descargar CSV
    Entonces se descarga un archivo CSV con nombre que contiene "empleados" y la fecha actual
    Y el archivo se abre sin errores
    Y el tipo de contenido descargado es "text/csv"

  Escenario: Descargar CSV vacío desde pantalla
    Dado que estoy en la pantalla del directorio de empleados
    Y no hay empleados registrados en el sistema
    Cuando hago clic en el botón descargar CSV
    Entonces se descarga un archivo CSV con solo encabezados
    Y se muestra el mensaje "El directorio está vacío, se descarga la plantilla" en el elemento con data-testid "mensaje-info"
    Y la respuesta HTTP es 200

# Preguntas abiertas

- El contexto no especifica la URL o el endpoint exacto para descargar el CSV (por ejemplo, `GET /api/empleados/export` o similar). Se asume que existe un endpoint que devuelve CSV.
- No se indica si el botón de descarga debe aparecer solo si hay empleados, o si siempre está disponible (incluso para descargar la plantilla vacía).
- No se define el formato exacto del nombre del archivo descargado (por ejemplo, `empleados-2025-01-20.csv`, `directorio_empleados.csv`, etc.).
- No se especifica si la descarga debe incluir solo empleados activos o todos (activos y dados de baja). El escenario asume todos.
- El contexto no menciona la estructura exacta de filas en el CSV (por ejemplo, con o sin espacios, separador exacto, etc.).
