---
name: py-documentation
description: >-
  Úsala cuando el usuario pida documentar, comentar o explicar con docstrings
  archivos Python (.py) de un proyecto sin cambiar su lógica, comportamiento ni
  arquitectura.
---
# Documentación de código Python

Documenta los `.py` del proyecto en español sin modificar lógica, comportamiento ni arquitectura. Solo documentar: no refactorizar, corregir ni rediseñar.

## Reglas generales

1. No modificar la lógica ni el comportamiento.
2. No cambiar nombres, firmas, tipos, imports ni estructura; no reformatear, reordenar ni reindentar.
3. No agregar dependencias, configuración ni herramientas.
4. No convertir entre paradigmas o estilos (clases/funciones, sync/async).
5. Conservar la documentación correcta; si contradice el código, corregirla y reportarlo.
6. Comentarios en español; identificadores, APIs y términos técnicos sin traducir.
7. Mantener el estilo del proyecto; si no hay, docstrings estilo Google.
8. Explicar propósito y decisiones importantes, no cada línea.
9. No documentar funcionalidad inexistente, comentada o sin uso como si existiera.
10. No inventar reglas, flujos, motivos ni efectos. Lo incierto se omite y va a "Puntos que requieren confirmación".
11. No afirmar cumplimiento de estándares o patrones salvo que el proyecto lo declare; describir lo observable.
12. No copiar secretos, credenciales, tokens, hosts/IPs internos ni datos personales; reportarlos sin su valor.
13. Conservar directivas (`noqa`, `type: ignore`, `pragma`, `fmt: off`, `pylint: disable`) y TODO/FIXME.
14. Sin comentarios redundantes que repitan el nombre del elemento.
15. No tocar archivos fuera del alcance.

## Alcance

Incluir `.py`. Excluir `venv/`, `.venv/`, `env/`, `__pycache__/`, `build/`, `dist/`, `*.egg-info/`, migraciones autogeneradas, archivos generados ("auto-generated", "DO NOT EDIT") y pruebas (usarlas solo como contexto), y otros lenguajes.

## Formato

- Docstrings PEP 257 (`"""..."""`) en español para módulos, clases, funciones y métodos; `#` solo para decisiones dentro del código.
- Adoptar el estilo existente (Google, NumPy o Sphinx); si hay mezcla, el del archivo.
- No repetir tipos ya anotados; no agregar ni cambiar anotaciones.

### Módulos
- Docstring al inicio (después de `#!` y codificación, antes de imports; respetar `from __future__`): propósito y contenido.
- Efectos al importar (código suelto, conexiones, registros, configuración).
- Constantes con unidades o formato si no son evidentes.

### Clases
- Responsabilidad, atributos públicos (`Attributes`) e invariantes.
- dataclass/Pydantic/attrs: solo campos con restricciones o significado no evidente, sin duplicar `Field(...)` ni validadores.
- Métodos especiales solo si son no evidentes; en gestores de contexto, qué recurso adquieren y liberan.

### Funciones y métodos
Resumen de una línea y, cuando aporte: `Args` (significado, unidades, formato, restricciones), `Returns` (incluidos vacíos o nulos), `Raises` (lanzadas o propagadas de forma efectiva), `Yields`, efectos secundarios e idempotencia solo si el código la garantiza.

```python
def registrar_movimiento(producto_id: int, cantidad: int) -> int:
    """Registra un movimiento de inventario y actualiza el stock del producto.

    La operación se ejecuta en una sola transacción: si falla, no se
    guarda ningún cambio.

    Args:
        producto_id: Identificador del producto en la tabla `productos`.
        cantidad: Unidades del movimiento; negativa para salidas.

    Returns:
        Identificador del movimiento creado.

    Raises:
        ValueError: Si la salida deja el stock en negativo.
    """
```

### Propiedades, decoradores y generadores
- `@property`: qué calcula y si su costo es relevante.
- Decoradores propios: qué cambian y en qué orden se aplican.
- Generadores: qué producen, cuándo terminan, si se consumen una sola vez.

### Asincronía y concurrencia
- `async def`: qué espera, qué tareas lanza, cancelación y timeouts.
- Hilos y procesos: datos compartidos y sincronización.
- Tareas en segundo plano: frecuencia, reintentos, solapamiento.

### Datos y E/S
Qué leen o escriben (archivos, BD, HTTP, colas), formato y codificación; límites de transacción y qué se revierte; cierre de recursos (`with`, `try/finally`) ante errores.

### Frameworks
- FastAPI/Flask: método, ruta, parámetros, esquema de respuesta, códigos, `Depends`.
- Django: vistas, URLs, señales, managers, modelos (tabla, relaciones, motivo de `on_delete`); no tocar `help_text`, `verbose_name` ni `Meta`.
- Celery: qué hace, argumentos y reintentos.
- CLI (`argparse`, `click`, `typer`): argumentos, opciones, defaults, códigos de salida y el bloque `if __name__ == "__main__":`.

## Riesgos específicos de Python

Comprobar si el proyecto consume docstrings en tiempo de ejecución y redactar para ese lector: FastAPI/DRF (documentación de API), `click`/`typer`/`argparse` con `description=__doc__` (`--help`), Pydantic (esquema JSON), Sphinx/mkdocstrings.

- No usar `>>>` en ejemplos (doctest los ejecutaría).
- Conservar `#!`, codificación y directivas.
- No modificar migraciones ni ejecutar comandos que alteren datos.

## Aspectos transversales (solo si existen)

Entradas y validaciones, salidas, acceso (auth, roles), efectos secundarios, transacciones, idempotencia y concurrencia, errores y recuperación, observabilidad, configuración (variables de entorno, nunca valores reales). Describir sin evaluar ni agregar lo que no hace.

## Comentarios inline

Solo para el motivo de una decisión; uno por bloque lógico; sin describir sintaxis evidente; indicar unidades o formatos no evidentes; sin comentarios sobre el proceso ni código comentado.

## Proceso

1. Listar archivos del alcance y ordenarlos de lo básico a lo general (utilidades y tipos, lógica, puntos de entrada).
2. Leer contexto: archivo completo, usos, pruebas, README y `docs/`.
3. Detectar el estilo existente y si los docstrings se consumen en ejecución.
4. Revisar módulos, clases, funciones, excepciones, efectos al importar y recursos.
5. Conservar lo correcto y agregar solo lo que falta.
6. En proyectos grandes, trabajar por lotes y verificar entre lotes.
7. Revisar `git diff`: toda línea agregada debe ser comentario/docstring o línea en blanco asociada; toda eliminada, un comentario reemplazado. Revertir cualquier otra diferencia.
8. Verificar sin cambiar configuración: `python -m py_compile` por archivo y, si están configurados, `pytest`, `ruff`, `flake8`/`pylint`, `mypy`.
9. Releer: claros, breves, coherentes y sin información inventada.

## Formato de entrega

Por archivo: ruta, resumen de una línea, elementos documentados, confirmación de que no cambió la lógica y resultado de las verificaciones.

Al final:
- **Puntos que requieren confirmación**.
- **Hallazgos**: documentación corregida, código sin uso, posibles secretos (sin su valor).
- **Sin cambios**: archivos que no lo requerían, con nota breve.

Si una verificación no se pudo ejecutar, indicar cuál y por qué.
