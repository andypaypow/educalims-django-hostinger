// Fonctions OCR simples - Gemini API
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

var GEMINI_API_KEY = 'AIzaSyDXtdx4b-MawFDi8wUfT4DPgSb9iZwOSEs';

console.log('[OCR] Script charge (Gemini + Tesseract)');
setTimeout(function() {
    var fileInput = document.getElementById('image-upload-input');
    var cameraInput = document.getElementById('camera-input');
    var textarea = document.getElementById('pronostics');
    console.log('[OCR] Init OK');

    function processOCR(file) {
        if (!file) return;

        console.log('[OCR] Fichier:', file.name, file.size, file.type);

        var status = document.getElementById('ocr-status');
        var btn = document.getElementById('upload-image-btn');

        if (!status || !textarea) return;

        status.style.display = 'block';
        status.style.color = 'var(--primary-color)';
        status.textContent = 'Analyse Gemini...';

        var reader = new FileReader();
        reader.onload = function(e) {
            var base64Data = e.target.result.split(',')[1];
            console.log('[OCR] Image convertie');

            var payload = {
                contents: [{
                    parts: [
                        { text: 'Extrais tout le texte de cette image. Retourne SEULEMENT le texte extrait, sans aucun commentaire ni explication. Si aucun texte n est present, retourne une chaine vide.' },
                        { inline_data: { mime_type: file.type || 'image/png', data: base64Data } }
                    ]
                }]
            };

            var models = [
                'gemini-2.5-flash',
                'gemini-2.0-flash',
                'gemini-flash-latest'
            ];

            function tryModel(index) {
                if (index >= models.length) {
                    console.warn('[OCR] Tous les modeles Gemini echouent, fallback Tesseract');
                    status.textContent = 'Fallback Tesseract...';
                    ocrWithTesseract(file, status, textarea, btn);
                    return;
                }

                var model = models[index];
                var url = 'https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent?key=' + GEMINI_API_KEY;
                console.log('[OCR] Essai modele:', model);

                fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })
                .then(function(response) {
                    console.log('[OCR] Gemini', model, 'status:', response.status);
                    if (response.ok) {
                        return response.json();
                    }
                    if (response.status === 404) {
                        throw new Error('MODEL_NOT_FOUND');
                    }
                    return response.json().then(function(e) { throw new Error(e.error?.message || 'HTTP_' + response.status); });
                })
                .then(function(data) {
                    if (data.error) {
                        throw new Error(data.error.message);
                    }
                    if (data.candidates && data.candidates[0] && data.candidates[0].content) {
                        var parts = data.candidates[0].content.parts;
                        var text = '';
                        for (var i = 0; i < parts.length; i++) {
                            if (parts[i].text) text += parts[i].text;
                        }
                        console.log('[OCR] Gemini', model, 'OK!');
                        console.log('[OCR] Texte extrait:', text.substring(0, 50));
                        textarea.value = text.trim();
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        status.textContent = 'Extraction reussie !';
                        status.style.color = 'var(--success-color)';
                        setTimeout(function() { status.style.display = 'none'; }, 3000);
                        btn.disabled = false;
                        if (fileInput) fileInput.value = '';
                        if (cameraInput) cameraInput.value = '';
                    } else {
                        throw new Error('FORMAT_INVALIDE');
                    }
                })
                .catch(function(err) {
                    if (err.message === 'MODEL_NOT_FOUND') {
                        console.log('[OCR] Modele', model, 'non trouve, essai suivant...');
                        tryModel(index + 1);
                    } else {
                        console.warn('[OCR] Erreur', model, ':', err.message);
                        tryModel(index + 1);
                    }
                });
            }

            tryModel(0);
        };
        reader.readAsDataURL(file);
    }

    function ocrWithTesseract(file, status, textarea, btn) {
        function doOCR() {
            if (typeof Tesseract === 'undefined') {
                setTimeout(doOCR, 200);
                return;
            }

            console.log('[OCR] Tesseract start');
            status.textContent = 'Analyse Tesseract...';

            Tesseract.recognize(file, 'fra', {
                logger: function(m) {
                    if (m.status === 'recognizing text') {
                        status.textContent = 'Analyse ' + Math.round(m.progress * 100) + '%';
                    }
                }
            }).then(function(result) {
                console.log('[OCR] Tesseract OK');
                textarea.value = result.data.text;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                status.textContent = 'Extraction reussie !';
                status.style.color = 'var(--success-color)';
                setTimeout(function() { status.style.display = 'none'; }, 3000);
            }).catch(function(err) {
                console.error('[OCR] Erreur:', err);
                status.textContent = 'Erreur: ' + (err.message || 'Echec');
                status.style.color = 'var(--danger-color)';
            }).finally(function() {
                btn.disabled = false;
                if (fileInput) fileInput.value = '';
                if (cameraInput) cameraInput.value = '';
            });
        }

        doOCR();
    }

    function openFileSelector() {
        document.getElementById('image-upload-input').click();
    }

    if (textarea) {
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

        textarea.addEventListener('dblclick', function(e) {
            openFileSelector();
        });

        textarea.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            openFileSelector();
        });

        var touchTimer = null;
        textarea.addEventListener('touchstart', function(e) {
            touchTimer = setTimeout(function() {
                if (navigator.vibrate) navigator.vibrate(50);
                openFileSelector();
            }, 600);
        }, { passive: true });

        textarea.addEventListener('touchend', function() {
            if (touchTimer) { clearTimeout(touchTimer); touchTimer = null; }
        });

        textarea.addEventListener('touchmove', function() {
            if (touchTimer) { clearTimeout(touchTimer); touchTimer = null; }
        }, { passive: true });
    }

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files.length > 0) {
                processOCR(e.target.files[0]);
            }
        });
    }

    if (cameraInput) {
        cameraInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                processOCR(e.target.files[0]);
            }
        });
    }

    console.log('[OCR] Ready - Gemini 2.5 + Tesseract');
}, 1500);
