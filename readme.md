# Chainlit Universal Chat (PostgreSQL + Pluggable LLM) 🚀

A production-ready starter template for building conversational AI applications with **persistent chat history**, powered by **Chainlit**, **PostgreSQL**, and any **OpenAI-compatible LLM** (local Ollama, OpenAI, LiteLLM, or corporate API gateways).

---

## ✨ Features

- **Pluggable LLM Provider:** Compatible with any endpoint implementing the OpenAI `/chat/completions` specification, including **local Ollama**, **official OpenAI**, **LiteLLM**, **vLLM**, and **corporate/enterprise gateways**.
- **Persistent Chat History (Sidebar):** Full thread persistence with sidebar navigation powered by Chainlit's `SQLAlchemyDataLayer` and PostgreSQL.
- **Zero-Config Database:** Pre-configured `docker-compose.yml` that mounts and automatically initializes the database schema on first startup.
- **Chainlit 2.10+ Persistence Fix:** The included `schema.sql` contains the `"autoCollapse"` column in the `steps` table, resolving the known issue where internal steps fail to persist and assistant responses disappear upon reopening threads.
- **PDF Document Support:** Automatic text extraction from PDF files uploaded directly in the chat interface.
- **Corporate Network & Proxy Friendly:** Optional `LLM_VERIFY_SSL=false` toggle to support restricted corporate networks with SSL-inspecting proxies or custom internal CA certificates.
- **Local Authentication:** Password-based authentication callback to isolate user sessions and manage individual chat histories.

---

## 📋 Prerequisites

1. **Python 3.10+**
2. **Docker & Docker Compose** (e.g., Docker Desktop)
3. **LLM Provider:**
   - **Local:** [Ollama](https://ollama.com/) running a model (e.g., `ollama run qwen3-cpre:latest` or `llama3`).
   - **Remote:** Any OpenAI-compatible API endpoint, API key, and model name.

---

## 🛠️ Quickstart Guide

### 1. Clone the repository
```bash
git clone https://github.com/reinermaia/chainlit-universal-chat.git
cd chainlit-universal-chat
```

### 2. Configure environment variables
Copy the example environment file:
```bash
cp .env.example .env
```

Generate a session secret:
```bash
chainlit create-secret
```

Open `.env` and fill in the values:
- `CHAINLIT_AUTH_SECRET`: Paste the secret key generated above.
- `CHAINLIT_LOCAL_USER`: Your desired login username.
- `CHAINLIT_LOCAL_PASSWORD`: Your desired login password.

#### LLM Configuration Examples

* **For Local Ollama (Default):**
  ```env
  LLM_BASE_URL=http://localhost:11434/v1
  LLM_API_KEY=ollama
  LLM_MODEL=qwen3-cpre:latest
  ```

* **For Corporate Gateway or OpenAI:**
  ```env
  LLM_BASE_URL=https://your-api-gateway.com/v1
  LLM_API_KEY=your_api_key_here
  LLM_MODEL=gpt-5.3-codex
  # If working behind an SSL-inspecting corporate proxy:
  # LLM_VERIFY_SSL=false
  ```

### 3. Start PostgreSQL via Docker
```bash
docker compose up -d
```
*(The container starts on port `5432` and automatically initializes all tables defined in `schema.sql`).*

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the application
```bash
chainlit run app.py -w
```

Open your browser at **`http://localhost:8000`** and log in with the credentials set in your `.env` file.

---

## 🔍 Chainlit Persistence Troubleshooting Note

When using Chainlit with `SQLAlchemyDataLayer` on version `2.10.0` or later, steps may fail to insert if the database schema lacks the `"autoCollapse"` column, causing assistant messages to disappear when reopening threads.

This repository resolves the issue out of the box:
- `schema.sql` defines `"autoCollapse" BOOLEAN` in the `steps` table.
- `query.sql` provides utility queries to repair legacy orphaned threads if migrating from an older schema.

---

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it!