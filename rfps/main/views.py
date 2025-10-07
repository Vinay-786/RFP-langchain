import uuid
import os
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project, RFPDocument
from .serializers import ProjectSerializer, RFPDocumentSerializer, PromptSerializer, ProjectRAGSerializer
from .utils.rag_service import RAGService
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Project instances.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if 'manager' not in serializer.validated_data:
            serializer.save(manager=self.request.user)
        else:
            serializer.save()


class RFPDocumentViewSet(viewsets.ModelViewSet):
    queryset = RFPDocument.objects.all()
    serializer_class = RFPDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        uploaded_file = self.request.data.get('document_file')
        original_filename = uploaded_file.name

        base_name, file_extension = os.path.splitext(original_filename)

        serializer.save(
            uploaded_by=self.request.user,
            file_id=str(uuid.uuid4()),
            filename=base_name,
            file_type=file_extension.lstrip('.').lower()
        )


class QueryRAGView(APIView):
    """
    POST endpoint to accept a prompt, query the RAG service, and return the answer.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PromptSerializer(data=request.data)

        if serializer.is_valid():
            user_query = serializer.validated_data['prompt']

            try:
                # Get the RAG chain (initialized only the first time)
                rag_chain = RAGService.get_rag_chain()

                # Invoke the chain
                # NOTE: For long-running queries, consider using Django Channels or
                # a background worker (like Celery) to avoid blocking the request thread.
                print(f"Invoking RAG chain for query: '{user_query}'")

                answer = rag_chain.invoke(user_query)

                # Return the result
                return Response({
                    'query': user_query,
                    'answer': answer
                }, status=status.HTTP_200_OK)

            except Exception as e:
                print(f"RAG Chain Error: {e}")
                return Response(
                    {'error': 'An error occurred while querying the knowledge base.',
                        'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

        project_id = serializer.validated_data['project_id']

        try:
            project = Project.objects.get(pk=project_id)

            if not project:
                return Response(
                    {'error': f"Project with ID {project_id} not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # In real code: project.documents.all()
            rfp_documents = project.documents.all()
            if not rfp_documents:
                return Response(
                    {'message': f"No RFPDocuments found for Project ID {project_id}. Nothing to index."},
                    status=status.HTTP_200_OK
                )

            # 2. Initialize RAG components (Manager and Splitter)
            # manager = RAGService.get_manager()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )

            all_chunked_docs = []

            # 3. Process each document
            for doc in rfp_documents:
                # doc.document_file.path is required to get the local disk path
                file_path = doc.document_file.path

                print(f"🔄 Processing document: {doc.filename}")

                # In a real app, use the file_type (doc.file_type) to select the correct loader.
                # Example: if doc.file_type == 'pdf': loader = PyPDFLoader(file_path)
                loader = Docx2txtLoader(file_path)
                documents = loader.load()

                chunked_docs = text_splitter.split_documents(documents)
                print(f"📄 Split into {len(chunked_docs)} chunks.")

                all_chunked_docs.extend(chunked_docs)

            # 4. Insert Data into Pinecone
            print(
                f"--- Inserting {len(all_chunked_docs)} chunks into Pinecone ---")

            result = RAGService.insert_documents(all_chunked_docs)

            return Response({
                'message': f"Successfully inserted {result.get('inserted_count', len(all_chunked_docs))} chunks for project {project_id}.",
                'project_id': project_id,
                'documents_processed': len(rfp_documents)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch file access, database connection, or LLM errors
            print(f"RAG Insertion Error: {e}")
            return Response(
                {'error': 'An error occurred during data insertion.',
                    'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
