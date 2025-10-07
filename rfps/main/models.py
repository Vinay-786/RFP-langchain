from django.db import models
from users.models import CustomUser
from rest_framework.utils.timezone import datetime


class Project(models.Model):
    class ProjectStage(models.TextChoices):
        PROSPECT = 'PR', ('Prospect')
        IN_PROGRESS = 'IP', ('In Progress')
        ON_HOLD = 'OH', ('On Hold')
        COMPLETED = 'CP', ('Completed')
        CANCELLED = 'CN', ('Cancelled')

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    description = models.TextField()
    stage = models.CharField(max_length=10, choices=ProjectStage.choices,
                             default=ProjectStage.PROSPECT)
    value = models.IntegerField()
    manager = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="projects")
    primary_contacts = models.ManyToManyField(
        CustomUser, related_name="assigned")

    REQUIRED_FILEDS = ['name', 'type']

    def __str__(self):
        return self.name


class RFPDocument(models.Model):
    file_id = models.CharField(
        primary_key=True, max_length=255, unique=True)

    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)

    # document_url = models.URLField(max_length=500, blank=True, null=True)
    document_file = models.FileField(
        upload_to='rfp_documents/%Y/%m/%d/')  # for local dev

    uploaded_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='uploader')

    uploaded_at = models.DateTimeField(default=datetime.now)
    project = models.ForeignKey(
        'Project',
        on_delete=models.SET_NULL,
        related_name='documents',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.filename
