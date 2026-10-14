from html_analyzer.lexer import tokenize_html, tokenize_js


def test_html_tokens_include_tag_attributes_and_positions():
    tokens = tokenize_html('<main id="app"><br></main>')
    assert [token.kind for token in tokens[:4]] == ["tag_open", "attribute", "attribute_value", "tag_end"]
    assert tokens[0].line == 1 and tokens[0].column == 1


def test_js_lexer_detects_unterminated_string_and_invalid_char():
    tokens = tokenize_js("const value = 'oops\n@")
    assert any(token.kind == "unterminated_string" for token in tokens)
    assert any(token.kind == "invalid" for token in tokens)
