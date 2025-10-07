from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from pinecone_manager import PineconeManager


def main():
    """Loads a document, chunks it, and inserts it into a Pinecone index."""
    print("--- Starting Data Insertion Process ---")

    # --- 1. Configuration ---
    PINECONE_INDEX_NAME = "rag-knowledge-base"
    DOCX_FILE_PATH = "example.docx"  # Make sure this file exists

    # --- 2. Initialize Models and Manager ---
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    manager = PineconeManager(
        index_name=PINECONE_INDEX_NAME, embedding_model=embeddings_model)

    # --- 3. Load and Chunk Document ---
    print(f"🔄 Loading document: {DOCX_FILE_PATH}...")
    loader = Docx2txtLoader(DOCX_FILE_PATH)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    chunked_docs = text_splitter.split_documents(documents)
    print(f"📄 Document split into {len(chunked_docs)} chunks.")

    # --- 4. Create Index and Insert Data ---
    # This will create the index if it doesn't exist and add the documents.
    # If the index exists, it will connect and you could add more docs if needed.
    manager.create_or_connect_vectorstore(documents=chunked_docs)

    print("--- ✅ Data Insertion Process Complete ---")


if __name__ == "__main__":
    main()
