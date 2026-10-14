"""Reglas agrupadas por estructura, sintaxis y lógica."""

from dataclasses import dataclass
import re
from .lexer import Token
from .parser import AstNode, ParseResult, VOID_ELEMENTS


@dataclass(slots=True)
class Finding:
    code: str
    message: str
    layer: str
    severity: str
    line: int
    column: int
    end_column: int | None = None

    def as_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "layer": self.layer, "severity": self.severity, "line": self.line, "column": self.column, "end_column": self.end_column}


ALLOWED_ATTRIBUTES = {"id", "class", "title", "style", "href", "src", "alt", "width", "height", "name", "type", "value", "placeholder", "action", "method", "for", "lang", "charset", "rel", "defer", "async", "data-*", "aria-*"}


def run_structure_rules(parsed: ParseResult) -> list[Finding]:
    findings: list[Finding] = []
    tag_stack: list[Token] = []
    for token in parsed.tokens:
        if token.kind == "tag_open" and token.value.lower() not in VOID_ELEMENTS:
            tag_stack.append(token)
        elif token.kind == "tag_close":
            if tag_stack and tag_stack[-1].value.lower() == token.value.lower():
                tag_stack.pop()
            else:
                findings.append(Finding("HTML-CLOSING", f"Cierre inesperado para '{token.value}'.", "structure", "error", token.line, token.column))
    for token in tag_stack:
        findings.append(Finding("HTML-UNCLOSED", f"La etiqueta '{token.value}' no está cerrada.", "structure", "error", token.line, token.column))
    open_tags: list[AstNode] = []
    seen_ids: set[str] = set()
    def visit(node: AstNode) -> None:
        if node.node_type != "element":
            for child in node.children:
                visit(child)
            return
        if node.name == "html" and open_tags:
            findings.append(Finding("HTML-NESTING", "La etiqueta html debe ser la raíz del documento.", "structure", "error", node.line, node.column))
        open_tags.append(node)
        if "id" in node.attributes and node.attributes["id"]:
            identifier = node.attributes["id"].strip("\"'")
            if identifier in seen_ids:
                findings.append(Finding("HTML-DUPLICATE-ID", f"El id '{identifier}' está duplicado.", "logic", "error", node.line, node.column))
            seen_ids.add(identifier)
        for attr in node.attributes:
            if not any(attr == allowed or (allowed.endswith("*") and attr.startswith(allowed[:-1])) for allowed in ALLOWED_ATTRIBUTES):
                findings.append(Finding("HTML-ATTRIBUTE", f"Atributo '{attr}' no reconocido para este prototipo.", "logic", "warning", node.line, node.column))
        for child in node.children:
            visit(child)
        open_tags.pop()
    visit(parsed.root)
    for token in parsed.tokens:
        if token.kind == "invalid":
            findings.append(Finding("HTML-TOKEN", "Token HTML inválido.", "syntax", "error", token.line, token.column))
        if token.kind == "invalid_attribute_value":
            findings.append(Finding("HTML-QUOTE", "Valor de atributo sin comillas balanceadas.", "syntax", "error", token.line, token.column))
    return findings


def run_syntax_rules(parsed: ParseResult) -> list[Finding]:
    findings: list[Finding] = []
    for token in parsed.tokens:
        if token.kind == "tag_close":
            continue
    for script in parsed.scripts:
        stack: list[Token] = []
        for token in script.tokens:
            if token.kind in {"invalid", "unterminated_string"}:
                message = "Token JavaScript inválido." if token.kind == "invalid" else "Cadena JavaScript sin cerrar."
                findings.append(Finding("JS-TOKEN" if token.kind == "invalid" else "JS-QUOTE", message, "syntax", "error", token.line, token.column))
            if token.value in "{[(":
                stack.append(token)
            elif token.value in "}])":
                expected = {"}": "{", "]": "[", ")": "("}[token.value]
                if not stack or stack[-1].value != expected:
                    findings.append(Finding("JS-BALANCE", f"Cierre '{token.value}' sin apertura correspondiente.", "syntax", "error", token.line, token.column))
                else:
                    stack.pop()
        for opening in stack:
            findings.append(Finding("JS-BALANCE", f"'{opening.value}' sin cerrar.", "syntax", "error", opening.line, opening.column))
    return findings


def run_logic_rules(parsed: ParseResult) -> list[Finding]:
    findings: list[Finding] = []
    declaration_words = {"var", "let", "const", "function"}
    for script in parsed.scripts:
        declared: set[str] = set()
        tokens = [token for token in script.tokens if token.kind != "comment"]
        for index, token in enumerate(tokens):
            if token.value in declaration_words and index + 1 < len(tokens) and tokens[index + 1].kind == "identifier":
                declared.add(tokens[index + 1].value)
            elif token.kind == "identifier" and (not index or tokens[index - 1].value not in {".", "function"}) and token.value not in declared and token.value not in {"console", "document", "window", "getElementById", "log"}:
                if index + 1 < len(tokens) and tokens[index + 1].value == "(":
                    continue
                findings.append(Finding("JS-UNDECLARED", f"Variable '{token.value}' usada sin declaración visible.", "logic", "warning", token.line, token.column))
    return findings
