from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from .pinecone_setup import PineconeManager


class RAGService:
    """
    Handles lazy and single initialization of the heavy RAG components (LLM, Index).
    """
    _rag_chain = None
    PINECONE_INDEX_NAME = "rag-docx-index-modular"

    @classmethod
    def get_rag_chain(cls):
        """Initializes components only if they haven't been already."""
        if cls._rag_chain is None:
            print("--- Initializing RAG Service Components (One-Time Setup) ---")

            embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
            llm = ChatOpenAI(model="gpt-4o")

            manager = PineconeManager(
                index_name=cls.PINECONE_INDEX_NAME,
                embedding_model=embeddings_model
            )

            manager.create_or_connect_vectorstore(documents=None)

            # Get the runnable RAG chain
            cls._rag_chain = manager.get_rag_chain(llm=llm)
            print("--- RAG Service Initialization Complete ---")

        return cls._rag_chain

    @classmethod
    def insert_documents(cls, chunks):
        """Initializes components only if they haven't been already."""
        if cls._rag_chain is None:
            print("--- Initializing RAG Service Components (One-Time Setup) ---")

            embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
            llm = ChatOpenAI(model="gpt-4o")

            manager = PineconeManager(
                index_name=cls.PINECONE_INDEX_NAME,
                embedding_model=embeddings_model
            )

            manager.create_or_connect_vectorstore(documents=chunks)

            # Get the runnable RAG chain
            cls._rag_chain = manager.get_rag_chain(llm=llm)
            print("--- RAG Service Initialization Complete ---")

        return cls._rag_chain
