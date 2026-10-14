"""Pipeline público que combina lexing, parsing y grafo de reglas."""

from dataclasses import dataclass
from .parser import parse_html
from .rules import Finding, run_logic_rules, run_structure_rules, run_syntax_rules


@dataclass(slots=True)
class AnalysisResult:
    """Agrupa los hallazgos y las métricas producidas por un análisis.

    Attributes:
        findings: Hallazgos ordenados por posición y capa.
        tokens: Total de tokens HTML y JavaScript procesados.
        scripts: Cantidad de bloques `script` encontrados.
        elapsed_ms: Tiempo del análisis en milisegundos.
    """

    findings: list[Finding]
    tokens: int
    scripts: int
    elapsed_ms: float = 0.0

    def as_dict(self) -> dict:
        """Convierte el resultado a un diccionario serializable a JSON."""
        return {"findings": [finding.as_dict() for finding in self.findings], "tokens": self.tokens, "scripts": self.scripts, "elapsed_ms": round(self.elapsed_ms, 2), "summary": {"total": len(self.findings), "structure": sum(item.layer == "structure" for item in self.findings), "syntax": sum(item.layer == "syntax" for item in self.findings), "logic": sum(item.layer == "logic" for item in self.findings)}}


def analyze(source: str) -> AnalysisResult:
    """Analiza HTML y JavaScript embebido y ordena sus hallazgos por ubicacion.

    Args:
        source: Documento HTML que se va a analizar.

    Returns:
        Resultado con hallazgos, conteos y tiempo transcurrido.
    """
    import time
    started = time.perf_counter()
    parsed = parse_html(source)
    findings = run_structure_rules(parsed) + run_syntax_rules(parsed) + run_logic_rules(parsed)
    findings.sort(key=lambda item: (item.line, item.column, item.layer))
    return AnalysisResult(findings, len(parsed.tokens) + sum(len(script.tokens) for script in parsed.scripts), len(parsed.scripts), (time.perf_counter() - started) * 1000)
