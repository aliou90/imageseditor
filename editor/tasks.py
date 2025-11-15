# tasks.py
import os
from celery import shared_task
from django.utils import timezone
from .models import UploadedImage
from django.conf import settings
import logging


# SUPPRESSION DES IMAGES ET ENREGISTREMENTS EXPIRÉS
logger = logging.getLogger(__name__)

@shared_task
def delete_expired_images():
    expired_images = UploadedImage.objects.filter(uploaded_at__lt=timezone.now() - timezone.timedelta(seconds=30))
    for image in expired_images:
        # Supprimer le fichier de temp_dir
        temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', os.path.basename(image.image.name))
        if os.path.isfile(temp_file_path):
            os.unlink(temp_file_path)
            logger.debug(f'Fichier temporaire supprimé : {temp_file_path}')

        # Supprimer l'enregistrement de la base de données
        image.delete()
        logger.debug(f'Enregistrement supprimé pour l\'image : {image.image.name}')
