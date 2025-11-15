// Fonction pour obtenir le jeton CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updatePreview() {
    const imagePreviewElement = document.getElementById('imagePreview');
    const tempImageUrl = imagePreviewElement.getAttribute('data-temp-url');
    const formData = new FormData();
    const resizeOptions = document.getElementById('resizeOptions').value;
    const removeBgCheckbox = document.getElementById('removeBgCheckbox');
    const removeBg = removeBgCheckbox.checked ? 'on' : 'off';
    const bgColor = document.getElementById('bgColor').value;
    const degree = document.getElementById('degree').value;
    const flipVerticalCheckbox = document.getElementById('flipVertical');
    const flipHorizontalCheckbox = document.getElementById('flipHorizontal');
    const flipVertical = flipVerticalCheckbox.checked ? 'on' : 'off';
    const flipHorizontal = flipHorizontalCheckbox.checked ? 'on' : 'off';
    const luminosity = document.getElementById('luminosity').value;
    const contrast = document.getElementById('contrast').value;

    if (!tempImageUrl) {
        console.error('URL temporaire non définie');
        return;
    }

    // Afficher l'image processing.gif pendant le traitement
    imagePreviewElement.src = processingGifUrl;

    fetch(tempImageUrl)
        .then(res => {
            if (!res.ok) {
                throw new Error('Image temporaire non trouvée');
            }
            return res.blob();
        })
        .then(blob => {
            formData.append('images', blob, 'preview.png');
            formData.append('resizeOptions', resizeOptions);
            formData.append('removeBg', removeBg);
            formData.append('bgColor', bgColor);
            formData.append('degree', degree);
            formData.append('flipVertical', flipVertical);
            formData.append('flipHorizontal', flipHorizontal);
            formData.append('luminosity', luminosity);
            formData.append('contrast', contrast);

            return fetch('/process-images/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') // Inclure le jeton CSRF
                }
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Réponse réseau non valide');
            }
            return response.blob();
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            imagePreviewElement.style.transition = 'opacity 1s ease-in-out';
            imagePreviewElement.style.opacity = 0; // Début de la transition
            setTimeout(() => {
                imagePreviewElement.src = url;
                imagePreviewElement.style.opacity = 1; // Fin de la transition
            }, 1000);
        })
        .catch(error => console.error('Erreur:', error));
}


// Écouter les changements sur les options de redimensionnement et la couleur de fond pour envoyer le formulaire
document.getElementById('resizeOptions').addEventListener('change', updatePreview);
document.getElementById('bgColor').addEventListener('change', updatePreview);
document.getElementById('removeBgCheckbox').addEventListener('change', updatePreview);
document.getElementById('degree').addEventListener('change', updatePreview);
document.getElementById('flipVertical').addEventListener('change', updatePreview);
document.getElementById('flipHorizontal').addEventListener('change', updatePreview);
document.getElementById('luminosity').addEventListener('change', updatePreview);
document.getElementById('contrast').addEventListener('change', updatePreview);

// GESTION D'INCRÉMENTATION ET DÉCRÉMENTATION DE DEGRÉE
// Affichages du degrée de la rotation dans les 2 sens
document.getElementById('decrementDegree').addEventListener('click', function(event) {
    event.preventDefault(); // Empêche le comportement par défaut du bouton
    const degreeEntry = document.getElementById('degree');
    let currentValue = parseInt(degreeEntry.value, 10);
    let newValue = (currentValue - 15 + 360) % 360; // Calculer la nouvelle valeur avec boucle de 360 degrés
    degreeEntry.value = newValue;
    updatePreview(); // Appeler la fonction pour mettre à jour la prévisualisation
});

document.getElementById('incrementDegree').addEventListener('click', function(event) {
    event.preventDefault(); // Empêche le comportement par défaut du bouton
    const degreeEntry = document.getElementById('degree');
    let currentValue = parseInt(degreeEntry.value, 10);
    let newValue = (currentValue + 15) % 360; // Calculer la nouvelle valeur avec boucle de 360 degrés
    degreeEntry.value = newValue;
    updatePreview(); // Appeler la fonction pour mettre à jour la prévisualisation
});  

