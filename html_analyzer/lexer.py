"""Tokenizadores pequeños y tolerantes para HTML5 y JavaScript."""

from dataclasses import dataclass
from bisect import bisect_right
from functools import lru_cache
import re


@dataclass(slots=True)
class Token:
    kind: str
    value: str
    line: int
    column: int
    offset: int
    end: int

    def location(self) -> dict[str, int]:
        return {"line": self.line, "column": self.column}


@lru_cache(maxsize=8)
def _line_starts(source: str) -> tuple[int, ...]:
    return (0, *(index + 1 for index, char in enumerate(source) if char == "\n"))


def _position(source: str, offset: int) -> tuple[int, int]:
    starts = _line_starts(source)
    line_index = bisect_right(starts, offset) - 1
    return line_index + 1, offset - starts[line_index] + 1


def _token(kind: str, value: str, source: str, start: int, end: int) -> Token:
    line, column = _position(source, start)
    return Token(kind, value, line, column, start, end)


def tokenize_html(source: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    text_start = 0
    length = len(source)
    while index < length:
        if source.startswith("<!--", index):
            if text_start < index:
                tokens.append(_token("text", source[text_start:index], source, text_start, index))
            end = source.find("-->", index + 4)
            end = length if end < 0 else end + 3
            tokens.append(_token("comment", source[index:end], source, index, end))
            index = end
            text_start = index
            continue
        if source[index] != "<":
            index += 1
            continue
        if text_start < index:
            tokens.append(_token("text", source[text_start:index], source, text_start, index))
        if source.startswith("<!DOCTYPE", index) or source.startswith("<!doctype", index):
            end = source.find(">", index + 2)
            end = length if end < 0 else end + 1
            tokens.append(_token("doctype", source[index:end], source, index, end))
            index = end
            text_start = index
            continue
        end = _find_tag_end(source, index + 1)
        end = length if end < 0 else end + 1
        raw = source[index:end]
        match = re.match(r"<\s*(/?)\s*([A-Za-z][\w:-]*)", raw)
        if not match:
            tokens.append(_token("invalid", raw, source, index, end))
        else:
            closing, name = match.groups()
            tokens.append(_token("tag_close" if closing else "tag_open", name, source, index, end))
            body_start = match.end()
            body = raw[body_start:-1] if raw.endswith(">") else raw[body_start:]
            if body.rstrip().endswith("/"):
                body = body.rstrip()[:-1]
            for attr in _attribute_tokens(body, source, index + body_start):
                tokens.append(attr)
            tokens.append(_token("tag_end", raw[-1:] or ">", source, end - 1, end))
        index = end
        text_start = index
    if text_start < length:
        tokens.append(_token("text", source[text_start:], source, text_start, length))
    return tokens


def _find_tag_end(source: str, start: int) -> int:
    quote = ""
    for index in range(start, len(source)):
        char = source[index]
        if quote:
            if char == quote:
                quote = ""
            elif char == ">":
                return index
        elif char in "\"'":
            quote = char
        elif char == ">":
            return index
    return -1


def _attribute_tokens(body: str, source: str, absolute_start: int) -> list[Token]:
    tokens: list[Token] = []
    pattern = re.compile(r"([:\w-]+)(?:\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s]+))?")
    for match in pattern.finditer(body):
        name_start = absolute_start + match.start(1)
        tokens.append(_token("attribute", match.group(1), source, name_start, absolute_start + match.end(1)))
        value = match.group(2)
        if value:
            value_start = absolute_start + match.start(2)
            kind = "attribute_value" if value[:1] in "\"'" and value[-1:] == value[:1] else "invalid_attribute_value"
            tokens.append(_token(kind, value, source, value_start, absolute_start + match.end(2)))
    return tokens


_JS_MULTI = ("===", "!==", "=>", "==", "!=", "<=", ">=", "++", "--", "&&", "||", "+=", "-=", "**")


def tokenize_js(source: str, offset: int = 0, position_source: str | None = None) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
            continue
        start = index
        if source.startswith("//", index):
            end = source.find("\n", index)
            index = len(source) if end < 0 else end
            tokens.append(_token("comment", source[start:index], position_source or source, offset + start, offset + index))
            continue
        if source.startswith("/*", index):
            end = source.find("*/", index + 2)
            index = len(source) if end < 0 else end + 2
            tokens.append(_token("comment", source[start:index], position_source or source, offset + start, offset + index))
            continue
        if char in "'\"`":
            quote = char
            index += 1
            escaped = False
            while index < len(source):
                if escaped:
                    escaped = False
                elif source[index] == "\\":
                    escaped = True
                elif source[index] == quote:
                    index += 1
                    break
                elif source[index] == "\n" and quote != "`":
                    break
                index += 1
            kind = "string" if index <= len(source) and source[index - 1:index] == quote else "unterminated_string"
            tokens.append(_token(kind, source[start:index], position_source or source, offset + start, offset + index))
            continue
        match = re.match(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", source[index:])
        if match:
            index += len(match.group(0))
            tokens.append(_token("number", source[start:index], position_source or source, offset + start, offset + index))
            continue
        match = re.match(r"[A-Za-z_$][\w$]*", source[index:])
        if match:
            index += len(match.group(0))
            tokens.append(_token("keyword" if match.group(0) in {"var", "let", "const", "function", "if", "else", "return", "for", "while", "true", "false", "null"} else "identifier", source[start:index], position_source or source, offset + start, offset + index))
            continue
        operator = next((item for item in _JS_MULTI if source.startswith(item, index)), None)
        if operator:
            index += len(operator)
            tokens.append(_token("operator", operator, position_source or source, offset + start, offset + index))
            continue
        if char in "{}()[].,;:+-*/%=!?<>":
            index += 1
            kind = "delimiter" if char in "{}()[].,;" else "operator"
            tokens.append(_token(kind, char, position_source or source, offset + start, offset + index))
            continue
        index += 1
        tokens.append(_token("invalid", char, position_source or source, offset + start, offset + index))
    return tokens
