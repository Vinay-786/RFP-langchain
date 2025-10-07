import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

load_dotenv()


class PineconeManager:
    """A class to manage Pinecone index operations and RAG pipeline creation."""

    def __init__(self, index_name: str, embedding_model):
        if not index_name:
            raise ValueError("Pinecone index name cannot be empty.")

        self.pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        self.index_name = index_name
        self.embedding_model = embedding_model
        self.embedding_dimension = 1536  # Dimension for 'text-embedding-3-small'
        self.vectorstore = None
        print("✅ PineconeManager initialized.")

    def create_or_connect_vectorstore(self, documents=None):
        if self.index_name not in self.pc.list_indexes().names():
            if not documents:
                raise ValueError(
                    "Documents must be provided to create a new index.")

            print(f"🌲 Creating new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            self.vectorstore = PineconeVectorStore.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                index_name=self.index_name
            )
            print("✅ Index created and documents embedded.")
        else:
            print(
                f"🌲 Connecting to existing Pinecone index: {self.index_name}")
            self.vectorstore = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                embedding=self.embedding_model
            )
            print("✅ Connected to index.")
        return self.vectorstore

    def get_rag_chain(self, llm, k=3):
        if not self.vectorstore:
            raise ConnectionError(
                "Vector store not initialized. Call 'create_or_connect_vectorstore' first.")

        print("🚀 Building RAG chain...")
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        prompt_template = """
        Use only the information from the context below to answer the question.
        If the answer is not in the context, say "I don't have enough information to answer that."

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        prompt = PromptTemplate.from_template(prompt_template)
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print("✅ RAG chain is ready.")
        return rag_chain
