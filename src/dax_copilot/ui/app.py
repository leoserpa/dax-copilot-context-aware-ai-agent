# ==============================================================================
# src/dax_copilot/ui/app.py — Interface Streamlit do DAX Copilot
# ==============================================================================
#
# Interface web interativa para o agente DAX Copilot, construída com
# Streamlit. Oferece uma experiência visual completa com:
#
#   - Sidebar: Upload de arquivos CSV/Excel para carregar esquema
#   - Chat: Interface de conversação com o agente
#   - Esquema: Visualização do esquema de dados carregado
#
# Para rodar:
#   uv run streamlit run src/dax_copilot/ui/app.py
#
# ==============================================================================

from pathlib import Path

# ── Carrega variáveis de ambiente ANTES de qualquer import local ────────
# Isso garante que GOOGLE_API_KEY esteja no ambiente antes da inicialização
# do Agno/Gemini, evitando erros de "API key not set".
from dotenv import load_dotenv

# ROOT_DIR aponta para a raiz do projeto (3 níveis acima:
# src/dax_copilot/ui/app.py → src/dax_copilot/ui → src/dax_copilot → src → raiz)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env", override=True)

# ── Imports locais (após carregar .env) ─────────────────────────────────
import streamlit as st  # noqa: E402

from dax_copilot.agent import create_agent  # noqa: E402
from dax_copilot.tools import format_schema_for_context, parse_schema  # noqa: E402


# ── Função para construir contexto de histórico de conversa ─────────────
def _build_history_context(messages: list[dict], max_turns: int = 10) -> str:
    """
    Constrói uma string com o histórico recente da conversa.

    Isso resolve o problema de "amnésia" do agente: como o Agno não tem
    storage persistente configurado, cada agent.run() é stateless.
    Esta função injeta as últimas N mensagens como contexto no prompt,
    dando ao agente memória conversacional completa.

    Args:
        messages: Lista de dicts com 'role' e 'content' do session_state.
        max_turns: Número máximo de mensagens recentes a incluir.

    Returns:
        String formatada com o histórico, pronta para injetar no prompt.
    """
    if not messages:
        return ""

    # Pega as últimas N mensagens (exclui a mensagem atual do usuário)
    recent = messages[-max_turns:]

    history_lines = ["\n--- HISTÓRICO DA CONVERSA (para manter contexto) ---"]
    for msg in recent:
        role_label = "Usuário" if msg["role"] == "user" else "Assistente"
        # Limpa possíveis blocos HTML ocultos de sugestões do histórico
        content = msg["content"]
        if "<!-- SUGESTOES:" in content:
            content = content.split("<!-- SUGESTOES:")[0].strip()
        # Trunca mensagens muito longas para economizar tokens
        if len(content) > 500:
            content = content[:500] + "...[truncado]"
        history_lines.append(f"[{role_label}]: {content}")
    history_lines.append("--- FIM DO HISTÓRICO ---\n")

    return "\n".join(history_lines)


# ── Cache nativo do Streamlit para evitar re-leitura do arquivo ─────────
# O @st.cache_data faz o Streamlit guardar o resultado em memória.
# Se o mesmo arquivo for processado novamente, ele retorna instantaneamente
# sem ler o disco nem recriar o DataFrame.
@st.cache_data(show_spinner="📂 Processando esquema...")
def cached_parse_schema(file_path: str, file_size: int) -> str:
    """Wrapper com cache do Streamlit sobre parse_schema.
    O parâmetro file_size serve como chave de invalidação:
    se o arquivo mudar de tamanho, o cache é descartado."""
    return parse_schema(file_path)


