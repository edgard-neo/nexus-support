# 🤖 NexusSupport — AI Customer Support Agent

> Agente inteligente de suporte ao cliente para e-commerce, construído com LangGraph, LangChain v1, RAG e FastAPI.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-v1.2-green)](https://docs.langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-v1.0-green)](https://docs.langchain.com/oss/python/langgraph/overview)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/LLM-Groq-orange)](https://groq.com)

---

## 📌 O que é

NexusSupport é um agente de suporte ao cliente com IA que:

- 🔍 **Consulta status de pedidos** — o agente busca dados do pedido e responde em linguagem natural
- 📚 **Responde FAQ** via RAG — busca na base de conhecimento da loja antes de responder
- 🧠 **Lembra o contexto** — mantém histórico da conversa na sessão
- 🔒 **Protege dados do usuário** — PII mascarado antes de qualquer chamada ao LLM
- 🙋 **Escala para humano** — quando não sabe ou a situação é sensível, transfere para atendente

---

## 🏗️ Arquitetura

```mermaid
graph TD
    Usuário[Usuário] --> UI[Gradio UI]
    UI <--> FastAPI[FastAPI /api/v1]

    FastAPI --> Graph[LangGraph Graph]
    Graph --> Router[Router Node]

    Router --> Orders[tools/orders.py]
    Router --> FAQ[tools/faq_retriever.py → ChromaDB]
    Router --> Handoff[tools/handoff.py]

    Graph --> Groq[Groq · llama-3.3-70b]
    Graph --> Memory[SQLite Checkpoint]
    Graph --> LangSmith[LangSmith Tracing]

    subgraph Segurança
        PII[PII Masking]
        Safety[Safety Guardrails]
    end
    Graph -.-> PII
    Graph -.-> Safety
```

---

## 🗂️ Estrutura do projeto

```
nexus-support/
├── app/
│   ├── main.py                    # entrypoint — FastAPI + Gradio mount
│   │
│   ├── core/                      # configurações e utilitários globais
│   │   ├── config.py              # pydantic-settings — variáveis de ambiente
│   │   ├── logging.py             # logging estruturado
│   │   └── prompts/
│   │       └── system.md          # system prompt em arquivo separado
│   │
│   ├── agent/
│   │   ├── graph.py               # LangGraph — orquestrador principal
│   │   ├── state.py               # AgentState — estado compartilhado
│   │   └── tools/
│   │       ├── orders.py          # consulta de pedidos
│   │       ├── faq_retriever.py   # busca no FAQ via RAG
│   │       └── handoff.py         # escalação para humano
│   │
│   ├── rag/
│   │   ├── ingest.py              # indexação do FAQ no ChromaDB
│   │   └── vectorstore.py         # retrieval por similaridade
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   └── chat.py            # endpoints de chat
│   │   ├── schemas.py             # Pydantic request/response models
│   │   └── deps.py                # injeção de dependências
│   │
│   └── security/
│       ├── pii.py                 # mascaramento de dados pessoais
│       └── safety.py              # validação contra prompt injection
│
├── data/
│   └── faq/                       # base de conhecimento da loja
├── tests/
├── .env.example
├── .python-version                # Python 3.12 — padrão uv
├── pyproject.toml
└── README.md
```

---

## 🚀 Como rodar localmente

> Este projeto usa [uv](https://docs.astral.sh/uv/) para gerenciamento de dependências.
> Instale com: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**1. Clone o repositório**

```bash
git clone https://github.com/edgard-neo/nexus-support.git
cd nexus-support
```

**2. Instale as dependências e crie o ambiente**

```bash
uv sync
```

**3. Configure as variáveis de ambiente**

```bash
cp .env.example .env
# Edite o .env com suas chaves
```

**4. Indexe a base de conhecimento**

```bash
uv run python -m app.rag.indexer
```

**5. Inicie a API**

```bash
uv run uvicorn app.api.main:app --reload
```

**6. Acesse a interface**

```
http://localhost:8000
```

---

## 🔌 Endpoints da API

| Método | Rota      | Descrição                |
| ------ | --------- | ------------------------ |
| `POST` | `/chat`   | Envia mensagem ao agente |
| `GET`  | `/health` | Status da API            |
| `GET`  | `/docs`   | Swagger UI automático    |

**Exemplo de request:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user_123", "message": "Qual o status do meu pedido #4521?"}'
```

**Exemplo de response:**

```json
{
  "response": "Seu pedido #4521 está em trânsito e deve chegar em até 2 dias úteis.",
  "escalated": false,
  "session_id": "user_123"
}
```

---

## 🧠 Decisões técnicas

**Por que LangGraph e não chains simples?**
LangGraph permite controle explícito do fluxo — o agente pode pausar, esperar input humano, e retomar. Isso é essencial para o padrão human-in-the-loop em suporte real.

**Por que RAG e não fine-tuning?**
O FAQ da loja muda com frequência. RAG permite atualizar a base de conhecimento sem retreinar o modelo — mais rápido, mais barato e mais flexível.

**Por que Groq?**
Latência sub-segundo em respostas. Para suporte ao cliente, tempo de resposta é UX crítica.

**Por que Sentence Transformers local para embeddings?**
Zero custo, zero limite de requisições, dados nunca saem da máquina.

---

## 🔒 Segurança

- PII (CPF, email, telefone, cartão) mascarado antes de qualquer chamada ao LLM
- Validação de input contra prompt injection
- API keys via variáveis de ambiente — nunca no código
- Dados de sessão não persistem entre reinicializações por padrão

---

## 🗺️ Roadmap

- [x] Estrutura do projeto
- [ ] RAG pipeline — indexação e retrieval do FAQ
- [ ] Tools — consulta de pedidos, FAQ, escalação
- [ ] LangGraph agent — orquestrador com estado
- [ ] Middleware — PII e safety
- [ ] FastAPI — endpoints REST
- [ ] Interface Gradio
- [ ] Testes automatizados
- [ ] Deploy no Hugging Face Spaces

---

## 👨‍💻 Autor

**Edgard Mendes** — AI Engineer em formação
[GitHub](https://github.com/edgard-neo) · [LinkedIn](https://www.linkedin.com/in/codewithedgard/)

---

## 📄 Licença

MIT — use, modifique e distribua livremente.
