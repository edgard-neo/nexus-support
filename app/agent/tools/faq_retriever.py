from langchain.tools import tool

from app.rag.vectorstore import format_context, retrieve_faq


@tool
def buscar_faq(pergunta: str) -> str:
    """
    Busca informacoes na base de conhecimento da loja.
    Use para responder perguntas sobre frete, prazo de entrega, trocas,
    devolucoes, formas de pagamento, parcelamento e politicas da loja.
    """
    chunks = retrieve_faq(pergunta)

    if not chunks:
        return "Nao encontrei informacoes sobre esse assunto na base de conhecimento."

    return format_context(chunks)
