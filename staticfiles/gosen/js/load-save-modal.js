// Modal de chargement de sauvegarde - Version amelioree

// Ouvrir la modal de chargement
function showLoadSaveModal() {
    const modal = document.getElementById('load-save-modal');
    if (modal) {
        modal.style.display = 'flex';
        loadSavesForModal();
    } else {
        console.error('Modal load-save-modal non trouve');
        alert('Erreur: modal non disponible');
    }
}

// Fermer la modal de chargement
function closeLoadSaveModal() {
    const modal = document.getElementById('load-save-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Charger les sauvegardes pour la modal
async function loadSavesForModal() {
    try {
        const response = await fetch('/api/sauvegardes/list/');
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        const result = await response.json();
        if (result.success) {
            displaySavesInModal(result.sauvegardes);
        } else {
            console.error('Erreur API:', result.error);
            const container = document.getElementById('load-save-list');
            if (container) {
                container.innerHTML = '<p style="text-align: center; color: #f44336; padding: 20px;">Erreur: ' + (result.error || 'Erreur inconnue') + '</p>';
            }
        }
    } catch (e) {
        console.error('Erreur fetch:', e);
        const container = document.getElementById('load-save-list');
        if (container) {
            container.innerHTML = '<p style="text-align: center; color: #f44336; padding: 20px;">Erreur de connexion au serveur</p>';
        }
    }
}

// Afficher les sauvegardes dans la modal
function displaySavesInModal(sauvegardes) {
    const container = document.getElementById('load-save-list');
    if (!container) return;

    if (sauvegardes.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #888; padding: 20px;">Aucune sauvegarde disponible. Sauvegardez une configuration pour pouvoir la charger ici.</p>';
        return;
    }

    container.innerHTML = sauvegardes.map(s => `
        <div class="save-item" style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 10px 0; cursor: pointer; transition: all 0.2s;" onclick="loadFromModal(${s.id})">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <strong style="color: var(--primary-color); font-size: 1rem;">${escapeHtml(s.nom)}</strong>
                    <div style="font-size: 0.85rem; color: #666; margin-top: 5px;">
                        📅 ${new Date(s.date_modification).toLocaleDateString('fr-FR')} ${new Date(s.date_modification).toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'})}
                    </div>
                    <div style="font-size: 0.8rem; margin-top: 5px;">
                        <span style="color: #666;">${s.num_partants} partants | ${s.taille_combinaison} combinaisons</span>
                        ${s.a_arrivee ? '<span style="color: green; margin-left: 10px;">✓ Arrivée: [' + s.arrivee.join(', ') + ']</span>' : '<span style="color: #999; margin-left: 10px;">Sans arrivée</span>'}
                    </div>
                </div>
                <div style="color: var(--primary-color); font-size: 1.5rem;">→</div>
            </div>
        </div>
    `).join('');
}

// Charger une sauvegarde depuis la modal
async function loadFromModal(id) {
    try {
        const response = await fetch('/api/sauvegardes/load/' + id + '/');
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        const result = await response.json();

        if (result.success) {
            const s = result.sauvegarde;

            // Restaurer la configuration
            if (typeof numPartantsInput !== 'undefined') {
                numPartantsInput.value = s.num_partants;
            }
            if (typeof tailleCombinaisonInput !== 'undefined') {
                tailleCombinaisonInput.value = s.taille_combinaison;
            }
            if (typeof pronosticsTextarea !== 'undefined') {
                pronosticsTextarea.value = formatPronosticsFromData(s.pronostics);
                if (typeof parsePronostics === 'function') {
                    parsePronostics();
                }
                if (typeof restoreGroupMinMax === 'function') {
                    restoreGroupMinMax(s.pronostics);
                }
            }
            if (typeof restoreFilters === 'function') {
                console.log('[LOAD] criteres_filtres:', JSON.stringify(s.criteres_filtres, null, 2));
                restoreFilters(s.criteres_filtres);
            }
            if (typeof currentFilteredCombinations !== 'undefined') {
                currentFilteredCombinations = s.combinaisons_filtres || [];
            }

            // Restaurer l'arrivée si disponible
            if (s.arrivee && s.arrivee.length > 0 && typeof backtestInput !== 'undefined') {
                backtestInput.value = s.arrivee.join(', ');
                if (s.combinaisons_filtres && s.combinaisons_filtres.length > 0 && typeof runBacktestAnalysis === 'function') {
                    runBacktestAnalysis();
                }
            }

            closeLoadSaveModal();
            alert('✅ Configuration chargée : ' + s.nom);
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    } catch (e) {
        console.error(e);
        alert('Erreur de connexion');
    }
}

// Fonction utilitaire pour échapper le HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Fonction utilitaire pour formater les pronostics (si elle n'existe pas déjà)
if (typeof formatPronosticsFromData === 'undefined') {
    window.formatPronosticsFromData = function(pronostics) {
        if (!pronostics || pronostics.length === 0) return '';
        if (typeof pronostics === 'string') return pronostics;
        return pronostics.map(g => g.name + ' : ' + (g.horses || []).join(', ')).join('\n');
    };
}

// Attacher les event listeners quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    // Attendre un peu pour s'assurer que tous les scripts sont chargés
    setTimeout(function() {
        const quickLoadBtn = document.getElementById('quick-load-save-btn');
        if (quickLoadBtn) {
            quickLoadBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                showLoadSaveModal();
            });
            console.log('[LoadSave] Event listener attache au bouton quick-load-save-btn');
        } else {
            console.warn('[LoadSave] Bouton quick-load-save-btn non trouve');
        }
    }, 500);
});

// Fermer la modal en cliquant à l'extérieur
document.addEventListener('click', function(e) {
    const modal = document.getElementById('load-save-modal');
    if (modal && e.target === modal) {
        closeLoadSaveModal();
    }
});

// Rendre la fonction globalement accessible
window.showLoadSaveModal = showLoadSaveModal;
window.closeLoadSaveModal = closeLoadSaveModal;
window.loadFromModal = loadFromModal;
