# ==============================================================================
# src/dax_copilot/agent/__init__.py — Módulo do Agente
# ==============================================================================
#
# Exporta a função principal de criação do agente para uso em outras partes
# do projeto. Isso permite importações limpas como:
#
#   from dax_copilot.agent import create_agent
#
# ==============================================================================

from dax_copilot.agent.core import create_agent

__all__ = ["create_agent"]
