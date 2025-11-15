# models.py
from django.db import models
import uuid

class UploadedImage(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)  # Champ pour l'ID de session
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for session {self.session_id} uploaded at {self.uploaded_at}'

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.name}'
