// Fonctions OCR - Tesseract uniquement (fiable sur Android)
function showOCRModal() {
    console.log('[OCR] showOCRModal');
    var modal = document.getElementById('image-source-modal');
    if (modal) modal.style.display = 'flex';
}

function closeOCRModal() {
    var modal = document.getElementById('image-source-modal');
    if (modal) modal.style.display = 'none';
}

function triggerFileInput() {
    var input = document.getElementById('image-upload-input');
    if (input) input.click();
    closeOCRModal();
}

function triggerCameraInput() {
    var input = document.getElementById('camera-input');
    if (input) input.click();
    closeOCRModal();
}

console.log('[OCR] Script charge (Tesseract uniquement - Android fix)');

setTimeout(function() {
    var fileInput = document.getElementById('image-upload-input');
    var cameraInput = document.getElementById('camera-input');
    var textarea = document.getElementById('pronostics');
    var status = document.getElementById('ocr-status');
    var btn = document.getElementById('upload-image-btn');

    console.log('[OCR] Init OK');

    // Fonction amelioree pour detecter le type MIME
    function getMimeType(file) {
        if (file.type && file.type !== '' && file.type !== 'application/octet-stream') {
            return file.type;
        }
        // Detection par extension
        var ext = file.name.split('.').pop().toLowerCase();
        var mimeTypes = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp'
        };
        return mimeTypes[ext] || 'image/jpeg';
    }

    // Verifier si le fichier est trop gros
    function isFileTooLarge(file) {
        var maxSize = 4 * 1024 * 1024; // 4MB
        return file.size > maxSize;
    }

    // Redimensionner l'image si trop grande
    function resizeImage(file, callback) {
        var img = new Image();
        var reader = new FileReader();

        reader.onload = function(e) {
            img.src = e.target.result;
        };

        img.onload = function() {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');

            // Dimensions max
            var maxDim = 2000;
            var width = img.width;
            var height = img.height;

            if (width > height) {
                if (width > maxDim) {
                    height *= maxDim / width;
                    width = maxDim;
                }
            } else {
                if (height > maxDim) {
                    width *= maxDim / height;
                    height = maxDim;
                }
            }

            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob(function(blob) {
                callback(new File([blob], file.name, {
                    type: 'image/jpeg',
                    lastModified: Date.now()
                }));
            }, 'image/jpeg', 0.85);
        };

        reader.readAsDataURL(file);
    }

    function processOCR(file) {
        if (!file) return;

        console.log('[OCR] Fichier:', file.name, file.size, file.type);

        if (!status || !textarea) {
            console.error('[OCR] Elements manquants');
            return;
        }

        status.style.display = 'block';
        status.style.color = 'var(--primary-color)';

        // Detection mobile
        var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        if (isMobile) {
            console.log('[OCR] Mobile detecte');
        }

        // Verifier type MIME
        var mimeType = getMimeType(file);
        console.log('[OCR] Type MIME:', mimeType);

        // Verifier taille
        if (isFileTooLarge(file)) {
            console.log('[OCR] Fichier trop grand, redimensionnement...');
            status.textContent = 'Redimensionnement...';
            resizeImage(file, function(resizedFile) {
                console.log('[OCR] Fichier redimensionne:', resizedFile.size);
                doOCR(resizedFile);
            });
            return;
        }

        status.textContent = 'Initialisation...';
        doOCR(file);
    }

    function doOCR(file) {
        if (btn) btn.disabled = true;

        // Attendre que Tesseract soit charge
        function checkTesseract() {
            if (typeof Tesseract === 'undefined') {
                console.log('[OCR] Tesseract pas encore charge, attente...');
                status.textContent = 'Chargement OCR...';
                setTimeout(checkTesseract, 500);
                return;
            }
            console.log('[OCR] Tesseract ready');
            runOCR(file);
        }

        function runOCR(file) {
            status.textContent = 'Analyse en cours...';
            status.style.color = 'var(--primary-color)';

            var startTime = Date.now();

            Tesseract.recognize(file, 'fra', {
                logger: function(m) {
                    if (m.status === 'recognizing text') {
                        var progress = Math.round(m.progress * 100);
                        status.textContent = 'Analyse ' + progress + '%';
                        console.log('[OCR] Progress:', progress + '%');
                    } else if (m.status === 'loading tesseract core') {
                        status.textContent = 'Chargement moteur...';
                    } else if (m.status === 'initializing tesseract') {
                        status.textContent = 'Initialisation...';
                    } else if (m.status === 'initializing api') {
                        status.textContent = 'Preparation...';
                    } else if (m.status === 'recognizing text') {
                        status.textContent = 'Reconnaissance...';
                    }
                }
            })
            .then(function(result) {
                var elapsed = Math.round((Date.now() - startTime) / 1000);
                console.log('[OCR] Succes en', elapsed, 's');
                console.log('[OCR] Texte:', result.data.text.substring(0, 100));

                // Afficher le texte extrait
                var extractedText = result.data.text.trim();
                if (extractedText) {
                    textarea.value = extractedText;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    status.textContent = 'Extraction reussie ! (' + elapsed + 's)';
                    status.style.color = 'var(--success-color)';
                } else {
                    status.textContent = 'Aucun texte detecte';
                    status.style.color = 'var(--warning-color)';
                }

                setTimeout(function() {
                    status.style.display = 'none';
                }, 3000);
            })
            .catch(function(err) {
                console.error('[OCR] Erreur:', err);
                status.textContent = 'Erreur: ' + (err.message || 'Echec OCR');
                status.style.color = 'var(--danger-color)';
            })
            .finally(function() {
                if (btn) btn.disabled = false;
                if (fileInput) fileInput.value = '';
                if (cameraInput) cameraInput.value = '';
            });
        }

        checkTesseract();
    }

    function openFileSelector() {
        document.getElementById('image-upload-input').click();
    }

    // Event listeners pour textarea
    if (textarea) {
        // Paste d'image
        textarea.addEventListener('paste', function(e) {
            var items = e.clipboardData.items;
            for (var i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    e.preventDefault();
                    var blob = items[i].getAsFile();
                    processOCR(new File([blob], 'paste.png', { type: blob.type }));
                    break;
                }
            }
        });

        // Double clic
        textarea.addEventListener('dblclick', function(e) {
            openFileSelector();
        });

        // Clic droit
        textarea.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            openFileSelector();
        });

        // Appui long (mobile)
        var touchTimer = null;
        textarea.addEventListener('touchstart', function(e) {
            touchTimer = setTimeout(function() {
                if (navigator.vibrate) navigator.vibrate(50);
                openFileSelector();
            }, 600);
        }, { passive: true });

        textarea.addEventListener('touchend', function() {
            if (touchTimer) {
                clearTimeout(touchTimer);
                touchTimer = null;
            }
        });

        textarea.addEventListener('touchmove', function() {
            if (touchTimer) {
                clearTimeout(touchTimer);
                touchTimer = null;
            }
        }, { passive: true });
    }

    // File inputs
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files.length > 0) {
                processOCR(e.target.files[0]);
            }
        });
    }

    if (cameraInput) {
        cameraInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files.length > 0) {
                processOCR(e.target.files[0]);
            }
        });
    }

    console.log('[OCR] Ready - Tesseract uniquement');
}, 1500);
