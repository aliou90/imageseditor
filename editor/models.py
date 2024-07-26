# models.py
# Create your models here.
from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.name}'