# =====================================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================================
st.set_page_config(
    page_title="🧠 DAX Copilot — Context-Aware AI Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# CSS CUSTOMIZADO — Visual premium com tema escuro
# =====================================================================
st.markdown(
    """
    <style>
    /* ── Header personalizado ───────────────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.85);
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }

    /* ── Esquema card ───────────────────────────────────────────── */
    .schema-card {
        background-color: #f0f2f6;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }

    /* ── Status badge ───────────────────────────────────────────── */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-loaded {
        background-color: #d4edda;
        color: #155724;
    }
    .status-empty {
        background-color: #fff3cd;
        color: #856404;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================================
# HEADER
# =====================================================================
st.markdown(
    """
    <div class="main-header">
        <h1>🧠 DAX Copilot — Context-Aware AI Agent</h1>
        <p>Especialista em Power BI • DAX • Power Query | Powered by Agno + Google Gemini</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================================
# INICIALIZAÇÃO DO SESSION STATE
# =====================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "schema_text" not in st.session_state:
    st.session_state.schema_text = None

if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

# Chave dinâmica para o file_uploader — ao incrementar, o widget é
# recriado do zero, removendo o arquivo selecionado anteriormente.
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


# =====================================================================
# SIDEBAR — Upload de esquema e informações
# =====================================================================
with st.sidebar:
    st.markdown("## 📂 Esquema de Dados")
    st.markdown(
        "Carregue um arquivo **CSV** ou **Excel** com seus dados. "
        "O agente usará os nomes das colunas e tipos de dados para "
        "gerar código DAX/Power Query preciso."
    )

    # ── Upload de arquivo ───────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Carregar arquivo de dados",
        type=["csv", "xlsx", "xls"],
        help="O agente lerá a estrutura (colunas, tipos) do arquivo.",
        key=f"file_uploader_{st.session_state.uploader_key}",
    )

    if uploaded_file is not None:
        # Salva o arquivo temporariamente para parsing
        temp_path = ROOT_DIR / "data" / uploaded_file.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # Usa versão com cache — só lê o arquivo se for novo ou diferente
            schema_text = cached_parse_schema(str(temp_path), temp_path.stat().st_size)
            schema_context = format_schema_for_context(schema_text)

            # Atualiza o estado da sessão
            st.session_state.schema_text = schema_text
            st.session_state.agent = create_agent(schema_context=schema_context)

            st.success(f"✅ Esquema carregado: **{uploaded_file.name}**")
        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo: {e}")

    # ── Exibição do esquema carregado ───────────────────────────────
    st.markdown("---")

    if st.session_state.schema_text:
        st.markdown(
            '<span class="status-badge status-loaded">📊 Esquema Ativo</span>',
            unsafe_allow_html=True,
        )
        with st.expander("Ver esquema carregado", expanded=False):
            st.code(st.session_state.schema_text, language=None)
    else:
        st.markdown(
            '<span class="status-badge status-empty">⚠️ Sem esquema</span>',
            unsafe_allow_html=True,
        )
        st.info(
            "Carregue um arquivo acima para que o agente conheça seus dados."
        )

    # ── Botão de limpar conversa ────────────────────────────────────
    st.markdown("---")
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔄 Resetar Esquema", use_container_width=True):
        st.session_state.schema_text = None
        st.session_state.agent = create_agent()
        # Incrementa a chave do uploader para forçar o Streamlit a
        # recriar o widget vazio, sem o arquivo anterior selecionado.
        st.session_state.uploader_key += 1
        st.rerun()

    # ── Informações sobre o agente ──────────────────────────────────
    st.markdown("---")
    st.markdown("### ℹ️ Sobre o Agente")
    st.markdown(
        """
        - **Modelo**: Google Gemini 3.1 Flash Lite Preview
        - **Framework**: Agno
        - **Especialidades**: DAX, Power Query, Star Schema
        - **Versão**: 1.0.0
        """
    )


# =====================================================================
# ÁREA DE CHAT — Histórico e input do usuário
# =====================================================================

# ── Exibe mensagens anteriores ──────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])

# ── Input do usuário ────────────────────────────────────────────────
if prompt := st.chat_input(
    "Faça sua pergunta sobre DAX, Power Query ou modelagem de dados..."
):
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "avatar": "🧑"}
    )

    # Exibe mensagem do usuário
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # ── Gera resposta do agente ─────────────────────────────────────
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 Pensando..."):
            try:
                # Injeta histórico de conversa para dar memória ao agente
                history_context = _build_history_context(
                    st.session_state.messages[:-1]  # Exclui a msg atual
                )
                full_prompt = (
                    f"{history_context}\n[Pergunta Atual]: {prompt}"
                    if history_context
                    else prompt
                )
                response = st.session_state.agent.run(full_prompt)

                if response and response.content:
                    st.markdown(response.content)
                    # Adiciona resposta ao histórico
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response.content,
                            "avatar": "🤖",
                        }
                    )
                else:
                    error_msg = (
                        "⚠️ Não recebi uma resposta. "
                        "Tente reformular sua pergunta."
                    )
                    st.warning(error_msg)
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_msg,
                            "avatar": "🤖",
                        }
                    )
            except Exception as e:
                error_msg = f"❌ Erro ao processar: {e}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_msg,
                        "avatar": "🤖",
                    }
                )
