# views.py
from django.shortcuts import render, redirect
from .models import UploadedImage
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.conf import settings
import zipfile
import io
from PIL import Image, ImageTk, ExifTags, ImageFilter, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageChops
import os
import logging
import uuid
import cv2
import traceback
import numpy as np
from .utils import correct_image_orientation, remove_background, resize_image, apply_rotation, vertical_flip, horizontal_flip, adjust_luminosity, adjust_contrast, add_new_background
# gestiond'e-mails
from django.core.mail import send_mail
from .models import Feedback


def index(request):
    return render(request, 'editor/index.html')


@csrf_exempt
def process_images(request):
    if request.method == 'POST':
        print("Traitement en cours !")
        try:
            images = request.FILES.getlist('images')
            resize_option = request.POST.get('resizeOptions')
            remove_bg = request.POST.get('removeBg') == 'on'
            bg_color = request.POST.get('bgColor')
            if not bg_color or bg_color == '#ffffff':
                bg_color = False
            degree = request.POST.get('degree', 0)
            flip_vertical = request.POST.get('flipVertical') == 'on'
            flip_horizontal = request.POST.get('flipHorizontal') == 'on'
            luminosity = request.POST.get('luminosity')
            contrast = request.POST.get('contrast')
            
            print(f"Images reçues : {len(images)}")
            print(f"Option de redimensionnement : {resize_option}")
            print(f"Suppression de l'arrière-plan : {remove_bg}")
            print(f"Ajout d'une nouvelle couleur d'arrière-plan : {bg_color}" if bg_color else "")
            print(f"Rotation : {degree}")
            print(f"flip vertical : {flip_vertical}")
            print(f"flip horizontal  : {flip_horizontal}")
            print(f"luminosité : {luminosity}")
            print(f"contraste : {contrast}")

            if not resize_option:
                return JsonResponse({'error': 'Resize option is missing'}, status=400)

            # Parse resize dimensions
            try:
                width, height = map(int, resize_option.split('x'))
            except ValueError:
                return JsonResponse({'error': 'Invalid resize option format'}, status=400)

            processed_images = []
            for image_file in images:
                original_name = image_file.name.rsplit('.', 1)[0]
                try:
                    # Traitement de l'image
                    img = Image.open(image_file)
                    img = correct_image_orientation(img)  # Corriger l'orientation de l'image
                    if remove_bg:
                        img = remove_background(image_file)  # Assuming this function exists

                    # Valider et appliquer la rotation
                    try:
                        degree = int(degree)
                    except ValueError:
                        degree = 0
                    img = apply_rotation(img, degree)

                    if flip_vertical:
                        img = vertical_flip(img)

                    if flip_horizontal:
                        img = horizontal_flip(img)
                    
                    # Valider et appliquer la luminosité
                    try:
                        luminosity = int(luminosity)
                    except ValueError:
                        luminosity = 0
                    img = adjust_luminosity(img, luminosity)

                    # Valider et appliquer le contrast
                    try:
                        contrast = int(contrast)
                    except ValueError:
                        contrast = 0
                    img = adjust_contrast(img, contrast)

                    img = resize_image(img, width, height) 

                    if bg_color:
                        img = add_new_background(img, width, height, bg_color)

                    # Save processed image to in-memory file
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    processed_images.append((original_name, buffer))  # Store original_name here
                except Exception as e:
                    print(f"Error processing image {image_file.name}: {str(e)}")
                    traceback.print_exc()
                    return JsonResponse({'error': str(e)}, status=500)

            # Compress processed images if more than one
            if len(processed_images) > 1:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zf:
                    for filename, img_buffer in processed_images:
                        zf.writestr(f"{filename}_edited.png", img_buffer.read())
                zip_buffer.seek(0)
                response = HttpResponse(zip_buffer, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=processed_images.zip'
                return response

            # Return the single processed image with '_edited' suffix
            single_image_name = f"{processed_images[0][0]}_edited.png"
            single_image_buffer = processed_images[0][1]
            response = HttpResponse(single_image_buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{single_image_name}"'
            return response

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



# SAUVEGARDER FICHIER TEMPORAIRE
# Configuration du journal
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def upload_image(request):
    try:
        if request.method == 'POST' and request.FILES.get('images'):
            image = request.FILES['images']
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            # Vider le répertoire temporaire
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        os.rmdir(file_path)
                except Exception as e:
                    logger.error(f'Erreur lors de la suppression du fichier {file_path}. Raison: {e}')

            temp_file_name = f"{uuid.uuid4().hex}_{image.name}"
            temp_file_path = os.path.join(temp_dir, temp_file_name)

            with open(temp_file_path, 'wb') as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)

            temp_url = os.path.join(settings.MEDIA_URL, 'temp', temp_file_name)
            logger.debug(f"Image temporaire enregistrée à : {temp_file_path}, URL : {temp_url}")
            return JsonResponse({'temp_url': temp_url})
        
        logger.error("Requête non valide ou fichier manquant")
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    except Exception as e:
        logger.exception("Erreur lors du téléchargement de l'image")
        return JsonResponse({'error': str(e)}, status=500)


# GESTION DES FEEDBACK
def feedback_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        feedback_text = request.POST.get('feedback')
        
        # Sauvegarder le feedback dans la base de données
        feedback = Feedback.objects.create(name=name, email=email, feedback=feedback_text)
        
        subject = f'Nouveau feedback de {name}'
        message = f'Nom: {name}\nEmail: {email}\nFeedback: {feedback_text}'
        recipient_list = [settings.EMAIL_HOST_USER]
        
        # Envoyer le feedback à tech.jamm.corp@gmail.com
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
        
        # Envoyer un e-mail de remerciement à l'utilisateur
        thank_you_subject = 'Merci pour votre feedback!'
        thank_you_message = f'Bonjour {name},\n\nMerci pour votre feedback! Votre message a été bien reçu et sera traité avec la plus grande importance.\n\nCordialement,\nL\'équipe de support'
        send_mail(thank_you_subject, thank_you_message, settings.EMAIL_HOST_USER, [email])
        
        return JsonResponse({'message': 'Merci pour votre feedback! Votre message a été envoyé.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

