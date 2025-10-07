from rest_framework import viewsets
from .serializers import CustomUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
