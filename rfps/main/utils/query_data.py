from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone_setup import PineconeManager


def main():
    """Connects to an existing knowledge base and answers user questions."""
    print("--- Starting Query Process ---")

    # --- 1. Configuration ---
    PINECONE_INDEX_NAME = "rag-docx-index-modular"

    # --- 2. Initialize Models and Manager ---
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    llm = ChatOpenAI(model="gpt-4o")
    manager = PineconeManager(
        index_name=PINECONE_INDEX_NAME, embedding_model=embeddings_model)

    manager.create_or_connect_vectorstore(documents=None)

    rag_chain = manager.get_rag_chain(llm=llm)

    print("\nAsk a question about your document (type 'exit' to quit).")
    while True:
        query = input("Your question: ")
        if query.lower() == 'exit':
            break

        print("\n🤔 Thinking...")
        answer = rag_chain.invoke(query)
        print(f"\n💡 Answer: {answer}\n")

    print("--- 👋 Goodbye! ---")


if __name__ == "__main__":
    main()
