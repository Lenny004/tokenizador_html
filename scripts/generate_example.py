"""Genera el fixture HTML grande usado para pruebas manuales y de rendimiento."""

from pathlib import Path


def build() -> str:
    """Genera el contenido HTML del fixture con errores distribuidos."""
    lines = [
        "<!doctype html>",
        '<html lang="es">',
        "<head>",
        '  <meta charset="utf-8">',
        "  <title>Ejemplo de analisis</title>",
        "</head>",
        "<body>",
        '  <main id="catalogo">',
    ]
    planted = {
        100: ['    <p class="invalid-nesting"><div>Contenido con anidamiento invalido</div></p>'],
        150: ['    <article id="duplicado"><h2>Primer id repetido</h2></article>'],
        200: ['    <script>const total_200 = { total_200;</script>'],
        250: ['    <article atributo-inventado="permitido"><h2>Atributo no valido</h2></article>'],
        300: ['    <div><span>Cierre que no corresponde</div>'],
        350: ['    <article id="duplicado"><h2>Segundo id repetido</h2></article>'],
        400: ['    <script>const total_400 = (1 + 2;</script>'],
        450: ['    <article atributo-inventado="sin cerrar><h2>Comillas sin cerrar</h2></article>'],
        500: ['    <script>const token_500 = 1 @ 2;</script>'],
        550: ['    <script>const text_550 = \'cadena sin cerrar;</script>'],
        600: ['    <img src="imagen.png"></img>'],
        650: ['    <script>unknown_650 = 1;</script>'],
    }
    for index in range(1, 731):
        lines.extend(planted.get(index, [
            f'    <article class="card" data-index="{index}">',
            f"      <h2>Registro {index}</h2>",
            f"      <p>Contenido de prueba para la linea {index}.</p>",
            "    </article>",
        ]))
    lines.extend([
        '    <article class="missing-close"><h2>Etiqueta sin cerrar</h2>',
        "  </main>",
        "</body>",
        "</html>",
        "<section>Elemento abierto al final",
    ])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    Path("ejemplo_prueba.html").write_text(build(), encoding="utf-8")