// AFFICHAGE VALEUR DE LUMINOSITÉ ET CONTRASTE
// Affichages des valeurs de la luminosité et du contrast
document.getElementById('luminosity').addEventListener('input', function() {
    document.getElementById('luminosityValue').textContent = this.value;
    updatePreview();
});

document.getElementById('contrast').addEventListener('input', function() {
    document.getElementById('contrastValue').textContent = this.value;
    updatePreview();
});

// TRAITEMENT ET TÉLÉCHARGEMENT 
document.getElementById('startButton').addEventListener('click', function(event) {
    event.preventDefault();

    const imagePreviewElement = document.getElementById('imagePreview');
    const formData = new FormData();
    const resizeOptions = document.getElementById('resizeOptions').value;
    const removeBgCheckbox = document.getElementById('removeBgCheckbox');
    const removeBg = removeBgCheckbox.checked ? 'on' : 'off';
    const bgColor = document.getElementById('bgColor').value;
    const degree = document.getElementById('degree').value;
    const flipVerticalCheckbox = document.getElementById('flipVertical');
    const flipHorizontalCheckbox = document.getElementById('flipHorizontal');
    const flipVertical = flipVerticalCheckbox.checked ? 'on' : 'off';
    const flipHorizontal = flipHorizontalCheckbox.checked ? 'on' : 'off';
    const luminosity = document.getElementById('luminosity').value;
    const contrast = document.getElementById('contrast').value;

    const uploadInput = document.getElementById('uploadInput');
    const files = uploadInput.files;

    if (files.length === 0) {
        console.error('Aucune image sélectionnée');
        return;
    }

    for (let i = 0; i < files.length; i++) {
        formData.append('images', files[i]);
    }

    formData.append('resizeOptions', resizeOptions);
    formData.append('removeBg', removeBg);
    formData.append('bgColor', bgColor);
    formData.append('degree', degree);
    formData.append('flipVertical', flipVertical);
    formData.append('flipHorizontal', flipHorizontal);
    formData.append('luminosity', luminosity);
    formData.append('contrast', contrast);

    // Afficher l'image downloading.gif pendant le traitement et téléchargement
    imagePreviewElement.src = downloadingGifUrl;

    fetch('/process-images/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Inclure le jeton CSRF
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob().then(blob => {
            const contentType = response.headers.get('Content-Type');
            const contentDisposition = response.headers.get('Content-Disposition');
            const filenameMatch = contentDisposition && contentDisposition.match(/filename="(.+)"/);
            const filename = filenameMatch ? filenameMatch[1] : (contentType === 'application/zip' ? 'processed_images.zip' : 'processed_image.png');

            // Traiter la réponse, par exemple télécharger le fichier
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename; // Nom du fichier selon le type de contenu
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url); // Nettoyer l'URL après le téléchargement

            // Afficher la première image traitée (ou toute autre image de votre choix)
            const imgBlobUrl = window.URL.createObjectURL(blob);
            imagePreviewElement.src = imgBlobUrl;
        });
    })
    .catch(error => console.error('Error:', error));
});

// GESTION DE L'AFFICHAGE SUR MOBILE
document.querySelectorAll('#plt_phone i').forEach(icon => {
    icon.addEventListener('click', function() {
        const targetId = this.getAttribute('data-target');
        const targetPopup = document.querySelector(targetId);

        if (targetPopup.classList.contains('active')) {
            // Si le popup est déjà actif, le fermer
            targetPopup.classList.remove('active');
        } else {
            // Fermer les autres popups
            document.querySelectorAll('.popup').forEach(popup => popup.classList.remove('active'));

            // Afficher le popup correspondant
            targetPopup.classList.add('active');
        }
    });
});

document.addEventListener('click', function(e) {
    if (!e.target.closest('#plt_phone') && !e.target.closest('.popup')) {
        document.querySelectorAll('.popup').forEach(popup => popup.classList.remove('active'));
    }
});

