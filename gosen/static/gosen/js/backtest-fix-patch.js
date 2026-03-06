// Patch pour afficher uniquement le nom et les boutons
(function() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.classList && node.classList.contains('saved-analysis-item')) {
                        fixAnalysisDisplay(node);
                    }
                    if (node.querySelectorAll) {
                        node.querySelectorAll('.saved-analysis-item').forEach(function(item) {
                            fixAnalysisDisplay(item);
                        });
                    }
                });
            }
        });
    });
    
    function fixAnalysisDisplay(item) {
        if (item.hasAttribute('data-fixed')) return;
        item.setAttribute('data-fixed', 'true');
        
        const id = item.dataset.id;
        
        // Masquer la date de creation
        const dateSpan = item.querySelector('.analysis-date');
        if (dateSpan) {
            dateSpan.style.display = 'none';
        }
        
        // Supprimer la ligne Arrivee | Trouve
        const detailsDiv = item.querySelector('.analysis-details');
        if (detailsDiv) {
            detailsDiv.style.display = 'none';
        }
        
        // Ajouter le bouton Modifier
        const actionsDiv = item.querySelector('.analysis-actions');
        if (actionsDiv && !actionsDiv.querySelector('.edit-analysis-btn')) {
            const editBtn = document.createElement('button');
            editBtn.className = 'edit-analysis-btn';
            editBtn.dataset.id = id;
            editBtn.textContent = 'Modifier';
            editBtn.style.background = '#FFA500';
            
            const viewBtn = actionsDiv.querySelector('.view-report-btn');
            if (viewBtn && viewBtn.nextSibling) {
                actionsDiv.insertBefore(editBtn, viewBtn.nextSibling);
            } else {
                actionsDiv.appendChild(editBtn);
            }
            
            editBtn.addEventListener('click', function() {
                editAnalysis(parseInt(id));
            });
        }
    }
    
    window.editAnalysis = async function(id) {
        try {
            const response = await fetch('/api/backtest/load/' + id + '/');
            const result = await response.json();
            
            if (result.success) {
                const a = result.analysis;
                
                const today = new Date().toISOString().split('T')[0];
                const dateCourse = a.date_course || today;
                const arriveeStr = a.arrivee ? a.arrivee.join('-') : '';
                
                const nom = prompt('Modifier le nom:', a.nom || '');
                if (nom === null) return;
                
                const arrivee = prompt('Modifier l\'arrivée (ex: 1-2-3-4-5-6-7-8):', arriveeStr);
                if (arrivee === null) return;
                
                const date = prompt('Modifier la date de la course (YYYY-MM-DD):', dateCourse);
                if (date === null) return;
                
                if (!nom.trim()) {
                    alert('Le nom est requis');
                    return;
                }
                
                let arriveeNum = null;
                if (arrivee.trim()) {
                    arriveeNum = arrivee.trim().split(/[-,\s]+/).map(n => parseInt(n.trim())).filter(n => !isNaN(n));
                    if (arriveeNum.length > 0) {
                        arriveeNum.sort((a, b) => a - b);
                    }
                }
                
                const updateData = { nom: nom.trim(), date_course: date };
                if (arriveeNum && arriveeNum.length > 0) {
                    updateData.arrivee = arriveeNum;
                    
                    const arriveeSet = new Set(arriveeNum);
                    const combinaisons_trouvees = (a.combinaisons_filtrees || []).filter(c => {
                        const s = new Set(c);
                        for (const n of arriveeSet) { if (!s.has(n)) return false; }
                        return true;
                    });
                    updateData.nombre_trouvees = combinaisons_trouvees.length;
                }
                
                const resp = await fetch('/api/backtest/update/' + id + '/', {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                    body: JSON.stringify(updateData)
                });
                
                const res = await resp.json();
                if (res.success) {
                    alert('Sauvegarde mise a jour!');
                    if (typeof loadSavedAnalyses === 'function') {
                        loadSavedAnalyses();
                    }
                } else {
                    alert('Erreur: ' + (res.error || 'Erreur'));
                }
            }
        } catch (e) {
            console.error(e);
            alert('Erreur de connexion');
        }
    };
    
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const parts = cookies[i].trim().split('=');
            if (parts[0] === 'csrftoken') return decodeURIComponent(parts[1]);
        }
        return '';
    }
    
    function startObserver() {
        const container = document.getElementById('saved-analyses-container');
        if (container) {
            observer.observe(container, { childList: true });
            container.querySelectorAll('.saved-analysis-item').forEach(function(item) {
                fixAnalysisDisplay(item);
            });
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startObserver);
    } else {
        startObserver();
    }
    
    console.log('[BACKTEST-FIX] Module charge');
})();
