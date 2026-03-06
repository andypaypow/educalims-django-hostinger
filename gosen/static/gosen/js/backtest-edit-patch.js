// Patch pour ajouter la fonctionnalite de modification du nom de la sauvegarde
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.classList && node.classList.contains('saved-analysis-item')) {
                            addEditButtonToAnalysis(node);
                        }
                    });
                }
            });
        });
        
        const container = document.getElementById('saved-analyses-container');
        if (container) {
            observer.observe(container, { childList: true });
            container.querySelectorAll('.saved-analysis-item').forEach(function(item) {
                addEditButtonToAnalysis(item);
            });
        }
        
        function addEditButtonToAnalysis(item) {
            if (item.querySelector('.edit-name-btn')) return;
            
            const id = item.dataset.id;
            const actionsDiv = item.querySelector('.analysis-actions');
            if (!actionsDiv) return;
            
            const editBtn = document.createElement('button');
            editBtn.className = 'edit-name-btn';
            editBtn.dataset.id = id;
            editBtn.textContent = 'Modifier Nom';
            editBtn.style.background = '#FFA500';
            
            const viewBtn = actionsDiv.querySelector('.view-report-btn');
            if (viewBtn && viewBtn.nextSibling) {
                actionsDiv.insertBefore(editBtn, viewBtn.nextSibling);
            } else {
                actionsDiv.appendChild(editBtn);
            }
            
            editBtn.addEventListener('click', function() {
                editAnalysisName(parseInt(id));
            });
        }
    });
    
    async function editAnalysisName(id) {
        try {
            const response = await fetch('/api/backtest/load/' + id + '/');
            const result = await response.json();
            
            if (result.success) {
                const analysis = result.analysis;
                const currentName = analysis.nom || '';
                
                const newName = prompt(
                    'Nom actuel: ' + currentName + '\n\n' +
                    'Entrez le nouveau nom:',
                    currentName
                );
                
                if (newName === null) return;
                
                if (newName.trim() === '') {
                    alert('Le nom ne peut pas etre vide.');
                    return;
                }
                
                const updateResponse = await fetch('/api/backtest/update/' + id + '/', {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ nom: newName.trim() })
                });
                
                const updateResult = await updateResponse.json();
                
                if (updateResult.success) {
                    alert('Nom mis a jour avec succes!');
                    if (typeof loadSavedAnalyses === 'function') {
                        loadSavedAnalyses();
                    }
                } else {
                    alert('Erreur: ' + (updateResult.error || 'Erreur inconnue'));
                }
            } else {
                alert('Erreur: ' + (result.error || 'Erreur inconnue'));
            }
        } catch (e) {
            console.error(e);
            alert('Erreur de connexion');
        }
    }
    
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const parts = cookies[i].trim().split('=');
            if (parts[0] === 'csrftoken') return decodeURIComponent(parts[1]);
        }
        return '';
    }
    
    console.log('[BACKTEST-NAME-EDIT-PATCH] Module charge');
})();
