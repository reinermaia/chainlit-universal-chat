# Chainlit Universal Chat (PostgreSQL + Pluggable LLM) 🚀

Um template completo e pronto para produção para executar um chat com LLM com persistência total do histórico de conversas, compatível tanto com **LLMs 100% locais (Ollama)** quanto com **Gateways Corporativos e OpenAI**.

---

## ✨ Funcionalidades

- **Provedor de LLM Plugável:** Compatível com qualquer endpoint com especificação OpenAI (`/chat/completions`), incluindo **Ollama local**, **OpenAI oficial**, **LiteLLM**, **vLLM** e **Gateways corporativos (ex: tribunais, empresas)**.
- **Histórico Persistente (Sidebar):** Suporte completo à barra lateral de conversas passadas usando `SQLAlchemyDataLayer` e PostgreSQL.
- **Banco de Dados Zero-Config:** `docker-compose.yml` pré-configurado que inicializa o schema do banco automaticamente no primeiro start.
- **Correção de Persistência Chainlit 2.10+:** O `schema.sql` já inclui a coluna `"autoCollapse"` na tabela `steps`, evitando que o step interno do Chainlit falhe e faça mensagens desaparecerem.
- **Suporte a PDFs:** Extração automática de texto de arquivos PDF anexados diretamente no chat.
- **Suporte a Redes Corporativas / Proxies:** Configuração opcional `LLM_VERIFY_SSL=false` para ambientes protegidos com inspeção SSL / proxy corporativo.
- **Autenticação Local:** Proteção simples por usuário e senha para habilitar a gestão de threads por usuário.

---

## 📋 Pré-requisitos

1. **Python 3.10+** instalado.
2. **Docker e Docker Compose** (ex: Docker Desktop).
3. **Provedor de LLM:**
   - **Opção local:** Ollama instalado (ex: `ollama run qwen3-cpre:latest` ou `llama3`).
   - **Opção remota:** Uma URL base, chave de API e modelo de qualquer servidor compatível com OpenAI.

---

## 🛠️ Instalação e Uso Passo a Passo

### 1. Clonar o repositório
```bash
git clone <url-do-seu-repositorio>
cd <pasta-do-projeto>
```

### 2. Configurar as variáveis de ambiente
Copie o arquivo de exemplo para `.env`:
```bash
cp .env.example .env
```
Gere uma chave secreta para a sessão:
```bash
chainlit create-secret
```
Abra o `.env` e configure:
- `CHAINLIT_AUTH_SECRET`: cole a chave gerada acima.
- `CHAINLIT_LOCAL_USER`: seu usuário de login.
- `CHAINLIT_LOCAL_PASSWORD`: sua senha de login.
- **Configuração do LLM:**
  - Para **Ollama local**:
    ```env
    LLM_BASE_URL=http://localhost:11434/v1
    LLM_API_KEY=ollama
    LLM_MODEL=seu-modelo-aqui
    ```
  - Para **Gateway Corporativo / OpenAI**:
    ```env
    LLM_BASE_URL=https://seu-gateway-llm.com/v1
    LLM_API_KEY=sua-chave-aqui
    LLM_MODEL=seu-modelo-aqui
    # Se estiver em rede corporativa com proxy SSL:
    # LLM_VERIFY_SSL=false
    ```

### 3. Iniciar o PostgreSQL via Docker
```bash
docker compose up -d
```
*(O banco inicializa na porta `5432` e o schema é carregado automaticamente pelo script em `schema.sql`).*

### 4. Instalar as dependências Python
```bash
pip install -r requirements.txt
```

### 5. Iniciar a aplicação
```bash
chainlit run app.py -w
```
Acesse no seu navegador: **`http://localhost:8000`** e faça login com as credenciais configuradas no `.env`.

---

## 🔍 Resolução do Bug de Histórico do Chainlit

Se você já utilizou o Chainlit com `SQLAlchemyDataLayer` e notou que as respostas da IA sumiam ao reabrir uma conversa antiga, isso ocorre porque desde a versão `2.10.0` o Chainlit adicionou o campo `"autoCollapse"` no objeto `Step`, mas a documentação oficial esqueceu de incluir essa coluna no `schema.sql`.

Este repositório resolve isso de ponta a ponta:
- O `schema.sql` já traz a coluna `"autoCollapse" BOOLEAN` definida.
- O arquivo `query.sql` contém comandos utilitários para recuperar threads legadas se necessário.

---

## 📄 Licença
Distribuído sob a licença MIT. Sinta-se livre para usar e customizar!