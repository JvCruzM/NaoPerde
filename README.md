# 🍲 NãoPerde

**Menos desperdício, mais aproveitamento.** O NãoPerde é um sistema de gerenciamento doméstico de alimentos com um assistente de IA para ajudar a acompanhar o estoque, observar datas de validade e aproveitar ingredientes.

## Funcionalidades

- Cadastro, edição e exclusão de alimentos.
- Registro de quantidade, unidade, categoria e data de validade.
- Controle de alimentos disponíveis, consumidos e descartados.
- Painel com resumo do estoque e alertas de validade.
- Assistente integrado à API do Groq, com contexto do estoque disponível.
- Histórico de conversas persistido em JSON.
- Testes automatizados com Pytest.

## Tecnologias

- Python
- Streamlit
- Groq API
- JSON
- python-dotenv
- Pytest

## Requisitos

Python 3.12 ou superior e uma chave da API Groq para utilizar o chat inteligente. O gerenciamento do estoque funciona mesmo sem a chave configurada.

## Instalação

```bash
git clone https://github.com/JvCruzM/NaoPerde.git
cd NaoPerde
python -m venv venv
```

No Windows PowerShell, ative o ambiente:

```powershell
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração do Groq

Crie um arquivo `.env` na raiz do projeto, usando `.env.example` como referência:

```env
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=openai/gpt-oss-20b
```

Nunca publique o arquivo `.env` nem compartilhe sua chave de API. O `.gitignore` já deve mantê-lo fora do versionamento.

## Executar a aplicação

Na raiz do projeto, com o ambiente virtual ativado:

```bash
streamlit run app.py
```

A aplicação possui três áreas: **Visão geral**, **Meu estoque** e **Assistente IA**. Os dados do estoque e das conversas ficam na pasta `data/`.

## Executar os testes

```bash
python -m pytest -v
```

## Estrutura principal

```text
NaoPerde/
├── app.py
├── data/
│   ├── inventory.json
│   └── conversations.json  # criado automaticamente
├── src/
│   ├── agent.py
│   ├── conversations.py
│   ├── expiration.py
│   ├── inventory.py
│   ├── prompts.py
│   └── recipes.py
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Observação sobre validade e segurança alimentar

A data cadastrada não garante, por si só, que um alimento esteja próprio para consumo. Considere também as condições de armazenamento, a integridade da embalagem e sinais de deterioração. Alimentos com data expirada ou sinais de deterioração não devem ser recomendados pelo assistente.

---

**NãoPerde — tecnologia a favor do consumo consciente.**
