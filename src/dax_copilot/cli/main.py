# ==============================================================================
# src/dax_copilot/cli/main.py — Entry Point CLI do DAX Copilot
# ==============================================================================
#
# Interface de linha de comando interativa para o agente DAX Copilot.
# Permite conversar com o agente diretamente no terminal, com suporte a:
#
#   /schema <caminho>  → Carrega um arquivo CSV/Excel como esquema de dados
#   /ver               → Mostra o esquema de dados atualmente carregado
#   /limpar            → Remove o esquema carregado e reinicia o agente
#   /ajuda             → Lista todos os comandos disponíveis
#   /sair              → Encerra o programa
#
# O output é formatado com a biblioteca Rich para uma experiência visual
# agradável no terminal.
#
# ==============================================================================

import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from dax_copilot.agent import create_agent
from dax_copilot.tools import format_schema_for_context, parse_schema

# ── Carrega variáveis de ambiente (.env) ────────────────────────────────
load_dotenv()

# ── Console Rich para output formatado ──────────────────────────────────
console = Console()


# =====================================================================
# BANNER — Tela de boas-vindas exibida ao iniciar o programa
# =====================================================================
BANNER = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]                                                              [bold cyan]║[/]
[bold cyan]║[/]   [bold white]🧠 DAX Copilot — Context-Aware AI Agent[/]                    [bold cyan]║[/]
[bold cyan]║[/]   [dim]Especialista em Power BI • DAX • Power Query[/]              [bold cyan]║[/]
[bold cyan]║[/]   [dim]Powered by Agno + Google Gemini[/]                            [bold cyan]║[/]
[bold cyan]║[/]                                                              [bold cyan]║[/]
[bold cyan]╚══════════════════════════════════════════════════════════════╝[/]
"""

HELP_TEXT = """
[bold yellow]📌 Comandos disponíveis:[/]

  [bold green]/schema <caminho>[/]  → Carrega um arquivo CSV/Excel como esquema de dados
  [bold green]/ver[/]               → Mostra o esquema de dados atualmente carregado
  [bold green]/limpar[/]            → Remove o esquema e reinicia o agente
  [bold green]/ajuda[/]             → Mostra esta mensagem de ajuda
  [bold green]/sair[/]              → Encerra o programa

[dim]💡 Dica: Carregue um esquema primeiro para que o agente conheça seus dados![/]
"""


def main() -> None:
    """
    Função principal — Inicia o loop interativo do DAX Copilot no terminal.

    O fluxo é:
    1. Exibe banner de boas-vindas
    2. Cria o agente (sem esquema inicialmente)
    3. Entra em loop infinito aguardando input do usuário
    4. Processa comandos (/) ou envia perguntas ao agente
    5. Exibe a resposta formatada no terminal
    """
    console.print(BANNER)
    console.print(HELP_TEXT)

    # ── Estado da sessão ────────────────────────────────────────────────
    schema_text: str | None = None     # Texto do esquema carregado
    agent = create_agent()             # Agente inicial (sem esquema)

    # ── Loop principal ──────────────────────────────────────────────────
    while True:
        try:
            # Prompt de input do usuário
            console.print()
            user_input = console.input("[bold cyan]🧑 Você → [/]").strip()

            # Ignora inputs vazios
            if not user_input:
                continue

            # ── Comandos especiais (começam com /) ──────────────────────

            # /sair — Encerra o programa
            if user_input.lower() in ("/sair", "/exit", "/quit"):
                console.print(
                    "\n[bold cyan]👋 Até logo! Boas análises![/]\n"
                )
                sys.exit(0)

            # /ajuda — Mostra comandos disponíveis
            if user_input.lower() in ("/ajuda", "/help"):
                console.print(HELP_TEXT)
                continue

            # /ver — Mostra esquema carregado
            if user_input.lower() in ("/ver", "/show"):
                if schema_text:
                    console.print(
                        Panel(
                            schema_text,
                            title="📊 Esquema Carregado",
                            border_style="green",
                        )
                    )
                else:
                    console.print(
                        "[yellow]⚠️  Nenhum esquema carregado. "
                        "Use /schema <caminho> para carregar.[/]"
                    )
                continue

            # /limpar — Remove esquema e reinicia agente
            if user_input.lower() in ("/limpar", "/clear"):
                schema_text = None
                agent = create_agent()
                console.print(
                    "[green]✅ Esquema removido e agente reiniciado.[/]"
                )
                continue

            # /schema <caminho> — Carrega esquema de dados
            if user_input.lower().startswith("/schema"):
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    console.print(
                        "[yellow]⚠️  Uso: /schema <caminho_do_arquivo>[/]\n"
                        "[dim]Exemplo: /schema data/sample_schema.csv[/]"
                    )
                    continue

                file_path = parts[1].strip()
                try:
                    with console.status(
                        "[cyan]📂 Lendo esquema de dados...[/]"
                    ):
                        schema_text = parse_schema(file_path)
                        schema_context = format_schema_for_context(schema_text)
                        agent = create_agent(schema_context=schema_context)

                    console.print(
                        f"[green]✅ Esquema carregado com sucesso: "
                        f"[bold]{file_path}[/bold][/]"
                    )
                    console.print(
                        Panel(
                            schema_text,
                            title="📊 Esquema Carregado",
                            border_style="green",
                        )
                    )
                except (FileNotFoundError, ValueError) as e:
                    console.print(f"[red]{e}[/]")
                continue

            # ── Enviar pergunta ao agente ───────────────────────────────
            console.print()
            with console.status("[cyan]🧠 Pensando...[/]"):
                response = agent.run(user_input)

            # Exibe a resposta formatada
            if response and response.content:
                console.print(
                    Panel(
                        Markdown(response.content),
                        title="🤖 DAX Copilot",
                        border_style="cyan",
                        padding=(1, 2),
                    )
                )
            else:
                console.print(
                    "[yellow]⚠️  Não recebi uma resposta do agente. "
                    "Tente reformular sua pergunta.[/]"
                )

        except KeyboardInterrupt:
            console.print(
                "\n\n[bold cyan]👋 Até logo! Boas análises![/]\n"
            )
            sys.exit(0)


# ── Entry point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
