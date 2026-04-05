# ==============================================================================
# src/dax_copilot/tools/schema_parser.py — Barreira de Segurança + Metadados
# ==============================================================================
#
# ⚠️  MÓDULO CRÍTICO DE SEGURANÇA — LGPD / GDPR COMPLIANCE
#
# Este módulo é a BARREIRA DE SEGURANÇA do projeto. Ele garante que NENHUMA
# linha de dados reais (PII, dados sensíveis, informações pessoais) seja
# enviada para APIs externas de LLM (Google Gemini, OpenAI, etc.).
#
# O que ENTRA: DataFrame com dados reais do usuário (lido localmente)
# O que SAI:   Apenas uma string de texto com o "esqueleto" (metadados):
#              - Nome sugerido da tabela (baseado no nome do arquivo)
#              - Lista de colunas com tipos de dados simplificados
#              - Contagem de linhas e colunas (métricas agregadas, não dados)
#
# O que NUNCA SAI:
#              ❌ Nenhuma amostra de linha
#              ❌ Nenhum valor individual de célula
#              ❌ Nenhum dado que permita identificação de indivíduos
#
# PRINCÍPIO: O DataFrame original é destruído (del + gc.collect) após a
# extração dos metadados, garantindo que não permaneça em memória.
#
# ==============================================================================

import gc
from pathlib import Path

import pandas as pd


# ── Mapeamento de tipos Pandas → Tipos simplificados para o LLM ────────
# Traduz os dtypes técnicos do Pandas para nomes amigáveis que o LLM
# consegue interpretar para gerar código DAX/Power Query correto.
_DTYPE_MAP: dict[str, str] = {
    "int8": "Número Inteiro",
    "int16": "Número Inteiro",
    "int32": "Número Inteiro",
    "int64": "Número Inteiro",
    "uint8": "Número Inteiro",
    "uint16": "Número Inteiro",
    "uint32": "Número Inteiro",
    "uint64": "Número Inteiro",
    "float16": "Número Decimal",
    "float32": "Número Decimal",
    "float64": "Número Decimal",
    "bool": "Booleano",
    "boolean": "Booleano",
    "datetime64[ns]": "Data/Hora",
    "timedelta64[ns]": "Duração",
    "category": "Categoria",
    "object": "Texto",
    "string": "Texto",
}


def _simplify_dtype(dtype: str) -> str:
    """
    Converte um dtype do Pandas para um tipo simplificado e legível.

    Prioriza o mapeamento exato; se não encontrar, aplica regras genéricas
    para cobrir variações como 'datetime64[ns, UTC]' ou 'Int64' (nullable).

    Args:
        dtype: String do dtype do Pandas (ex: 'int64', 'object', 'datetime64[ns]')

    Returns:
        Tipo simplificado em Português (ex: 'Número Inteiro', 'Texto', 'Data/Hora')
    """
    dtype_str = str(dtype).lower()

    # Busca exata no mapeamento
    if dtype_str in _DTYPE_MAP:
        return _DTYPE_MAP[dtype_str]

    # Regras genéricas para variações de dtype
    if "datetime" in dtype_str:
        return "Data/Hora"
    if "timedelta" in dtype_str:
        return "Duração"
    if "int" in dtype_str:
        return "Número Inteiro"
    if "float" in dtype_str or "decimal" in dtype_str:
        return "Número Decimal"
    if "bool" in dtype_str:
        return "Booleano"

    # Fallback seguro — trata como texto
    return "Texto"


# =====================================================================
# FUNÇÃO PRINCIPAL — Barreira de Segurança
# =====================================================================

