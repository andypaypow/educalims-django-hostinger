// Fonctions OCR simples
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

// Initialisation OCR
console.log('[OCR] Script charge');
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
        status.textContent = 'Analyse...';

        function doOCR() {
            if (typeof Tesseract === 'undefined') {
                setTimeout(doOCR, 200);
                return;
            }

            console.log('[OCR] Start Tesseract');

            Tesseract.recognize(file, 'fra', {
                logger: function(m) {
                    if (m.status === 'recognizing text') {
                        status.textContent = 'Analyse ' + Math.round(m.progress * 100) + '%';
                    }
                }
            }).then(function(result) {
                console.log('[OCR] Succes');
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
        console.log('[OCR] Open selector');
        document.getElementById('image-upload-input').click();
    }

    if (textarea) {
        // Coller (Ctrl+V)
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

        // Double-clic (PC)
        textarea.addEventListener('dblclick', function(e) {
            console.log('[OCR] Double-clic');
            openFileSelector();
        });

        // Clic droit (PC)
        textarea.addEventListener('contextmenu', function(e) {
            console.log('[OCR] Contextmenu');
            e.preventDefault();
            openFileSelector();
        });

        // Appui long (Android)
        var touchTimer = null;
        textarea.addEventListener('touchstart', function(e) {
            touchTimer = setTimeout(function() {
                console.log('[OCR] Long press');
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

    // File input avec gestion Android
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            console.log('[OCR] Input change, files:', e.target.files.length);
            
            if (e.target.files && e.target.files.length > 0) {
                var file = e.target.files[0];
                console.log('[OCR] File selected:', file.name, file.size, file.type);
                
                // Fix Android: verifier que le fichier est valide
                if (file.size === 0) {
                    console.error('[OCR] File empty!');
                    var status = document.getElementById('ocr-status');
                    if (status) {
                        status.style.display = 'block';
                        status.textContent = 'Fichier vide - Reessayez';
                        status.style.color = 'red';
                    }
                    return;
                }
                
                // Convertir en Blob si necessaire pour Android
                if (file instanceof File) {
                    processOCR(file);
                } else {
                    // Fallback pour Android
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        var blob = new Blob([e.target.result], { type: file.type || 'image/jpeg' });
                        processOCR(new File([blob], file.name || 'image.jpg', { type: blob.type }));
                    };
                    reader.onerror = function() {
                        console.error('[OCR] FileReader error');
                        var status = document.getElementById('ocr-status');
                        if (status) {
                            status.style.display = 'block';
                            status.textContent = 'Erreur lecture fichier';
                            status.style.color = 'red';
                        }
                    };
                    reader.readAsArrayBuffer(file);
                }
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

    console.log('[OCR] Ready');
}, 1500);
