# ==============================================================================
# src/dax_copilot/tools/__init__.py — Pacote de Ferramentas do Agente
# ==============================================================================
#
# Este pacote contém as ferramentas customizadas que estendem as capacidades
# do agente DAX Copilot.
#
# Ferramentas disponíveis:
#   - schema_parser: Lê e parseia esquemas de dados de arquivos CSV/Excel
#     🔒 Barreira de segurança LGPD/GDPR — extrai APENAS metadados
#
# ==============================================================================

from dax_copilot.tools.schema_parser import (
    extract_safe_schema,
    format_schema_for_context,
    parse_schema,
)

__all__ = ["extract_safe_schema", "format_schema_for_context", "parse_schema"]