def extract_safe_schema(df: pd.DataFrame, table_name: str = "tabela") -> str:
    """
    🔒 BARREIRA DE SEGURANÇA — Extrai APENAS metadados de um DataFrame.

    Esta função é o ponto central de proteção de dados do projeto.
    Ela recebe um DataFrame com dados reais e retorna SOMENTE uma string
    com a estrutura da tabela (nomes de colunas + tipos), sem nenhum valor
    real de célula, amostra ou dado que permita identificar indivíduos.

    Após extrair os metadados, a função:
    1. Apaga a referência ao DataFrame (`del df`)
    2. Força coleta de lixo (`gc.collect()`) para liberar memória
    3. Retorna apenas a string segura de metadados

    Args:
        df:         DataFrame do Pandas com os dados reais do usuário.
                    ⚠️ Este objeto será DESTRUÍDO após a extração.
        table_name: Nome sugerido para a tabela (geralmente o nome do arquivo
                    sem extensão). Usado na saída para ajudar o LLM a gerar
                    código com o nome correto da tabela.

    Returns:
        String formatada contendo APENAS:
        - Nome sugerido da tabela
        - Quantidade de linhas e colunas (métricas agregadas)
        - Lista de colunas com tipos simplificados
        ❌ NENHUM dado real de linha é incluído.
    """
    # ── ETAPA 1: Extração de metadados (somente estrutura) ──────────
    # Capturamos APENAS informações estruturais — nunca valores de células.
    num_rows = len(df)
    num_cols = len(df.columns)

    # Lista de tuplas (nome_coluna, tipo_simplificado)
    # Nenhum valor real é acessado — apenas df.columns e df[col].dtype
    columns_info: list[tuple[str, str]] = [
        (str(col), _simplify_dtype(df[col].dtype))
        for col in df.columns
    ]

    # ── ETAPA 2: Destruição imediata do DataFrame ───────────────────
    # 🔒 SEGURANÇA: Apagamos o DataFrame da memória ANTES de montar
    # a string de saída. Isso garante que, mesmo em caso de erro
    # posterior, os dados reais não ficam acessíveis.
    del df
    gc.collect()  # Força liberação imediata de memória

    # ── ETAPA 3: Montagem da string segura (somente metadados) ──────
    # A partir daqui, trabalhamos APENAS com as variáveis de metadados
    # extraídas na Etapa 1. O DataFrame original já não existe mais.
    output_lines: list[str] = []

    output_lines.append("═" * 50)
    output_lines.append(f"🔒 ESQUEMA SEGURO — {table_name}")
    output_lines.append("═" * 50)
    output_lines.append("")
    output_lines.append(f"📋 Tabela: {table_name}")
    output_lines.append("─" * 50)
    output_lines.append(f"  Linhas: {num_rows:,} | Colunas: {num_cols}")
    output_lines.append("")

    # Lista de colunas com tipos simplificados
    output_lines.append("  Colunas:")
    max_col_len = max(len(name) for name, _ in columns_info) if columns_info else 0
    for col_name, col_type in columns_info:
        output_lines.append(f"    • {col_name:<{max_col_len}} → {col_type}")

    output_lines.append("")
    output_lines.append("─" * 50)
    output_lines.append("🔒 Nenhum dado real foi incluído neste esquema.")
    output_lines.append("═" * 50)

    return "\n".join(output_lines)


# =====================================================================
# FUNÇÃO DE LEITURA + EXTRAÇÃO SEGURA (Pipeline completo)
# =====================================================================

def parse_schema(file_paths: str | list[str]) -> str:
    """
    Lê um ou mais arquivos CSV/Excel e retorna APENAS os metadados seguros.

    Esta função é o pipeline completo de segurança:
    1. Lê os arquivos localmente com Pandas
    2. Extrai metadados via extract_safe_schema() (barreira de segurança)
    3. O DataFrame é destruído dentro de extract_safe_schema()
    4. Retorna apenas a string segura com todas as tabelas

    ❌ NENHUMA linha de dado real é retornada.

    Args:
        file_paths: Caminho(s) absoluto(s) ou relativo(s) para os arquivos CSV ou Excel.
                    Pode ser uma string (um arquivo) ou uma lista de strings.

    Returns:
        String formatada com metadados seguros de todas as tabelas.

    Raises:
        FileNotFoundError: Se algum arquivo não existir.
        ValueError: Se o formato não for suportado (.csv, .xlsx, .xls).
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    all_schemas: list[str] = []

    for file_path in file_paths:
        path = Path(file_path)

        # ── Validação: arquivo existe? ──────────────────────────────────────
        if not path.exists():
            raise FileNotFoundError(
                f"❌ Arquivo não encontrado: '{file_path}'\n"
                f"   Verifique o caminho e tente novamente."
            )

        # ── Validação: formato suportado? ───────────────────────────────────
        suffix = path.suffix.lower()
        supported_formats = {".csv", ".xlsx", ".xls"}

        if suffix not in supported_formats:
            raise ValueError(
                f"❌ Formato '{suffix}' não suportado no arquivo '{path.name}'.\n"
                f"   Formatos aceitos: {', '.join(supported_formats)}"
            )

        # ── Leitura e extração segura ───────────────────────────────────────
        if suffix == ".csv":
            table_name = path.stem
            # Tenta UTF-8 primeiro; se falhar, usa latin-1 (ISO-8859-1),
            # padrão de arquivos exportados pelo Excel no Windows em Português.
            try:
                df = pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(path, encoding="latin-1")

            # 🔒 Extrai metadados e DESTRÓI o DataFrame
            all_schemas.append(extract_safe_schema(df, table_name=table_name))
            # Nota: df já foi destruído dentro de extract_safe_schema()

        else:
            # Excel → lê cada aba como tabela separada
            excel_file = pd.ExcelFile(path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                # 🔒 Extrai metadados e DESTRÓI o DataFrame de cada aba
                all_schemas.append(extract_safe_schema(df, table_name=sheet_name))

    return "\n\n".join(all_schemas)


def format_schema_for_context(schema_text: str) -> str:
    """
    Envolve o texto do esquema em delimitadores claros para injeção
    no contexto do agente. Isso ajuda o modelo a distinguir claramente
    entre o esquema de dados e a conversa do usuário.

    Args:
        schema_text: Output seguro da função parse_schema().

    Returns:
        String formatada com delimitadores para injeção no contexto.
    """
    return (
        "\n<ESQUEMA_DE_DADOS>\n"
        f"{schema_text}\n"
        "</ESQUEMA_DE_DADOS>\n"
    )
