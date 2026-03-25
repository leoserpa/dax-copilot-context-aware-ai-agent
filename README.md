# 🧠 DAX Copilot — Context-Aware AI Agent

<div align="center">

**Agente de IA especialista em Power BI, DAX e Power Query**
*Construído com [Agno](https://agno.com) + Google Gemini*

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Agno](https://img.shields.io/badge/Agno-AI_Agent-667eea?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Versão](https://img.shields.io/badge/Versão-1.0.0-984bb4?style=for-the-badge)

[Português](#-sobre-o-projeto) · [English](#-about-the-project)

</div>

---

## 🇧🇷 Sobre o Projeto

O **DAX Copilot** é um agente de IA **context-aware** (consciente do contexto) que atua como um **Arquiteto de Dados Sênior** especializado em:

- 📊 **Power BI** — Modelagem dimensional e boas práticas
- 📐 **DAX** — Medidas otimizadas com variáveis VAR/RETURN
- 🔄 **Power Query (Linguagem M)** — Transformações de dados eficientes
- ⭐ **Star Schema** — Modelagem Fato/Dimensão profissional

### ✨ Funcionalidades

| Feature | Descrição |
|---------|-----------|
| 🧠 **Context-Aware** | Lê seu esquema de dados (CSV/Excel) e usa nomes reais de colunas e tabelas |
| 🔒 **Fidelidade aos Dados** | NUNCA inventa nomes de colunas — usa exatamente o que está no seu arquivo |
| 📝 **Código Limpo** | Gera código DAX/Power Query formatado, indentado e pronto para copiar |
| 💡 **Dicas de Performance** | Sugere otimizações e boas práticas de modelagem |
| 🖥️ **CLI Interativa** | Interface de terminal rica com comandos intuitivos |
| 🌐 **UI Streamlit** | Interface web moderna com upload de arquivos e chat |

### 🛡️ Segurança de Dados e Privacidade (Data Privacy by Design)

Um dos pilares deste projeto é a **segurança absoluta dos dados corporativos**. O DAX Copilot foi construído com uma arquitetura *Zero-Data-Leak*:

- **NUNCA lê seus dados reais:** O agente processa **EXCLUSIVAMENTE METADADOS** (nomes das colunas e tipos de dados).
- **Processamento 100% Local (Client-Side):** Quando você faz o upload de um arquivo, a ferramenta de leitura (`parse_schema`) extrai apenas as cabeçalhos localmente.
- **Nenhuma linha de fatos ou valores financeiros é enviada para a API da LLM (Google Gemini).**
- Totalmente aderente às políticas de privacidade corporativas e LGPD.

### 🛠️ Stack Tecnológica

| Tecnologia | Papel |
|-----------|-------|
| **[Agno](https://agno.com)** | Framework de agente de IA |
| **[Google Gemini](https://ai.google.dev)** | Modelo de linguagem (LLM) |
| **[Streamlit](https://streamlit.io)** | Interface web interativa |
| **[Rich](https://rich.readthedocs.io)** | Output formatado no terminal |
| **[Pandas](https://pandas.pydata.org)** | Parsing de dados CSV/Excel |
| **[uv](https://docs.astral.sh/uv/)** | Gerenciador de pacotes ultrarrápido |

---

### 🚀 Instalação

**Pré-requisitos:**
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) instalado
- Chave de API do [Google AI Studio](https://aistudio.google.com/apikey)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/DAX-Copilot-Context-Aware.git
cd DAX-Copilot-Context-Aware

# 2. Instale as dependências
uv sync

# 3. Configure sua API Key
copy .env.example .env
# Edite o arquivo .env e adicione sua GOOGLE_API_KEY

# 4. Execute!
uv run python main.py          # CLI interativa
uv run streamlit run ui/app.py  # Interface web
```

### 💻 Uso — CLI

```
🧠 DAX Copilot — Context-Aware AI Agent

📌 Comandos disponíveis:
  /schema <caminho>  → Carrega um arquivo CSV/Excel como esquema de dados
  /ver               → Mostra o esquema de dados atualmente carregado
  /limpar            → Remove o esquema e reinicia o agente
  /ajuda             → Mostra ajuda
  /sair              → Encerra o programa

🧑 Você → /schema data/sample_schema.csv
✅ Esquema carregado com sucesso!

🧑 Você → Crie uma medida DAX que calcule a receita total
🤖 DAX Copilot → ...
```

### 🌐 Uso — Streamlit

```bash
uv run streamlit run ui/app.py
```

1. Acesse `http://localhost:8501` no navegador
2. Faça upload do seu arquivo CSV/Excel na sidebar
3. Faça perguntas no chat sobre DAX, Power Query ou modelagem

---

### 📁 Estrutura do Projeto

```
DAX-Copilot-Context-Aware/
├── .env.example          # Template de variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
├── LICENSE               # ⚖️ Licença MIT
├── pyproject.toml        # Dependências do projeto (uv)
├── README.md             # Esta documentação
│
├── agent.py              # 🤖 Definição do agente Agno + Gemini
├── main.py               # 🖥️ Entry point CLI interativa
├── prompts.py            # 📝 System prompt e regras do agente
│
├── tools/
│   ├── __init__.py       # Exportações do pacote
│   └── schema_parser.py  # 📊 Parser de esquema CSV/Excel
│
├── ui/
│   └── app.py            # 🌐 Interface Streamlit
│
└── data/
    └── sample_schema.csv # 📄 Dados de exemplo para testes
```

---

## 🇺🇸 About the Project

**DAX Copilot** is a **context-aware AI agent** that acts as a **Senior Data Architect** specialized in:

- 📊 **Power BI** — Dimensional modeling and best practices
- 📐 **DAX** — Optimized measures with VAR/RETURN variables
- 🔄 **Power Query (M Language)** — Efficient data transformations
- ⭐ **Star Schema** — Professional Fact/Dimension modeling

### ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Context-Aware** | Reads your data schema (CSV/Excel) and uses real column and table names |
| 🔒 **Data Fidelity** | NEVER invents column names — uses exactly what's in your file |
| 📝 **Clean Code** | Generates formatted, indented DAX/Power Query code ready to copy |
| 💡 **Performance Tips** | Suggests optimizations and modeling best practices |
| 🖥️ **Interactive CLI** | Rich terminal interface with intuitive commands |
| 🌐 **Streamlit UI** | Modern web interface with file upload and chat |

### 🛡️ Data Privacy & Security (Zero-Data-Leak)

A core pillar of this project is the **absolute security of corporate data**. The DAX Copilot was built with a *Zero-Data-Leak* architecture:

- **NEVER reads your actual data:** The agent processes **EXCLUSIVELY METADATA** (column names and data types).
- **100% Local Processing:** When you upload a file, the reading tool (`parse_schema`) extracts only the headers locally.
- **No factual rows, financial values, or PII are ever sent to the LLM API (Google Gemini).**
- Fully compliant with corporate privacy policies, GDPR, and LGPD.

### 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/your-user/DAX-Copilot-Context-Aware.git
cd DAX-Copilot-Context-Aware
uv sync

# Configure your API Key
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run!
uv run python main.py          # Interactive CLI
uv run streamlit run ui/app.py  # Web interface
```

---

## 📄 Licença / License

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

This project is distributed under the MIT License. See `LICENSE` for details.

---

<div align="center">
<sub>Feito com 💜 por Leonardo Serpa — Powered by Agno + Google Gemini</sub>
</div>
