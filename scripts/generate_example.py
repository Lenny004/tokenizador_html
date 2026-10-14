"""Genera el fixture HTML grande usado para pruebas manuales y de rendimiento."""

from pathlib import Path


def build() -> str:
    lines = ["<!doctype html>", '<html lang="es">', "<head>", '  <meta charset="utf-8">', "  <title>Ejemplo de análisis</title>", "</head>", "<body>", '  <main id="catalogo">']
    for index in range(1, 2990):
        lines.extend([f'    <article class="card" data-index="{index}">', f"      <h2>Registro {index}</h2>", f'      <p>Contenido de prueba para la línea {index}.</p>', "    </article>"])
    lines.extend([
        '    <article id="duplicado"><h2>Fallo lógico</h2></article>',
        '    <article id="duplicado" atributo-inventado="sin comillas><h2>Fallo de atributos</h2></article>',
        '    <script>',
        '      const total = 2990;',
        '      const broken = { total: total;',
        '      console.log(unknownValue);',
        "      const text = 'cadena sin cerrar;",
        '    </script>',
        '  </main>',
        '</body>',
        '</html>',
    ])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    Path("ejemplo_prueba.html").write_text(build(), encoding="utf-8")
