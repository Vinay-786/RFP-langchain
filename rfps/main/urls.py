from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ProjectViewSet,
    RFPDocumentViewSet,
    QueryRAGView,
    InsertRAGView,
    OpenAIChat,
    GenerateRFPView
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'documents', RFPDocumentViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('query', QueryRAGView.as_view(), name='rag-query'),
    path('insert-rag', InsertRAGView.as_view(), name='rag-query'),
    path('chatai', OpenAIChat.as_view(), name='openaichat'),
    path('generate-rfp', GenerateRFPView.as_view(), name='generate-rfp'),
]