// GESTION DES FEEDBACK
$('#feedbackForm').on('submit', function(e) {
    e.preventDefault();
    
    const name = $('#name').val();
    const email = $('#email').val();
    const feedback = $('#feedback').val();
    
    $.ajax({
        type: 'POST',
        url: '{% url "feedback" %}',
        data: {
            'name': name,
            'email': email,
            'feedback': feedback,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(response) {
            alert(response.message);
            $('#feedbackForm')[0].reset();
        },
        error: function(xhr) {
            alert('Une erreur s\'est produite. Veuillez réessayer.');
        }
    });
});

// GESTION CHARGEMENT DES IMAGES (UPLOAD)
document.getElementById('uploadInput').addEventListener('change', function() {
    const imagePreviewElement = document.getElementById('imagePreview');
    const imageFormElement = document.getElementById('imageForm');
    const dropZoneElement = document.getElementById('dropZone'); // Sélectionnez la zone de dépôt
    
    if (this.files) {
        // Cacher la background-image
        dropZoneElement.style.backgroundImage = 'none'; // Enlève ou cache l'image de fond
        
        const formData = new FormData();
        Array.from(this.files).forEach(file => {
            formData.append('images', file);
        });

        // Envoyer l'image au serveur pour stockage temporaire
        fetch('/upload-image/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Inclure le jeton CSRF
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Sauvegarder l'URL de l'image temporaire pour la prévisualisation
            imagePreviewElement.setAttribute('data-temp-url', data.temp_url);

            // Afficher l'image en prévisualisation depuis l'URL temporaire
            imagePreviewElement.src = data.temp_url;
            imagePreviewElement.style.display = 'block';
            imageFormElement.style.display = 'none';

            // Réinitialiser l'état des widgets après un upload réussi
            initialise_state();
        })
        .catch(error => console.error('Error:', error));
    }
});


// GESTION DES IMAGES DÉPOSÉES DANS LE CADRE POUR TRAITEMENT (img)
const dropZone = document.getElementById('dropZone');
const uploadInput = document.getElementById('uploadInput');
const imagePreview = document.getElementById('imagePreview');

dropZone.addEventListener('click', () => {
    uploadInput.click();
});

uploadInput.addEventListener('change', () => {
    handleFiles(uploadInput.files);
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    const dataTransfer = new DataTransfer();

    for (let i = 0; i < files.length; i++) {
        dataTransfer.items.add(files[i]);
    }

    uploadInput.files = dataTransfer.files;
    const event = new Event('change');
    uploadInput.dispatchEvent(event);
});

function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            dropZone.querySelector('label').style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

function initialise_state() {
    // Réinitialiser la sélection de résolution
    document.getElementById('resizeOptions').selectedIndex = 0; // Réinitialise à la première option

    // Réinitialiser l'arrière-plan
    document.getElementById('removeBgCheckbox').checked = false; // Désactiver la case à cocher pour supprimer l'arrière-plan
    document.getElementById('bgColor').value = "#ffffff"; // Réinitialiser la couleur d'arrière-plan à blanc

    // Réinitialiser la rotation
    document.getElementById('degree').value = 0; // Remettre à 0
   
    // Réinitialiser le flip vertical et horizontal
    document.getElementById('flipVertical').checked = false; // Désactiver flip vertical
    document.getElementById('flipHorizontal').checked = false; // Désactiver flip horizontal

    // Réinitialiser luminosité et contraste
    document.getElementById('luminosity').value = 0; // Réinitialiser luminosité à 0
    document.getElementById('luminosityValue').innerText = 0; // Afficher la valeur de luminosité
    document.getElementById('contrast').value = 0; // Réinitialiser contraste à 0
    document.getElementById('contrastValue').innerText = 0; // Afficher la valeur de contraste
}



/*----------------------------------------------------------------
        SUPPRIMER DERNIÈRE IMAGE TEMPORAIRE
------------------------------------------------------------------*/
window.addEventListener('beforeunload', function () {
    // Envoyer une requête pour signaler la fermeture de la page
    navigator.sendBeacon('/delete_temp_image/');
});