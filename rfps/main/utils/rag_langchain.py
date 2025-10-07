import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from langchain_community.document_loaders import Docx2txtLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# --- 1. Load Environment Variables ---
# Load API keys from the .env file
load_dotenv()

# Ensure your keys are set correctly
if "PINECONE_API_KEY" not in os.environ:
    raise ValueError(
        "PINECONE_API_KEY is not set in the environment variables.")
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

print("✅ Environment variables loaded.")

# --- 2. Constants and Configuration ---
# Choose a name for your Pinecone index
PINECONE_INDEX_NAME = "rag-architecture"
# The document you want to query
# DOCX_FILE_PATH = "./rfps/media/rfp_documents/2025/10/07/21-114_Customer_Identity_and_Access_Management_Solution.docx"
DOCX_FILE_PATH="example.docx"

# --- 3. Initialize Connections ---
# Initialize Pinecone client
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Initialize OpenAI embeddings model
# The 'text-embedding-3-small' model creates vectors with 1536 dimensions
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
embedding_dimension = 1536

# Initialize the powerful Chat Model for generation
llm = ChatOpenAI(model="gpt-4o")

print("✅ Connections initialized.")

# --- 4. Load and Process the Document ---
print(f"🔄 Loading document: {DOCX_FILE_PATH}...")
loader = Docx2txtLoader(DOCX_FILE_PATH)
documents = loader.load()

# --- 5. Intelligent Chunking ---
# This splitter tries to keep paragraphs, sentences, and words together.
# chunk_size: The max number of characters in a chunk.
# chunk_overlap: The number of characters to overlap between chunks to maintain context.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200)
chunked_docs = text_splitter.split_documents(documents)

print(f"📄 Document loaded and split into {len(chunked_docs)} chunks.")

# --- 6. Create or Connect to Pinecone Index and Vector Store ---
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    print(f"🌲 Creating new Pinecone index: {PINECONE_INDEX_NAME}")
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=embedding_dimension,  # Dimension for text-embedding-3-small
        metric="cosine",  # Cosine similarity is great for text
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    # This is the core step: embedding documents and storing them in Pinecone
    vectorstore = PineconeVectorStore.from_documents(
        documents=chunked_docs,
        embedding=embeddings_model,
        index_name=PINECONE_INDEX_NAME
    )
    print("✅ Index created and documents embedded.")
else:
    print(f"🌲 Connecting to existing Pinecone index: {PINECONE_INDEX_NAME}")
    # If the index already exists, we just connect to it
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings_model
    )
    print("✅ Connected to index.")

# --- 7. Define the RAG Chain (The "Brain" of the operation) ---
# Create a retriever to fetch relevant documents from the vector store
# Retrieve top 3 most relevant chunks
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Define the prompt template to structure the input for the LLM
prompt_template = """
You are an intelligent assistant that answers questions based on the provided context.
Use only the information from the context below to answer the question.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question:
{question}

Answer:
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# This is the LangChain Expression Language (LCEL) chain
# It defines the flow:
# 1. The user's question is passed to the retriever.
# 2. The retriever's output (context) and the original question are passed to the prompt.
# 3. The formatted prompt is passed to the language model (LLM).
# 4. The LLM's output is parsed into a clean string.
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("🚀 RAG pipeline is ready to answer questions!")

# --- 8. Query the Pipeline ---
if __name__ == "__main__":
    # Example queries
    query1 = "What is this Request of proposal about?"
    print(f"\n❓ Querying with: '{query1}'")
    answer1 = rag_chain.invoke(query1)
    print(f"💡 Answer: {answer1}")

    # Change this to a specific question for your doc
    # query2 = "Summarize the key points mentioned about project alpha."
    # print(f"\n❓ Querying with: '{query2}'")
    # answer2 = rag_chain.invoke(query2)
    # print(f"💡 Answer: {answer2}")
