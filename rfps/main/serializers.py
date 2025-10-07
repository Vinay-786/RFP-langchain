from users.serializers import MinimalCustomUserSerializer
from rest_framework import serializers
from .models import Project, RFPDocument
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    primary_contacts = MinimalCustomUserSerializer(many=True, read_only=True)
    manager_email = serializers.ReadOnlyField(source='manager.email')

    primary_contacts_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=User.objects.all(),
        source='primary_contacts'
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'type',
            'due_date',
            'description',
            'stage',
            'value',
            'manager',
            'manager_email',
            'primary_contacts',
            'primary_contacts_ids'
        ]
        read_only_fields = ['id']


class RFPDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.ReadOnlyField(source='uploaded_by.email')
    project_name = serializers.ReadOnlyField(source='project.name')

    class Meta:
        model = RFPDocument
        fields = [
            'file_id',
            'filename',
            'file_type',
            'document_file',
            'uploaded_by',
            'uploaded_by_email',
            'uploaded_at',
            'project',
            'project_name'
        ]
        read_only_fields = ['file_id', 'uploaded_by_email',
                            'uploaded_at', 'filename', 'file_type', 'project_name']
        extra_kwargs = {
            'uploaded_by': {'write_only': True},
        }


class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(
        required=True,
        max_length=500,
        help_text="The question to be answered by the RAG system."
    )


class ProjectRAGSerializer(serializers.Serializer):
    """Validates the incoming JSON input for project ID."""
    project_id = serializers.IntegerField(
        required=True,
        help_text="ID of the project whose documents should be indexed."
    )
