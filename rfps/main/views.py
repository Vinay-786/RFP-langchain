import uuid
import os
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project, RFPDocument
from .serializers import (
    ProjectSerializer,
    RFPDocumentSerializer,
    PromptSerializer,
    ProjectRAGSerializer,
)
from .utils.rag_service import RAGService
from .utils.openai_setup import chat_with_gpt
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from django.conf import settings
from pathlib import Path


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Project instances.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if "manager" not in serializer.validated_data:
            serializer.save(manager=self.request.user)
        else:
            serializer.save()


class RFPDocumentViewSet(viewsets.ModelViewSet):
    queryset = RFPDocument.objects.all()
    serializer_class = RFPDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        uploaded_file = self.request.data.get("document_file")
        original_filename = uploaded_file.name

        base_name, file_extension = os.path.splitext(original_filename)

        serializer.save(
            uploaded_by=self.request.user,
            file_id=str(uuid.uuid4()),
            filename=base_name,
            file_type=file_extension.lstrip(".").lower(),
        )

    def perform_update(self, serializer):
        uploaded_file = self.request.data.get("document_file")

        update_kwargs = {}

        if uploaded_file:
            original_filename = uploaded_file.name
            base_name, file_extension = os.path.splitext(original_filename)

            update_kwargs['filename'] = base_name
            update_kwargs['file_type'] = file_extension.lstrip(".").lower()

        # Save the instance with any collected updates
        serializer.save(**update_kwargs)


class QueryRAGView(APIView):
    """
    POST endpoint to accept a prompt, query the RAG service, and return the answer.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PromptSerializer(data=request.data)

        if serializer.is_valid():
            user_query = serializer.validated_data["prompt"]

            try:
                # Get the RAG chain (initialized only the first time)
                rag_chain = RAGService.get_rag_chain()

                # Invoke the chain
                # NOTE: For long-running queries, consider using Django Channels or
                # a background worker (like Celery) to avoid blocking the request thread.
                print(f"Invoking RAG chain for query: '{user_query}'")

                answer = rag_chain.invoke(user_query)

                # Return the result
                return Response(
                    {"query": user_query, "answer": answer}, status=status.HTTP_200_OK
                )

            except Exception as e:
                print(f"RAG Chain Error: {e}")
                return Response(
                    {
                        "error": "An error occurred while querying the knowledge base.",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InsertRAGView(APIView):
    """
    POST endpoint to take a project ID, retrieve associated documents,
    process, and insert chunks into Pinecone.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProjectRAGSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        project_id = serializer.validated_data["project_id"]

        try:
            project = Project.objects.get(pk=project_id)

            if not project:
                return Response(
                    {"error": f"Project with ID {project_id} not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            rfp_documents = project.documents.all()
            if not rfp_documents:
                return Response(
                    {
                        "message": f"No RFPDocuments found for Project ID {project_id}. Nothing to index."
                    },
                    status=status.HTTP_200_OK,
                )

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )

            all_chunked_docs = []

            for doc in rfp_documents:
                # This ensures the path is correct regardless of OS
                file_path = Path(settings.MEDIA_ROOT) / doc.document_file.name

                if not file_path.exists():
                    print(
                        f"File not found for document {doc.filename}: {file_path}")
                    # Optionally skip this document or return an error
                    continue

                print(
                    f"Processing document: {doc.filename} at {file_path} with {doc.file_type}")

                if (doc.file_type == 'pdf'):
                    loader = PyPDFLoader(
                        str(file_path)
                    )
                elif (doc.file_type == 'docx'):
                    loader = Docx2txtLoader(
                        str(file_path)
                    )
                else:
                    print(
                        f"Unsupported file_type '{doc.file_type}' for document. Skipping.")
                    continue
                documents = loader.load()

                chunked_docs = text_splitter.split_documents(documents)
                print(f"Doc Split into {len(chunked_docs)} chunks.")

                all_chunked_docs.extend(chunked_docs)

            if not all_chunked_docs:
                return Response(
                    {
                        "message": f"No processable chunks found for Project ID {project_id}. Nothing to insert."
                    },
                    status=status.HTTP_200_OK,
                )

            # 4. Insert Data into Pinecone using RAGService
            result = RAGService.insert_documents(all_chunked_docs)

            return Response(
                {
                    "message": f"Successfully inserted {result.get('inserted_count', 0)} chunks for project {project_id}.",
                    "project_id": project_id,
                    "documents_processed": len(rfp_documents),
                },
                status=status.HTTP_200_OK,
            )

        except Project.DoesNotExist:
            return Response(
                {"error": f"Project with ID {project_id} not found in the database."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            # Catch file access, database connection, or LLM errors
            print(f"RAG Insertion Error: {e}")
            return Response(
                {
                    "error": "An error occurred during data insertion.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OpenAIChat(APIView):
    def post(self, request):
        messages = request.data.get("messages", [])

        if not isinstance(messages, list) or not messages:
            return Response(
                {"error": "messages must be a non-empty list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            answer = chat_with_gpt(messages)
            return Response({"response": answer}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
