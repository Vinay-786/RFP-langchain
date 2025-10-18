from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from .pinecone_setup import PineconeManager
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.runnables import RunnableSerializable


class RAGService:
    """
    Handles lazy and single initialization of the heavy RAG components (LLM, Index).
    """

    _rag_chain: Optional[RunnableSerializable[Dict[str, Any], str]] = None
    _pinecone_manager: Optional[PineconeManager] = None
    _embeddings_model: Optional[OpenAIEmbeddings] = None
    _llm: Optional[ChatOpenAI] = None
    PINECONE_INDEX_NAME: str = "rag-docx-index-modular"

    @classmethod
    def _initialize_components(cls) -> None:
        """
        Initializes components (embeddings, LLM, PineconeManager) only if they haven't been already.
        Ensures these are singletons.
        """
        if cls._embeddings_model is None:
            cls._embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        if cls._llm is None:
            cls._llm = ChatOpenAI(model="gpt-4o")
        if cls._pinecone_manager is None:
            cls._pinecone_manager = PineconeManager(
                index_name=cls.PINECONE_INDEX_NAME,
                embedding_model=cls._embeddings_model,
            )
            # Ensure the vectorstore is connected/created upon manager initialization
            cls._pinecone_manager.create_or_connect_vectorstore(documents=None)

    @classmethod
    def get_rag_chain(cls, project_id: str) -> RunnableSerializable[Dict[str, Any], str]:
        """
        Initializes components and returns the RAG chain.
        The RAG chain is initialized only once (singleton pattern).
        """
        if cls._embeddings_model is None:
            cls._embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        if cls._llm is None:
            cls._llm = ChatOpenAI(model="gpt-4o")

        print(f"🚀 Initializing RAG chain for project: {project_id}")
        pinecone_manager = PineconeManager(
            index_name=cls.PINECONE_INDEX_NAME,
            embedding_model=cls._embeddings_model,
            namespace=f"project_{project_id}",  # 👈 unique per project
        )
        pinecone_manager.create_or_connect_vectorstore()
        return pinecone_manager.get_rag_chain(llm=cls._llm)

    @classmethod
    def insert_documents(cls, chunks: List[Document], project_id: str) -> Dict[str, int]:
        """
        Inserts a list of document chunks into the Pinecone index.
        Initializes components if they haven't been already.
        """
        if cls._embeddings_model is None:
            cls._embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

        print(f"--- Inserting chunks into Pinecone for project_{project_id} ---")
        pinecone_manager = PineconeManager(
            index_name=cls.PINECONE_INDEX_NAME,
            embedding_model=cls._embeddings_model,
            namespace=f"project_{project_id}",
        )
        pinecone_manager.create_or_connect_vectorstore()
        pinecone_manager.vectorstore.add_documents(documents=chunks)
        print("--- Data Insertion Complete ---")
        return {"inserted_count": len(chunks)}
