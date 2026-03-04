/**
 * Module de gestion des configurations sauvegardées
 * Système indépendant du backtest
 */

document.addEventListener('DOMContentLoaded', () => {
    // ===== ÉLÉMENTS DU DOM =====
    const saveNameInput = document.getElementById('saved-config-name');
    const saveBtn = document.getElementById('btn-save-current-config');
    const configsList = document.getElementById('saved-configs-list');

    // Modal d'édition
    const editModal = document.getElementById('edit-saved-config-modal');
    const editIdInput = document.getElementById('edit-config-id');
    const editNameInput = document.getElementById('edit-config-name');
    const editReunionInput = document.getElementById('edit-config-reunion');
    const editDateInput = document.getElementById('edit-config-date');
    const editArrivalInput = document.getElementById('edit-config-arrival');
    const btnSaveEdit = document.getElementById('btn-save-edit-config');
    const btnCancelEdit = document.getElementById('btn-cancel-edit-config');
    const btnCloseEditModal = document.getElementById('btn-close-edit-modal');

    // ===== FONCTIONS =====

    /**
     * Collecte les critères de filtres actuels
     * Utilise la structure existante de main.js
     */
    function collectFilterCriteria() {
        const criteria = { filters: [] };

        document.querySelectorAll('.filter-box').forEach(box => {
            const h3 = box.querySelector('h3');
            if (!h3) return;

            const f = {
                title: h3.textContent,
                enabled: box.querySelector('.filter-enable')?.checked || false,
                type: null,
                params: {}
            };

            if (box.classList.contains('standard-filter') || box.classList.contains('advanced-filter')) {
                f.type = 'expert';
                f.params = {
                    chevaux_min: box.querySelector('.chevaux-min')?.value,
                    groupes_min: box.querySelector('.groupes-min')?.value
                };
            } else if (box.classList.contains('weight-filter')) {
                f.type = 'weight';
                f.params = {
                    source: box.querySelector('.weight-source')?.value,
                    poids_min: box.querySelector('.weight-min')?.value,
                    poids_max: box.querySelector('.weight-max')?.value
                };
            } else if (box.classList.contains('alternance-filter')) {
                f.type = 'alternance';
                f.params = {
                    source: box.querySelector('.alternance-source')?.value,
                    alternances_min: box.querySelector('.alternance-min')?.value,
                    alternances_max: box.querySelector('.alternance-max')?.value
                };
            } else if (box.classList.contains('statistic-filter')) {
                f.type = 'statistic';
                f.params = {
                    evenOdd: box.querySelector('[data-subfilter="evenOdd"]')?.checked,
                    even_min: box.querySelector('.even-min')?.value,
                    even_max: box.querySelector('.even-max')?.value,
                    smallLarge: box.querySelector('[data-subfilter="smallLarge"]')?.checked,
                    small_min: box.querySelector('.small-min')?.value,
                    small_max: box.querySelector('.small-max')?.value,
                    consecutive: box.querySelector('[data-subfilter="consecutive"]')?.checked,
                    consecutive_min: box.querySelector('.consecutive-min')?.value,
                    consecutive_max: box.querySelector('.consecutive-max')?.value
                };
            }

            criteria.filters.push(f);
        });

        return criteria;
    }

    /**
     * Sauvegarde la configuration actuelle
     */
    async function saveCurrentConfig() {
        const name = saveNameInput.value.trim();
        if (!name) {
            alert('Veuillez entrer un nom pour la configuration');
            return;
        }

        const numPartants = document.getElementById('num-partants')?.value || 16;
        const tailleCombinaison = document.getElementById('taille-combinaison')?.value || 6;
        const pronosticsText = document.getElementById('pronostics')?.value || '';

        const payload = {
            nom: name,
            num_partants: parseInt(numPartants),
            taille_combinaison: parseInt(tailleCombinaison),
            pronostics_text: pronosticsText,
            criteres_filtres: collectFilterCriteria()
        };

        try {
            const response = await fetch('/api/saved-configs/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {
                alert('Configuration sauvegardée avec succès !');
                saveNameInput.value = '';
                loadSavedConfigsList();
            } else {
                alert('Erreur: ' + (result.error || 'Erreur inconnue'));
            }
        } catch (error) {
            console.error('Erreur de sauvegarde:', error);
            alert('Erreur lors de la sauvegarde');
        }
    }

    /**
     * Charge la liste des configurations sauvegardées
     */
    async function loadSavedConfigsList() {
        try {
            const response = await fetch('/api/saved-configs/list/');
            const result = await response.json();

            if (result.success) {
                renderSavedConfigsList(result.configs);
            } else {
                configsList.innerHTML = '<p style="color: #888; text-align: center;">Erreur de chargement</p>';
            }
        } catch (error) {
            console.error('Erreur de chargement:', error);
            configsList.innerHTML = '<p style="color: #888; text-align: center;">Erreur de chargement</p>';
        }
    }

    /**
     * Affiche la liste des configurations
     */
    function renderSavedConfigsList(configs) {
        if (!configs || configs.length === 0) {
            configsList.innerHTML = '<p style="color: #888; text-align: center; padding: 20px;">Aucune configuration sauvegardée</p>';
            return;
        }

        configsList.innerHTML = configs.map(config => {
            const date = new Date(config.created_at).toLocaleDateString('fr-FR', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });

            return `
                <div class="saved-config-item">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4>${escapeHtml(config.nom)}</h4>
                            <div style="color: #888; font-size: 0.9rem;">
                                ${config.num_partants} partants | Combinaison de ${config.taille_combinaison}
                            </div>
                            <div style="color: #666; font-size: 0.85rem; margin-top: 5px;">${date}</div>
                            ${config.reunion || config.date_course || config.has_arrivee ? `
                                <div style="margin-top: 8px; display: flex; gap: 5px; flex-wrap: wrap;">
                                    ${config.reunion ? `<span class="badge">${escapeHtml(config.reunion)}</span>` : ''}
                                    ${config.date_course ? `<span class="badge">${config.date_course}</span>` : ''}
                                    ${config.has_arrivee ? '<span class="badge" style="background: rgba(0, 158, 96, 0.2); color: var(--primary-color);">Avec arrivée</span>' : ''}
                                </div>
                            ` : ''}
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <button onclick="window.loadConfig(${config.id})" class="add-filter-btn" style="padding: 8px 12px; font-size: 0.9rem;" title="Charger">📂</button>
                            <button onclick="window.editConfig(${config.id})" class="add-filter-btn" style="padding: 8px 12px; font-size: 0.9rem; background: #FFA500;" title="Modifier">✏️</button>
                            <button onclick="window.deleteConfig(${config.id})" class="add-filter-btn" style="padding: 8px 12px; font-size: 0.9rem; background: var(--danger-color, #e74c3c);" title="Supprimer">🗑️</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Charge et restaure une configuration
     */
    window.loadConfig = async function(configId) {
        try {
            const response = await fetch(`/api/saved-configs/load/${configId}/`);
            const result = await response.json();

            if (result.success) {
                const config = result.config;

                // Restaurer la configuration de base
                document.getElementById('num-partants').value = config.num_partants;
                document.getElementById('taille-combinaison').value = config.taille_combinaison;
                document.getElementById('pronostics').value = config.pronostics_text;

                // Déclencher le parsing des pronostics
                if (typeof window.parsePronostics === 'function') {
                    window.parsePronostics();
                }

                // Restaurer les filtres
                restoreFilters(config.criteres_filtres);

                // Basculer vers l'onglet Résultats
                document.querySelector('[data-tab="results-tab-content"]')?.click();

                alert('Configuration chargée avec succès !');
            } else {
                alert('Erreur: ' + (result.error || 'Configuration non trouvée'));
            }
        } catch (error) {
            console.error('Erreur de chargement:', error);
            alert('Erreur lors du chargement');
        }
    };

    /**
     * Restaure les filtres à partir des critères sauvegardés
     */
    function restoreFilters(criteria) {
        // Supprimer tous les filtres existants
        document.querySelectorAll('.filter-box').forEach(box => box.remove());

        if (!criteria || !criteria.filters) return;

        // Recréer chaque filtre
        criteria.filters.forEach(filter => {
            if (!filter.enabled) return;

            let type = 'standard';
            if (filter.type === 'weight') type = 'weight';
            else if (filter.type === 'statistic') type = 'statistic';
            else if (filter.type === 'alternance') type = 'alternance';

            // Utiliser la fonction addFilter existante
            if (typeof window.addFilter === 'function') {
                window.addFilter(type);

                // Remplir les paramètres
                setTimeout(() => {
                    const boxes = document.querySelectorAll('.filter-box');
                    const lastBox = boxes[boxes.length - 1];

                    if (filter.type === 'expert' && lastBox) {
                        const minInput = lastBox.querySelector('.chevaux-min');
                        const groupsInput = lastBox.querySelector('.groupes-min');
                        if (minInput && filter.params.chevaux_min) minInput.value = filter.params.chevaux_min;
                        if (groupsInput && filter.params.groupes_min) groupsInput.value = filter.params.groupes_min;
                    }
                    // Ajouter les autres types de filtres selon besoins
                }, 100);
            }
        });

        // Mettre à jour la synthèse
        if (typeof window.updateSynthesis === 'function') {
            window.updateSynthesis();
        }
    }

    /**
     * Ouvre le modal d'édition
     */
    window.editConfig = async function(configId) {
        try {
            const response = await fetch(`/api/saved-configs/load/${configId}/`);
            const result = await response.json();

            if (result.success) {
                const config = result.config;

                editIdInput.value = config.id;
                editNameInput.value = config.nom;
                editReunionInput.value = config.reunion || '';
                editDateInput.value = config.date_course || '';
                editArrivalInput.value = config.arrivee ? config.arrivee.join('-') : '';

                editModal.style.display = 'flex';
            } else {
                alert('Erreur: ' + (result.error || 'Configuration non trouvée'));
            }
        } catch (error) {
            console.error('Erreur de chargement:', error);
            alert('Erreur lors du chargement');
        }
    };

    /**
     * Sauvegarde les modifications
     */
    async function saveEditedConfig() {
        const configId = editIdInput.value;

        // Parser l'arrivée
        let arrivee = null;
        const arrivalText = editArrivalInput.value.trim();
        if (arrivalText) {
            arrivee = arrivalText.split(/[-,\s]+/)
                .map(n => parseInt(n.trim()))
                .filter(n => !isNaN(n));
            if (arrivee.length === 0) arrivee = null;
        }

        const payload = {
            nom: editNameInput.value,
            reunion: editReunionInput.value,
            date_course: editDateInput.value,
            arrivee: arrivee
        };

        try {
            const response = await fetch(`/api/saved-configs/update/${configId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {
                alert('Configuration mise à jour avec succès !');
                closeEditModal();
                loadSavedConfigsList();
            } else {
                alert('Erreur: ' + (result.error || 'Erreur inconnue'));
            }
        } catch (error) {
            console.error('Erreur de mise à jour:', error);
            alert('Erreur lors de la mise à jour');
        }
    }

    /**
     * Supprime une configuration
     */
    window.deleteConfig = async function(configId) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cette configuration ?')) {
            return;
        }

        try {
            const response = await fetch(`/api/saved-configs/delete/${configId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                alert('Configuration supprimée avec succès !');
                loadSavedConfigsList();
            } else {
                alert('Erreur: ' + (result.error || 'Erreur inconnue'));
            }
        } catch (error) {
            console.error('Erreur de suppression:', error);
            alert('Erreur lors de la suppression');
        }
    };

    /**
     * Ferme le modal d'édition
     */
    function closeEditModal() {
        editModal.style.display = 'none';
    }

    /**
     * Récupère le token CSRF
     */
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (const cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return decodeURIComponent(value);
        }
        return '';
    }

    /**
     * Échappe les caractères HTML
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ===== EVENT LISTENERS =====

    saveBtn?.addEventListener('click', saveCurrentConfig);

    btnSaveEdit?.addEventListener('click', saveEditedConfig);
    btnCancelEdit?.addEventListener('click', closeEditModal);
    btnCloseEditModal?.addEventListener('click', closeEditModal);

    editModal?.addEventListener('click', (e) => {
        if (e.target === editModal) closeEditModal();
    });

    // Charger la liste quand on affiche l'onglet
    document.querySelector('[data-tab="saved-tab-content"]')?.addEventListener('click', () => {
        loadSavedConfigsList();
    });

    // Charger la liste au démarrage si l'onglet est actif
    if (document.querySelector('#saved-tab-content')?.style.display !== 'none') {
        loadSavedConfigsList();
    }
});
