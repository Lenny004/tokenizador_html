"""Reglas agrupadas por estructura, sintaxis y logica."""

from dataclasses import dataclass
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


def _end(token: Token) -> int:
    return token.column + max(len(token.value), 1)


def run_structure_rules(parsed: ParseResult) -> list[Finding]:
    findings: list[Finding] = []
    tag_stack: list[Token] = []
    for token in parsed.tokens:
        if token.kind == "tag_open" and token.value.lower() not in VOID_ELEMENTS:
            tag_stack.append(token)
        elif token.kind == "tag_close":
            if token.value.lower() in VOID_ELEMENTS:
                findings.append(Finding("HTML-VOID-CLOSING", f"El elemento void '{token.value}' no debe cerrarse.", "structure", "error", token.line, token.column, _end(token)))
            elif tag_stack and tag_stack[-1].value.lower() == token.value.lower():
                tag_stack.pop()
            else:
                findings.append(Finding("HTML-CLOSING", f"Cierre inesperado para '{token.value}'.", "structure", "error", token.line, token.column, _end(token)))
                for index in range(len(tag_stack) - 1, -1, -1):
                    if tag_stack[index].value.lower() == token.value.lower():
                        for unclosed in tag_stack[index + 1:]:
                            findings.append(Finding("HTML-UNCLOSED", f"La etiqueta '{unclosed.value}' no esta cerrada.", "structure", "error", unclosed.line, unclosed.column, _end(unclosed)))
                        del tag_stack[index:]
                        break
    for token in tag_stack:
        findings.append(Finding("HTML-UNCLOSED", f"La etiqueta '{token.value}' no esta cerrada.", "structure", "error", token.line, token.column, _end(token)))

    open_tags: list[AstNode] = []
    seen_ids: set[str] = set()

    def visit(node: AstNode) -> None:
        if node.node_type != "element":
            for child in node.children:
                visit(child)
            return
        if open_tags and open_tags[-1].name == "p" and node.name in {"div", "section", "article", "p"}:
            findings.append(Finding("HTML-NESTING", f"'{node.name}' no puede anidarse dentro de 'p'.", "structure", "error", node.line, node.column, node.column + len(node.name)))
        open_tags.append(node)
        if node.name == "html" and len(open_tags) > 1:
            findings.append(Finding("HTML-NESTING", "La etiqueta html debe ser la raiz del documento.", "structure", "error", node.line, node.column, node.column + len(node.name)))
        if "id" in node.attributes and node.attributes["id"]:
            identifier = node.attributes["id"].strip("\"'")
            if identifier in seen_ids:
                attr = node.attribute_tokens["id"]
                findings.append(Finding("HTML-DUPLICATE-ID", f"El id '{identifier}' esta duplicado.", "logic", "error", attr.line, attr.column, _end(attr)))
            seen_ids.add(identifier)
        for attr in node.attributes:
            if not any(attr == allowed or (allowed.endswith("*") and attr.startswith(allowed[:-1])) for allowed in ALLOWED_ATTRIBUTES):
                attr_token = node.attribute_tokens[attr]
                findings.append(Finding("HTML-ATTRIBUTE", f"Atributo '{attr}' no reconocido para este prototipo.", "logic", "warning", attr_token.line, attr_token.column, _end(attr_token)))
        for child in node.children:
            visit(child)
        open_tags.pop()

    visit(parsed.root)
    for token in parsed.tokens:
        if token.kind == "invalid":
            findings.append(Finding("HTML-TOKEN", "Token HTML invalido.", "syntax", "error", token.line, token.column, _end(token)))
        if token.kind == "invalid_attribute_value":
            findings.append(Finding("HTML-QUOTE", "Valor de atributo sin comillas balanceadas.", "syntax", "error", token.line, token.column, _end(token)))
    return findings


def run_syntax_rules(parsed: ParseResult) -> list[Finding]:
    findings: list[Finding] = []
    for script in parsed.scripts:
        stack: list[Token] = []
        for token in script.tokens:
            if token.kind in {"invalid", "unterminated_string"}:
                message = "Token JavaScript invalido." if token.kind == "invalid" else "Cadena JavaScript sin cerrar."
                findings.append(Finding("JS-TOKEN" if token.kind == "invalid" else "JS-QUOTE", message, "syntax", "error", token.line, token.column, _end(token)))
            if token.value in "{[(":
                stack.append(token)
            elif token.value in "}])":
                expected = {"}": "{", "]": "[", ")": "("}[token.value]
                if not stack or stack[-1].value != expected:
                    findings.append(Finding("JS-BALANCE", f"Cierre '{token.value}' sin apertura correspondiente.", "syntax", "error", token.line, token.column, _end(token)))
                else:
                    stack.pop()
        for opening in stack:
            findings.append(Finding("JS-BALANCE", f"'{opening.value}' sin cerrar.", "syntax", "error", opening.line, opening.column, _end(opening)))
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
                findings.append(Finding("JS-UNDECLARED", f"Variable '{token.value}' usada sin declaracion visible.", "logic", "warning", token.line, token.column, _end(token)))
    return findings
