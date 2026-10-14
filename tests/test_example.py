from pathlib import Path

from html_analyzer import analyze


def test_fixture_reports_seeded_layers_and_exact_locations():
    source = Path("ejemplo_prueba.html").read_text(encoding="utf-8")
    result = analyze(source)
    expected = {
        ("structure", "HTML-NESTING", 405, 32),
        ("structure", "HTML-UNCLOSED", 1193, 10),
        ("structure", "HTML-CLOSING", 1193, 41),
        ("structure", "HTML-VOID-CLOSING", 2375, 27),
        ("syntax", "JS-BALANCE", 799, 31),
        ("syntax", "JS-BALANCE", 1587, 31),
        ("syntax", "HTML-QUOTE", 1784, 33),
        ("syntax", "JS-TOKEN", 1981, 33),
        ("syntax", "JS-QUOTE", 2178, 30),
        ("logic", "HTML-ATTRIBUTE", 996, 14),
        ("logic", "HTML-DUPLICATE-ID", 1390, 14),
        ("logic", "HTML-ATTRIBUTE", 1784, 14),
        ("logic", "JS-UNDECLARED", 2572, 13),
    }
    actual = {(item.layer, item.code, item.line, item.column) for item in result.findings}
    assert expected <= actual
    assert {item.layer for item in result.findings} == {"structure", "syntax", "logic"}
    assert result.elapsed_ms < 1000


def test_duplicate_id_points_to_attribute_and_unclosed_quote_does_not_cascade():
    duplicate = analyze('<main id="one"><p id="one"></p></main>')
    finding = next(item for item in duplicate.findings if item.code == "HTML-DUPLICATE-ID")
    assert (finding.line, finding.column) == (1, 19)

    quoted = analyze('<article atributo-inventado="sin cerrar><h2>Texto</h2></article>')
    assert [item.code for item in quoted.findings] == ["HTML-ATTRIBUTE", "HTML-QUOTE"]
