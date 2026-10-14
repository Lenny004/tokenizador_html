"""Construcción de un AST tolerante para HTML y scripts."""

from dataclasses import dataclass, field
import re
from .lexer import Token, tokenize_html, tokenize_js


@dataclass(slots=True)
class AstNode:
    node_type: str
    name: str
    line: int
    column: int
    attributes: dict[str, str] = field(default_factory=dict)
    children: list["AstNode"] = field(default_factory=list)
    tokens: list[Token] = field(default_factory=list)
    closing: bool = False


@dataclass(slots=True)
class ParseResult:
    root: AstNode
    tokens: list[Token]
    scripts: list[AstNode]


VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def parse_html(source: str) -> ParseResult:
    tokens = tokenize_html(source)
    root = AstNode("document", "#document", 1, 1)
    stack = [root]
    scripts: list[AstNode] = []
    current_tag: AstNode | None = None
    for token in tokens:
        if token.kind == "tag_open":
            node = AstNode("element", token.value.lower(), token.line, token.column)
            if stack:
                stack[-1].children.append(node)
            current_tag = node
            if node.name not in VOID_ELEMENTS:
                stack.append(node)
        elif token.kind == "tag_close":
            for index in range(len(stack) - 1, 0, -1):
                if stack[index].name == token.value.lower():
                    del stack[index:]
                    break
        elif token.kind == "attribute" and current_tag is not None:
            current_tag.attributes[token.value.lower()] = ""
        elif token.kind in {"attribute_value", "invalid_attribute_value"} and current_tag is not None:
            if current_tag.attributes:
                name = next(reversed(current_tag.attributes))
                current_tag.attributes[name] = token.value
        elif token.kind == "text" and current_tag and current_tag.name == "script":
            script = AstNode("script", "script", token.line, token.column, tokens=tokenize_js(token.value, token.offset, source))
            current_tag.children.append(script)
            scripts.append(script)
        elif token.kind == "invalid":
            stack[-1].children.append(AstNode("invalid", token.value, token.line, token.column))
    return ParseResult(root, tokens, scripts)
