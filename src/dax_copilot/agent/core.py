# ==============================================================================
# src/dax_copilot/agent/core.py — Definição do Agente DAX Copilot
# ==============================================================================
#
# Este módulo cria e configura o agente principal usando o framework Agno.
# O agente é um "Arquiteto de Dados Sênior" especialista em Power BI, DAX
# e Power Query, potencializado pelo modelo Google Gemini.
#
# Arquitetura:
#   - Modelo: Google Gemini (gemini-3.1-flash-lite-preview)
#   - Instruções: importadas de dax_copilot.agent.prompts (separação de concerns)
#   - Ferramentas: parse_schema para leitura de metadados de tabelas
#   - Contexto: esquema de dados injetado dinamicamente na sessão
#
# Uso:
#   from dax_copilot.agent import create_agent
#   agent = create_agent()
#   agent.print_response("Crie uma medida de Total de Vendas")
#
# ==============================================================================

from agno.agent import Agent
from agno.models.google import Gemini

from dax_copilot.agent.prompts import get_all_instructions


def create_agent(schema_context: str | None = None) -> Agent:
    """
    Cria e retorna uma instância configurada do agente DAX Copilot.

    O agente é configurado com:
    - Modelo Google Gemini para geração de respostas
    - Instruções especializadas em DAX/Power Query
    - Contexto de esquema de dados (quando fornecido)

    Args:
        schema_context: Texto do esquema de dados parseado pela ferramenta
                       parse_schema. Se fornecido, é adicionado às instruções
                       do agente para que ele tenha consciência das tabelas
                       e colunas disponíveis.

    Returns:
        Instância do Agent do Agno, pronta para uso.

    Exemplo:
        >>> from dax_copilot.agent import create_agent
        >>> from dax_copilot.tools import parse_schema, format_schema_for_context
        >>>
        >>> schema = parse_schema("dados/vendas.csv")
        >>> contexto = format_schema_for_context(schema)
        >>> agent = create_agent(schema_context=contexto)
        >>> agent.print_response("Qual a receita total?")
    """

    # ── Monta as instruções do agente ───────────────────────────────────
    instructions = get_all_instructions()

    # Se um esquema de dados foi carregado, adiciona ao contexto
    if schema_context:
        instructions.append(
            "\n## ESQUEMA DE DADOS CARREGADO:\n"
            "Use EXATAMENTE estes nomes de tabelas e colunas nas suas respostas.\n"
            f"{schema_context}"
        )
    else:
        instructions.append(
            "\n## ⚠️ NENHUM ESQUEMA CARREGADO:\n"
            "O usuário ainda não carregou nenhum esquema de dados. "
            "Peça educadamente que ele carregue um arquivo CSV ou Excel "
            "para que você possa gerar código DAX/Power Query preciso."
        )

    # ── Criação do Agente ───────────────────────────────────────────────
    agent = Agent(
        name="DAX Copilot",
        model=Gemini(id="gemini-3.1-flash-lite-preview"),
        instructions=instructions,
        markdown=True,                   # Respostas em Markdown formatado
        add_datetime_to_context=True,    # Agente sabe a data/hora atual
        # Nota: A memória conversacional é gerenciada manualmente pelo
        # app.py (via _build_history_context), pois o Agno não possui
        # storage backend configurado nesta versão.
    )

    return agent
