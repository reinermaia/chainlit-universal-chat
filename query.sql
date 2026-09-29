-- =======================================================================
-- Consultas e utilitários para manutenção do banco de dados do Chainlit
-- =======================================================================

-- 1. Verificar os passos e mensagens salvos de uma conversa recente:
-- SELECT id, type, name, "parentId", LEFT(output, 80) AS preview, "createdAt"
-- FROM steps
-- ORDER BY "createdAt" DESC
-- LIMIT 30;

-- 2. Recuperar mensagens legadas órfãs (caso algum banco antigo tenha mensagens
-- cujo step pai não foi gravado):
-- UPDATE steps
-- SET "parentId" = NULL
-- WHERE "type" IN ('user_message', 'assistant_message', 'system_message')
--   AND "parentId" IS NOT NULL
--   AND "parentId" NOT IN (SELECT id FROM steps);

-- 3. Adicionar manualmente a coluna autoCollapse (se atualizando um banco antigo):
-- ALTER TABLE steps ADD COLUMN IF NOT EXISTS "autoCollapse" BOOLEAN;