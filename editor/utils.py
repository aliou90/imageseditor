# utils.py
import tempfile
import json
import os
from datetime import datetime
import cv2
import requests
import io
import glob
import numpy as np
from rembg import remove
from PIL import Image, ImageTk, ExifTags, ImageFilter, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageChops
from pathlib import Path
import sys  
from math import cos, sin, radians

def remove_background(image_file):
    # Charger l'image depuis le fichier
    image = np.array(Image.open(image_file).convert('RGB'))  # Convertir en RGB
    
    # Charger l'image depuis le fichier
    input_image = Image.open(image_file).convert('RGBA')
    
    # Supprimer l'arrière-plan
    output_image = remove(input_image)
    
    # Convertir le résultat en RGBA si ce n'est pas déjà le cas
    if output_image.mode != 'RGBA':
        output_image = output_image.convert('RGBA')

    print(f"Background removed for {image_file}.")
    return output_image


# Redimentionner l'image
def resize_image(image, width, height):
    # Convertir l'image reçue à "RGBA" si ce n'est pas déjà le cas
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    # Obtenez les dimensions de l'image reçue
    img_width, img_height = image.size
    print(f"Dimension de l'image sans BG: {img_width}x{img_height}")
    
    # Calculer le facteur de redimensionnement pour maintenir les proportions
    aspect_ratio = img_width / img_height
    container_ratio = width / height
    
    if aspect_ratio > container_ratio:
        # Redimensionner l'image en fonction de la largeur
        new_width = width
        new_height = int(new_width / aspect_ratio)
    else:
        # Redimensionner l'image en fonction de la hauteur
        new_height = height
        new_width = int(new_height * aspect_ratio)
    
    # Redimensionner l'image
    image = image.resize((new_width, new_height), Image.LANCZOS)
    print(f"Dimension de l'image redimensionnée: {new_width}x{new_height}")
    
    # Créer une nouvelle image avec les dimensions spécifiées
    new_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    
    # Calculer les coordonnées pour centrer l'image redimensionnée
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    
    # Coller l'image redimensionnée au centre de la nouvelle image
    new_image.paste(image, (left, top), image)
    
    return new_image

# Convertir le format de couleur en RGB
def hex_to_rgb(hex_color):
    """ Convertit le nom d'une couleur hexadécimale en RGB """
    hex_color = hex_color.lstrip("#")
    # Convertir les valeurs hexadécimales en tuples RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Appliquer la rotation
def apply_rotation(image, degree):
    image = image.rotate(degree, expand=True)
    return image

# Appliquer le flip vertical
def vertical_flip(image):
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return image

# Appliquer le flip horizontal
def horizontal_flip(image):
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    return image

# Appliquer luminosité
def adjust_luminosity(image, luminosity_value):
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1 + luminosity_value / 11.0)
    return image

def adjust_contrast(image, contrast_value):
    # Appliquer le contraste
    if contrast_value > 0:
        contrast_value = contrast_value / 10.0
        # Convertir l'image en mode 'RGB' si elle est en mode 'RGBA'
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        # Appliquer le contrast
        image = ImageOps.autocontrast(image, cutoff=contrast_value * 20)
        # Revenir en mode 'RGBA' si nécessaire
        if image.mode == 'RGB':
            image = image.convert('RGBA')
    else:
        image = image
        
    return image

# Ajouter Nouveau Background
def add_new_background(image, font_width, font_height, new_color):
    # Convertir la couleur hexadécimale en RGB
    rgb_color = hex_to_rgb(new_color)
    
    # Obtenez les dimensions de l'image reçue
    img_width, img_height = image.size
    
    # Créez une nouvelle image avec la couleur de fond spécifiée
    background_image = Image.new("RGB", (font_width, font_height), rgb_color)
    
    # Convertir l'image d'origine au mode RGBA pour inclure la transparence si nécessaire
    image = image.convert("RGBA")
    
    # Coller l'image reçue sur le fond coloré
    # Le troisième argument (masque) assure que la transparence est respectée
    background_image.paste(image, (0, 0), image)
    
    print(f"Nouvelle arrière-plan ajoutée")
    return background_image


# Correction de l'image avant traitement
def correct_image_orientation(image):
    try:
        # Vérifier si l'image a des métadonnées EXIF
        if hasattr(image, '_getexif') and image._getexif() is not None:
            # Trouver la clé d'orientation dans les métadonnées EXIF
            orientation = None
            for key, value in ExifTags.TAGS.items():
                if value == 'Orientation':
                    orientation = key
                    break
            
            # Obtenir les données EXIF
            exif = dict(image._getexif().items())
            
            # Corriger l'orientation de l'image si nécessaire
            if orientation and orientation in exif:
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # L'image n'a pas de métadonnées EXIF ou aucune orientation n'a besoin d'être corrigée
        pass
    
    return image


