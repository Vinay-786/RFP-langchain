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
    def get_rag_chain(cls) -> RunnableSerializable[Dict[str, Any], str]:
        """
        Initializes components and returns the RAG chain.
        The RAG chain is initialized only once (singleton pattern).
        """
        if cls._rag_chain is None:
            print("--- Initializing RAG Service Components (One-Time Setup) ---")
            cls._initialize_components()
            # Ensure components are initialized before use
            if cls._llm is None or cls._pinecone_manager is None:
                raise RuntimeError("RAGService components failed to initialize.")
            # Get the runnable RAG chain from the PineconeManager
            cls._rag_chain = cls._pinecone_manager.get_rag_chain(llm=cls._llm)
            print("--- RAG Service Initialization Complete ---")

        return cls._rag_chain

    @classmethod
    def insert_documents(cls, chunks: List[Document]) -> Dict[str, int]:
        """
        Inserts a list of document chunks into the Pinecone index.
        Initializes components if they haven't been already.
        """
        print(
            "--- Initializing RAG Service Components for Insertion (One-Time Setup) ---"
        )
        cls._initialize_components()

        if cls._pinecone_manager is None or cls._pinecone_manager.vectorstore is None:
            raise RuntimeError("PineconeManager or its vectorstore not initialized.")

        print(f"--- Inserting {len(chunks)} chunks into Pinecone ---")
        # Use the add_documents method directly from the PineconeVectorStore
        cls._pinecone_manager.vectorstore.add_documents(documents=chunks)
        print("--- Data Insertion Process Complete ---")
        # Return a dictionary with inserted_count, as expected by InsertRAGView
        return {"inserted_count": len(chunks)}
