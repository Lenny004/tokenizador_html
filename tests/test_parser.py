from html_analyzer.parser import parse_html


def test_parser_builds_script_ast():
    result = parse_html("<html><body><script>const ready = true;</script></body></html>")
    assert result.root.children[0].name == "html"
    assert len(result.scripts) == 1
    assert any(token.value == "ready" for token in result.scripts[0].tokens)


def test_parser_keeps_void_elements_without_children():
    result = parse_html("<div><img src='x'><p>Texto</p></div>")
    div = result.root.children[0]
    assert [child.name for child in div.children] == ["img", "p"]
