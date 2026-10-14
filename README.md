<!-- readme-standard:v1 -->
<!-- Esta línea permite que los agentes de IA reconozcan y actualicen este README. No la borres. -->

<!-- section:header -->
# Tokenizador HTML

> Prototipo universitario de análisis estático HTML5 y JavaScript en el navegador.

<!-- section:toc -->
## 📑 Contenido

- [Aspectos destacados](#-aspectos-destacados)
- [Descripción](#%E2%84%B9%EF%B8%8F-descripción)
- [Requisitos](#%EF%B8%8F-requisitos)
- [Instalación](#%EF%B8%8F-instalación)
- [Uso](#-uso)
- [Estructura del proyecto](#%EF%B8%8F-estructura-del-proyecto)
- [Desarrollo](#%EF%B8%8F-desarrollo)
- [Pruebas](#-pruebas)
- [Soporte y contribuciones](#-soporte-y-contribuciones)

<!-- section:highlights -->
## 🌟 Aspectos destacados

- **Lexer HTML5 + JavaScript**: recorre etiquetas, atributos, texto y scripts embebidos con línea y columna.
- **AST tolerante**: conserva la estructura del documento para localizar anidamiento y cierres inesperados.
- **Reglas en capas**: separa estructura, sintaxis y lógica para priorizar la corrección.
- **Interfaz sin backend**: ejecuta Python mediante Pyodide desde una interfaz de chat y editor local.
- **Fixture de rendimiento**: incluye `ejemplo_prueba.html` con aproximadamente 3 000 líneas y 16 errores sembrados en tres capas.
- **Editor resaltado**: marca cada hallazgo sobre la línea y permite saltar al rango exacto desde su tarjeta.

<!-- section:overview -->
## ℹ️ Descripción

Este prototipo ayuda a inspeccionar documentos HTML5 grandes con JavaScript embebido. El usuario puede pegar código, cargar un archivo o abrir el ejemplo incluido; el pipeline genera tokens, construye un AST y responde con hallazgos agrupados por capa, línea y columna.

La ejecución ocurre en el navegador: el paquete Python se carga en Pyodide y no requiere backend. El diseño está pensado para una práctica universitaria y prioriza trazabilidad, reglas sencillas y tiempos medibles sobre una implementación completa del estándar ECMAScript.

**Stack:** Python, Pyodide, HTML5, JavaScript ES modules y CSS BEM con design tokens.

<!-- section:requirements -->
## 📋 Requisitos

- Python 3.10 o superior para el servidor estático y las pruebas.
- Navegador moderno con módulos ES, `fetch` y soporte para WebAssembly.
- Conexión a internet durante la primera carga para obtener Pyodide desde jsDelivr.

<!-- section:installation -->
## ⬇️ Instalación

```bash
python -m http.server 8000
```

Abre `http://localhost:8000` en el navegador. El servidor es necesario porque el navegador bloquea algunos módulos y archivos Python cuando se abre `index.html` directamente.

<!-- section:usage -->
## 🚀 Uso

1. Pega HTML5 y JavaScript en el editor, carga un archivo o pulsa **Abrir ejemplo**.
2. Pulsa **Analizar código**.
3. Revisa el resumen, el resaltado sobre el editor y las tarjetas: verde es estructura, gris sintaxis y rojo lógica. Al seleccionar una tarjeta, el editor salta a su rango.

También se puede analizar un archivo desde la terminal:

```bash
python -m html_analyzer.main ejemplo_prueba.html
```

El resultado esperado es un JSON con `findings`, `tokens`, `scripts`, tiempo de ejecución y resumen por capa.

<!-- section:structure -->
## 🗂️ Estructura del proyecto

```text
.
├── html_analyzer/          # Lexer, parser, reglas y API de análisis en Python
├── tests/                  # Pruebas pytest de lexer, AST, reglas y rendimiento
├── styles/                 # Tokens, reset, base y bloques BEM
├── scripts/                # Generador del fixture grande
├── ejemplo_prueba.html     # Documento de aproximadamente 3 000 bloques con errores
├── index.html               # Interfaz de editor y chat
└── app.js                   # Puente Pyodide y comportamiento del navegador
```

<!-- section:data -->
## 🧾 Datos

`ejemplo_prueba.html` es un fixture UTF-8 generado por `scripts/generate_example.py`. Contiene 2 897 líneas, registros repetidos para probar volumen y 16 errores distribuidos entre estructura, sintaxis y lógica.

<!-- section:development -->
## 🛠️ Desarrollo

Para regenerar el documento grande después de ajustar el patrón:

```bash
python scripts/generate_example.py
```

Los módulos mantienen nombres `snake_case`; la interfaz usa bloques BEM y los tokens visuales viven en `styles/tokens.css`.

<!-- section:testing -->
## ✅ Pruebas

```bash
python -m pytest -q
```

Las pruebas cubren posiciones del lexer, cadenas JavaScript sin cerrar, construcción del AST, elementos void, capas de reglas, posiciones exactas del fixture de 2 897 líneas y rendimiento inferior a un segundo.

<!-- section:contributing -->
## 💭 Soporte y contribuciones

Reporta errores con el código de regla, línea, columna y un fragmento mínimo reproducible. Para contribuir, añade una prueba junto con cada cambio del lexer, parser o regla y ejecuta `python -m pytest -q` antes de abrir una propuesta.

<!-- section:license -->
## 📄 Licencia

Uso académico.
