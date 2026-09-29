import os
import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.types import ThreadDict
from openai import AsyncOpenAI
from pypdf import PdfReader

# Corte grosseiro de caracteres pra não estourar o context window do modelo
# com um PDF gigante. 12000 chars é um chute conservador pra um num_ctx de
# 32768 tokens (visto no seu "ollama show") — sobra espaço pro resto da
# conversa. Ajuste se precisar de PDFs maiores.
MAX_PDF_CHARS = 12000


def extract_pdf_text(path: str) -> str:
    try:
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as e:
        return f"[Falha ao ler o PDF: {e}]"
    if not text:
        return (
            "[PDF sem texto extraível — provavelmente é um scan/imagem, não "
            "texto real. Extração de texto não ajuda aqui; precisaria de OCR "
            "ou de um modelo com visão, nenhum dos dois implementado ainda.]"
        )
    if len(text) > MAX_PDF_CHARS:
        text = text[:MAX_PDF_CHARS] + "\n[...texto cortado, PDF maior que o limite...]"
    return text

# 1. MUDANÇA PRINCIPAL: Apontamos o cliente para o seu Ollama local
client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",  # URL do servidor local do Ollama
    api_key="ollama"  # A biblioteca exige uma chave, mas o Ollama local ignora o que estiver escrito aqui
)

# llm settings
settings = {
    "model": "qwen3-cpre:latest",  # <-- Atualizado para o nome correto
    "temperature": 0,
    "max_tokens": 900,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

# Corte por NÚMERO de mensagens, não por tokens — mesma ressalva de antes:
# ajuste considerando o context window real do qwen3-cpre.
MAX_CONTEXT_MESSAGES = 20


# --- Autenticação -----------------------------------------------------
# Usuário único, local. A sidebar de threads só aparece com auth + data
# layer configurados juntos (confirmado na doc de Chat History do Chainlit).
LOCAL_USERNAME = os.environ.get("CHAINLIT_LOCAL_USER", "reiner")
LOCAL_PASSWORD = os.environ.get("CHAINLIT_LOCAL_PASSWORD")

if not LOCAL_PASSWORD:
    raise RuntimeError(
        "Defina CHAINLIT_LOCAL_PASSWORD no .env antes de rodar o app."
    )


@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    if username == LOCAL_USERNAME and password == LOCAL_PASSWORD:
        return cl.User(identifier=username)
    return None
# ------------------------------------------------------------------------


# --- Persistência (Postgres local via docker-compose.yml / schema.sql) --
# Com a coluna "autoCollapse" devidamente adicionada no schema.sql (Chainlit 2.10.0+),
# o step on_message é persistido com sucesso e não há mais mensagens órfãs.
@cl.data_layer
def get_data_layer():
    return SQLAlchemyDataLayer(conninfo=os.environ["DATABASE_URL"])
# ------------------------------------------------------------------------


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    # Corpo vazio DE PROPÓSITO. Confirmei lendo chainlit/socket.py: o próprio
    # framework repopula cl.chat_context com os steps persistidos da thread
    # ANTES de qualquer mensagem nova chegar — mas só faz isso se este
    # handler existir. Reconstruir isso na mão aqui seria redundante e
    # arriscaria divergir da lógica interna do framework.
    pass


@cl.on_message
async def main(message: cl.Message):
    # Anexos: o Chainlit já salva o arquivo em disco e expõe o caminho local
    # em element.path antes do on_message rodar — confirmei isso lendo
    # chainlit/emitter.py (process_message). Não precisa buscar nada.
    attachment_note = ""
    for element in message.elements or []:
        mime = (element.mime or "").lower()
        path = getattr(element, "path", None)
        is_pdf = mime == "application/pdf" or (
            path and str(path).lower().endswith(".pdf")
        )
        if is_pdf and path:
            attachment_note += (
                f"\n\n--- Conteúdo extraído de '{element.name}' ---\n"
                f"{extract_pdf_text(path)}"
            )
        elif mime.startswith("image/"):
            attachment_note += (
                f"\n\n[Anexo de imagem '{element.name}' recebido — o "
                "qwen3-cpre não tem capacidade de visão (confirmado via "
                "'ollama show': Capabilities = tools, thinking, completion, "
                "sem 'vision'). Não consigo analisar o conteúdo visual dele.]"
            )

    # cl.chat_context já contém a mensagem que acabou de chegar (o framework
    # adiciona antes de chamar este handler — confirmei em
    # chainlit/emitter.py) + todo o histórico da thread atual, seja ela nova
    # ou retomada pela sidebar.
    payload_messages = cl.chat_context.to_openai()[-MAX_CONTEXT_MESSAGES:]

    if attachment_note:
        # Injeta o texto extraído SÓ nesta chamada ao Ollama — não fica
        # gravado no histórico persistido (o que está salvo no Postgres
        # continua sendo só "o que tem neste PDF?", sem o texto extraído).
        # Isso significa: se você retomar essa thread depois e perguntar de
        # novo sobre o mesmo PDF sem reanexar, o modelo não vai mais ter o
        # conteúdo — só a pergunta em texto. Decisão consciente pra não
        # inflar a bolha de mensagem do usuário na tela com o PDF inteiro.
        payload_messages = payload_messages[:-1] + [
            {"role": "user", "content": message.content + attachment_note}
        ]

    stream = await client.chat.completions.create(
        messages=payload_messages,
        stream=True,
        **settings
    )

    # Create a new message and stream the response
    msg = cl.Message(content="")
    await msg.send()

    async for chunk in stream:
        if token := chunk.choices[0].delta.content:
            await msg.stream_token(token)

    await msg.update()


@cl.on_chat_start
async def on_chat_start():
    # Certifique-se de que o arquivo "hi.gif" existe na mesma pasta, senão remova a linha abaixo
    image = cl.Image(path="./hi.gif", name="Hi", display="inline")

    # Sending an action button within a chatbot message
    actions = [
        cl.Action(
            name="action_button",
            icon="mouse-pointer-click",
            payload={"value": "example_value"},
            label="Click me!"
        )
    ]

    # Attach the image and the clickable button to the message
    await cl.Message(
        content="Hi There, how can I help you today?",
        actions=actions,
        elements=[image]
    ).send()


@cl.action_callback("action_button")
async def on_action(action: cl.Action):
    print(action.payload)


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Refine my email",
            message="Can you correct and refine my email for clarity",
            icon="/public/idea.svg",
            ),
        cl.Starter(
            label="Explain In laymans Terms",
            message="Explain explain the following term/subject in laymans terms. user friendly and informative tone",
            icon="/public/learn.svg",
            ),
        cl.Starter(
            label="Fix grammatic errors",
            message="Review and fix grammatical errors of the following statement",
            icon="/public/terminal.svg",
            ),
        cl.Starter(
            label="Debug a code",
            message="Debug the following error of the following code",
            icon="/public/write.svg",
            )
        ]