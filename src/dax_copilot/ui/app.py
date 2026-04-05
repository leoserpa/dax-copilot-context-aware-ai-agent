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
def cached_parse_schema(file_paths: tuple[str, ...], total_size: int) -> str:
    """Wrapper com cache do Streamlit sobre parse_schema."""
    return parse_schema(list(file_paths))


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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Tipografia e Fundo Global ──────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* As cores globais serão herdadas do tema adaptativo Light/Dark do Streamlit */

    /* ── Header personalizado (Glassmorphism Adaptativo) ────────── */
    .main-header {
        background: rgba(128, 128, 128, 0.08); /* Fundo neutro que funciona em Light e Dark */
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 2rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08);
    }
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: var(--text-color);
        opacity: 0.75;
        margin: 0.5rem 0 0 0;
        font-size: 1.05rem;
        font-weight: 500;
    }

    /* ── Sidebar Glassmorphism Adaptativo ───────────────────────── */
    [data-testid="stSidebar"] {
        background: rgba(128, 128, 128, 0.05) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(128, 128, 128, 0.15);
    }

    /* ── Chat Messages Adaptativo ───────────────────────────────── */
    .stChatMessage {
        background: rgba(128, 128, 128, 0.05); /* Fundo com opacidade neutra */
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stChatMessage:hover {
        background: rgba(128, 128, 128, 0.10);
    }

    /* ── Esquema card Adaptativo ────────────────────────────────── */
    .schema-card {
        background: rgba(128, 128, 128, 0.08); /* Fundo neutro */
        border-left: 4px solid #8b5cf6;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: inherit; /* Segue Dark/Light automático do Streamlit */
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }

    /* ── Status badge ───────────────────────────────────────────── */
    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .status-loaded {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    .status-empty {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    /* ── Botões (Pill-shaped) ───────────────────────────────────── */
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        background: rgba(139, 92, 246, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: rgba(139, 92, 246, 0.15) !important;
        border: 1px solid rgba(139, 92, 246, 0.8) !important;
        transform: translateY(-2px);
    }
    
    /* Input do Chat Adaptativo */
    .stChatInputContainer {
        border-radius: 16px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background: rgba(128, 128, 128, 0.08);
        backdrop-filter: blur(10px);
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

    # ── Upload de arquivos múltiplos ────────────────────────────────
    uploaded_files = st.file_uploader(
        "Carregar arquivo de dados (Star Schema Multi-arquivos suportado)",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        help="O agente lerá a estrutura e criará os relacionamentos dos arquivos selecionados.",
        key=f"file_uploader_{st.session_state.uploader_key}",
    )

    if uploaded_files:
        # Verifica se os arquivos mudaram para evitar salvar no disco a cada mensagem enviada no chat
        files_hash = "-".join([f"{uf.name}_{uf.size}" for uf in uploaded_files])
        if st.session_state.get("processed_files_hash") != files_hash:
            temp_paths = []
            total_size = 0
    
            for uf in uploaded_files:
                # Salva os arquivos temporariamente para parsing
                temp_path = ROOT_DIR / "data" / uf.name
                temp_path.parent.mkdir(parents=True, exist_ok=True)
    
                with open(temp_path, "wb") as f:
                    f.write(uf.getbuffer())
                
                temp_paths.append(str(temp_path))
                total_size += temp_path.stat().st_size
    
            try:
                # Usa versão com cache usando tupla em paths pra ser "hashable"
                schema_text = cached_parse_schema(tuple(temp_paths), total_size)
                schema_context = format_schema_for_context(schema_text)
    
                # Atualiza o estado da sessão
                st.session_state.schema_text = schema_text
                st.session_state.agent = create_agent(schema_context=schema_context)
                st.session_state.processed_files_hash = files_hash
    
                st.success(f"✅ Esquema carregado ({len(uploaded_files)} arquivos detectados)")
            except Exception as e:
                st.error(f"❌ Erro ao ler arquivos: {e}")

    # ── Exibição do esquema carregado ───────────────────────────────
    st.markdown("---")

    if st.session_state.schema_text:
        st.markdown(
            '<span class="status-badge status-loaded">📊 Esquema Ativo</span>',
            unsafe_allow_html=True,
        )
        with st.expander("Ver Esquema Raw", expanded=False):
            st.code(st.session_state.schema_text, language=None)
    else:
        st.markdown(
            '<span class="status-badge status-empty">⚠️ Sem esquema</span>',
            unsafe_allow_html=True,
        )
        st.info(
            "Carregue um arquivo acima para construir seu modelo de dados."
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
        - **Versão**: 1.2.0
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
prompt = st.chat_input(
    "Faça sua pergunta sobre DAX, Power Query ou modelagem de dados..."
)

# ── Sugestões Inteligentes (Quick Actions) ──────────────────────────
# Aparece apenas se houver um esquema carregado e a conversa estiver vazia
if st.session_state.schema_text and len(st.session_state.messages) == 0:
    st.markdown("<p style='text-align: center; color: #888; font-size: 0.95rem; margin-top: 1rem; margin-bottom: 0.5rem;'>🎯 <strong>Ações Rápidas de Consultoria:</strong></p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("📐 Estrutura do Modelo & Cardinalidade", use_container_width=True):
        prompt = "Atue como um Arquiteto de Dados Sênior. Analise meu esquema e projete um Star Schema COMPLETO e EXAUSTIVO. Ação Obrigatória: 1) GERE OS SCRIPTS EM LINGUAGEM M (let...in) INDEPENDENTES para CADA TABELA necessária (Fato, Dim_Produtos, Dim_Clientes, Dim_Calendario, Dim_Geografia, etc.). NÃO ECONOMIZE nas tabelas, quero o modelo mais granular e completo possível. 2) Mostre a TABELA DE RELACIONAMENTOS (Origem, Destino, Coluna, Cardinalidade 1:*, Filtro). Instrução: Avise sobre o 'Editor Avançado' em negrito."
    if c2.button("💡 Top 5 KPIs de Elite (Business Insights)", use_container_width=True):
        prompt = "Atue como um Consultor de BI Sênior e Analytics Engineer. Primeiro, identifique o domínio de negócio deste modelo (Vendas, Logística, etc). Sugira os Top 5 KPIs de Elite (nível Diretoria). Para CADA KPI, forneça: 1) Nome e objetivo de negócio, 2) Código DAX PROFISSIONAL (Indentado, usando VAR/RETURN e funções como CALCULATE e DIVIDE), 3) Breve explicação de como esse KPI ajuda na tomada de decisão e 4) Qual visual de Dashboard você recomenda para ele."
    
    c3, c4 = st.columns(2)
    if c3.button("📈 Plano: Storytelling com Dados (Nível Sênior)", use_container_width=True):
        prompt = "Atue como um Consultor de Elite em Data Storytelling baseado EXCLUSIVAMENTE na metodologia de Cole Nussbaumer Knaflic. Analise meu esquema de dados e forneça um Guia Mestre seguindo estes critérios: 1) CONTEXTO: Defina o público (C-Level) e o 'Big Idea' (A frase de impacto). 2) VISUAL DE ELITE: Escolha os gráficos certos e descreva o 'Antes vs Depois' (Como o gráfico júnior seria e como o seu gráfico sênior será). 3) ELIMINAR O CLUTTER: Liste exatamente 5 elementos visuais para EU DELETAR do dashboard agora. 4) FOCO COM CORES: Forneça uma Paleta Profissional (HEX CODES) usando o conceito de 'Mudo vs Destaque' (ex: Tons de Cinza para o geral e Azul/Laranja para o insight). 5) TÍTULOS ATIVOS: Sugira 3 títulos de gráficos que já contam a conclusão (em vez de nomes genéricos). 6) A NARRATIVA: Monte o roteiro da apresentação utilizando o Arco Narrativo (Instigação, Ascensão, Clímax e Resolução)."
    if c4.button("🔐 Governança & Segurança (RLS)", use_container_width=True):
        prompt = "Atue como um Arquiteto de BI e Segurança de Dados Sênior. Analise meu esquema e projete o plano de segurança RLS (Row-Level Security) ideal. 1) Identifique as dimensões sensíveis para filtragem (ex: Região, Departamento, Gerente). 2) GERE O CÓDIGO DAX para a regra de segurança profissional usando USERPRINCIPALNAME() ou LOOKUPVALUE(). 3) Forneça o passo a passo técnico de como configurar isso no Desktop e no Service. 4) Explique por que o RLS Dinâmico é superior para este modelo específico em termos de escalabilidade e compliance."

if prompt:
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "avatar": "🧑"}
    )

    # Exibe mensagem do usuário
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # ── Gera resposta do agente ─────────────────────────────────────
    with st.chat_message("assistant", avatar="🤖"):
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
            # Gerador para processar pedaço por pedaço e dar a sensação de velocidade
            def stream_agent_response():
                for chunk in st.session_state.agent.run(full_prompt, stream=True):
                    if chunk and chunk.content:
                        yield chunk.content
                        
            # Escreve a resposta na tela enquanto ela é gerada
            full_response = st.write_stream(stream_agent_response())

            if full_response:
                # Adiciona resposta ao histórico
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": full_response,
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
