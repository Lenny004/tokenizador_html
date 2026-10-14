from html_analyzer import analyze


def test_rules_report_layers_and_locations():
    source = "<div id='same'><span></div><div id='same'></div><script>value = {</script>"
    result = analyze(source).as_dict()
    layers = {finding["layer"] for finding in result["findings"]}
    assert {"structure", "syntax", "logic"}.issubset(layers)
    assert all(finding["line"] >= 1 and finding["column"] >= 1 for finding in result["findings"])


def test_large_document_stays_fast():
    source = "<section><p>ok</p></section>\n" * 3000
    result = analyze(source)
    assert result.tokens > 9000
    assert result.elapsed_ms < 2500


def test_embedded_js_keeps_absolute_location():
    result = analyze("<body>\n  <script>\n    unknownValue = 1;\n  </script>\n</body>")
    finding = next(item for item in result.findings if item.code == "JS-UNDECLARED")
    assert (finding.line, finding.column) == (3, 5)
