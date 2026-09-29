-- Schema para chainlit.data.sql_alchemy.SQLAlchemyDataLayer (chainlit==2.12.0)
--
-- NÃO é uma cópia do schema.sql da doc oficial (docs.chainlit.io/data-layers/sqlalchemy).
-- Aquela doc usa UUID/JSONB/TEXT[] e eu tenho evidência de que ela já ficou
-- dessincronizada do código real antes (colunas "modes"/"disableFeedback"
-- ausentes em relatos de usuários, e o outro schema oficial — Prisma, para o
-- repo chainlit-datalayer — tem aviso explícito de estar desatualizado desde
-- a versão 2.0.0). Em vez de copiar, extraí os nomes de coluna direto do
-- código-fonte instalado (StepDict, Message.to_dict(), create_step) e validei
-- rodando de verdade contra esse schema (create_user, get_user, o INSERT
-- dinâmico de create_step, get_thread, list_threads) usando SQLite como
-- stand-in, já que não tenho um Postgres disponível neste ambiente pra testar
-- direto. Por isso os tipos abaixo são TEXT em vez de UUID/JSONB/TEXT[]
-- "idiomáticos" do Postgres: é o que eu realmente testei recebendo os valores
-- que o código produz (strings de UUID, JSON já serializado via json.dumps).
-- Ganho em correteza verificada, perco em tipagem nativa do Postgres.
--
-- Não testado: tags como lista populada (só validei com tags=NULL),
-- elements/feedbacks além da criação da tabela, e o dialeto Postgres em si
-- (asyncpg pode se comportar diferente do aiosqlite em alguma borda que eu
-- não bati durante o teste).

CREATE TABLE IF NOT EXISTS users (
    "id" TEXT PRIMARY KEY,
    "identifier" TEXT NOT NULL UNIQUE,
    "metadata" TEXT NOT NULL,
    "createdAt" TEXT
);

CREATE TABLE IF NOT EXISTS threads (
    "id" TEXT PRIMARY KEY,
    "createdAt" TEXT,
    "name" TEXT,
    "userId" TEXT,
    "userIdentifier" TEXT,
    "tags" TEXT,
    "metadata" TEXT,
    FOREIGN KEY ("userId") REFERENCES users("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS steps (
    "id" TEXT PRIMARY KEY,
    "name" TEXT,
    "type" TEXT NOT NULL,
    "threadId" TEXT NOT NULL,
    "parentId" TEXT,
    "streaming" BOOLEAN,
    "waitForAnswer" BOOLEAN,
    "isError" BOOLEAN,
    "metadata" TEXT,
    "tags" TEXT,
    "input" TEXT,
    "output" TEXT,
    "createdAt" TEXT,
    "command" TEXT,
    "start" TEXT,
    "end" TEXT,
    "generation" TEXT,
    "showInput" TEXT,
    "language" TEXT,
    "defaultOpen" BOOLEAN,
    "autoCollapse" BOOLEAN,
    "modes" TEXT,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS elements (
    "id" TEXT PRIMARY KEY,
    "threadId" TEXT,
    "type" TEXT,
    "url" TEXT,
    "chainlitKey" TEXT,
    "name" TEXT NOT NULL,
    "display" TEXT,
    "objectKey" TEXT,
    "size" TEXT,
    "page" INTEGER,
    "language" TEXT,
    "forId" TEXT,
    "mime" TEXT,
    "props" TEXT,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedbacks (
    "id" TEXT PRIMARY KEY,
    "forId" TEXT NOT NULL,
    "threadId" TEXT NOT NULL,
    "value" INTEGER NOT NULL,
    "comment" TEXT,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);
