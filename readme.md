# Chainlit Local Chat (PostgreSQL + Ollama) 🚀

Um template completo e pronto para produção para executar um chat com LLM **100% local e privado**, utilizando **Chainlit**, **Ollama** e **PostgreSQL** para persistência total do histórico de conversas.

---

## ✨ Funcionalidades

- **100% Local e Privado:** Conectado diretamente ao Ollama local, sem enviar dados para APIs de terceiros.
- **Histórico Persistente (Sidebar):** Suporte completo à barra lateral de conversas passadas usando `SQLAlchemyDataLayer` e PostgreSQL.
- **Banco de Dados Zero-Config:** `docker-compose.yml` pré-configurado que inicializa o schema do banco automaticamente no primeiro start.
- **Correção de Persistência Chainlit 2.10+:** O `schema.sql` já inclui a coluna `"autoCollapse"` na tabela `steps`, evitando que o step interno do Chainlit falhe e faça mensagens desaparecerem.
- **Suporte a PDFs:** Extração automática de texto de arquivos PDF anexados diretamente no chat.
- **Autenticação Local:** Proteção simples por usuário e senha para habilitar a gestão de threads por usuário.

---

## 📋 Pré-requisitos

1. **Python 3.10+** instalado.
2. **Docker e Docker Compose** (ex: Docker Desktop).
3. **Ollama** instalado e rodando com o modelo desejado (ex: `ollama run qwen3-cpre:latest` ou `llama3`).

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
Abra o `.env` e preencha:
- `CHAINLIT_AUTH_SECRET`: cole a chave gerada acima.
- `CHAINLIT_LOCAL_USER`: seu usuário de login (ex: `admin`).
- `CHAINLIT_LOCAL_PASSWORD`: sua senha de login.

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