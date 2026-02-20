// ============================================
// GESTION DES CONFIGURATIONS SAUVEGARDÉES
// ============================================
const SAVED_CONFIGS_KEY = 'turfFilterSavedConfigs';

function getSavedConfigs() {
    const saved = localStorage.getItem(SAVED_CONFIGS_KEY);
    return saved ? JSON.parse(saved) : [];
}

function saveConfigs(configs) {
    localStorage.setItem(SAVED_CONFIGS_KEY, JSON.stringify(configs));
}

function getCurrentFiltersFromDOM() {
    const filters = [];
    const filterBoxes = document.querySelectorAll('.filter-box');

    filterBoxes.forEach((box, idx) => {
        const filterName = box.querySelector('h3')?.textContent || 'Filtre ' + (idx + 1);
        const isEnabled = box.querySelector('.filter-enable')?.checked || false;
        const filterType = box.classList.contains('standard-filter') ? 'standard' :
                          box.classList.contains('advanced-filter') ? 'advanced' :
                          box.classList.contains('weight-filter') ? 'weight' :
                          box.classList.contains('statistic-filter') ? 'statistic' :
                          box.classList.contains('alternance-filter') ? 'alternance' : 'unknown';

        const filterData = {
            filterName: filterName,
            type: filterType,
            enabled: isEnabled
        };

        if (filterType === 'standard' || filterType === 'advanced') {
            filterData.chevauxMin = box.querySelector('.chevaux-min')?.value || '';
            filterData.groupesMin = box.querySelector('.groupes-min')?.value || '';
        } else if (filterType === 'weight') {
            filterData.source = box.querySelector('.weight-source')?.value || '';
            filterData.poidsMin = box.querySelector('.weight-min')?.value || '';
            filterData.poidsMax = box.querySelector('.weight-max')?.value || '';
        } else if (filterType === 'statistic') {
            filterData.subfilters = {};
            const evenOdd = box.querySelector('[data-subfilter="evenOdd"]');
            if (evenOdd) {
                filterData.subfilters.evenOdd = {
                    enabled: evenOdd.checked,
                    evenMin: box.querySelector('.even-min')?.value || '',
                    evenMax: box.querySelector('.even-max')?.value || ''
                };
            }
            const smallLarge = box.querySelector('[data-subfilter="smallLarge"]');
            if (smallLarge) {
                filterData.subfilters.smallLarge = {
                    enabled: smallLarge.checked,
                    smallMin: box.querySelector('.small-min')?.value || '',
                    smallMax: box.querySelector('.small-max')?.value || ''
                };
            }
            const consecutive = box.querySelector('[data-subfilter="consecutive"]');
            if (consecutive) {
                filterData.subfilters.consecutive = {
                    enabled: consecutive.checked,
                    consecutiveMin: box.querySelector('.consecutive-min')?.value || '',
                    consecutiveMax: box.querySelector('.consecutive-max')?.value || ''
                };
            }
        } else if (filterType === 'alternance') {
            filterData.source = box.querySelector('.alternance-source')?.value || '';
            filterData.alternanceMin = box.querySelector('.alternance-min')?.value || '';
            filterData.alternanceMax = box.querySelector('.alternance-max')?.value || '';
        }

        filters.push(filterData);
    });

    return filters;
}

function renderConfigSummary() {
    const container = document.getElementById('config-summary');
    if (!container) return;

    const numPartants = document.getElementById('num-partants')?.value || '-';
    const tailleCombinaison = document.getElementById('taille-combinaison')?.value || '-';
    const filters = getCurrentFiltersFromDOM();

    let filtersHTML = '';
    if (filters.length > 0) {
        filtersHTML = filters.map((filter) => {
            return '<div style="margin-bottom:8px;padding:8px;background:#333;border-radius:5px;">' +
                '<div style="color:var(--primary-color);font-weight:bold;">' + filter.filterName + ' ' + (filter.enabled ? '(actif)' : '(inactif)') + '</div>' +
                '<div style="margin-left:15px;color:#aaa;">- Type: ' + filter.type + '</div>' +
            '</div>';
        }).join('');
    } else {
        filtersHTML = '<div style="color:#888;">Aucun filtre actif</div>';
    }

    container.innerHTML =
        '<div style="background:#2a2a2a;border:1px solid #555;border-radius:8px;padding:15px;margin-bottom:15px;">' +
            '<h4 style="color:var(--primary-color);margin:0 0 10px 0;">Configuration actuelle</h4>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:15px;">' +
                '<div style="background:#333;padding:10px;border-radius:5px;">' +
                    '<div style="color:#888;font-size:0.85rem;">Partants</div>' +
                    '<div style="color:#fff;font-size:1.2rem;font-weight:bold;">' + numPartants + '</div>' +
                '</div>' +
                '<div style="background:#333;padding:10px;border-radius:5px;">' +
                    '<div style="color:#888;font-size:0.85rem;">Taille combinaison</div>' +
                    '<div style="color:#fff;font-size:1.2rem;font-weight:bold;">' + tailleCombinaison + '</div>' +
                '</div>' +
            '</div>' +
            '<div style="background:#333;padding:10px;border-radius:5px;margin-bottom:15px;">' +
                '<div style="color:#888;font-size:0.85rem;">Filtres: ' + filters.length + '</div>' +
            '</div>' +
            '<div style="max-height:200px;overflow-y:auto;">' +
                '<div style="color:#888;font-size:0.85rem;margin-bottom:5px;">Filtres actifs:</div>' +
                filtersHTML +
            '</div>' +
        '</div>';
}

function saveCurrentConfig() {
    const nameInput = document.getElementById('config-name-input');
    const name = nameInput.value.trim();

    if (!name) {
        alert('Nom requis');
        return;
    }

    const config = {
        id: Date.now().toString(),
        name: name,
        date: new Date().toISOString(),
        pronostics: document.getElementById('pronostics').value,
        filters: getCurrentFiltersFromDOM(),
        numPartants: document.getElementById('num-partants').value,
        tailleCombinaison: document.getElementById('taille-combinaison').value
    };

    const configs = getSavedConfigs();
    const existingIndex = configs.findIndex(function(c) { return c.name === name; });

    if (existingIndex >= 0) {
        if (confirm('Remplacer la configuration existante ?')) {
            configs[existingIndex] = config;
        } else {
            return;
        }
    } else {
        configs.unshift(config);
    }

    saveConfigs(configs);
    nameInput.value = '';
    renderSavedConfigs();
    alert('Configuration "' + name + '" sauvegardee avec succes!');
}

function loadConfig(configId) {
    const configs = getSavedConfigs();
    const config = configs.find(function(c) { return c.id === configId; });

    if (!config) return;

    if (config.pronostics) {
        document.getElementById('pronostics').value = config.pronostics;
    }
    if (config.numPartants) {
        document.getElementById('num-partants').value = config.numPartants;
    }
    if (config.tailleCombinaison) {
        document.getElementById('taille-combinaison').value = config.tailleCombinaison;
    }

    closeSavedConfigsModal();
    alert('Configuration "' + config.name + '" chargee! Veuillez recreer les filtres manuellement.');
}

function deleteConfig(configId) {
    const configs = getSavedConfigs();
    const config = configs.find(function(c) { return c.id === configId; });

    if (config && confirm('Supprimer cette configuration ?')) {
        const newConfigs = configs.filter(function(c) { return c.id !== configId; });
        saveConfigs(newConfigs);
        renderSavedConfigs();
    }
}

function renderSavedConfigs() {
    const configs = getSavedConfigs();
    const container = document.getElementById('saved-configs-list');

    if (!container) return;

    if (configs.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#888;padding:20px;">Aucune sauvegarde</p>';
        return;
    }

    container.innerHTML = configs.map(function(config) {
        const date = new Date(config.date).toLocaleDateString('fr-FR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });

        const filtersCount = config.filters ? config.filters.length : 0;
        const safeName = config.name.replace(/'/g, "\\'");
        const safeId = config.id.replace(/'/g, "\\'");

        return '<div class="saved-config-item" data-config-id="' + safeId + '" style="background:#2a2a2a;border:1px solid #444;border-radius:8px;padding:15px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">' +
            '<div>' +
            '<div style="font-weight:bold;color:var(--primary-color);margin-bottom:5px;">' + safeName + '</div>' +
            '<div style="color:#888;font-size:0.85rem;">' + date + '</div>' +
            '<div style="color:#aaa;font-size:0.9rem;margin-top:5px;">Filtres: ' + filtersCount + '</div>' +
            '</div>' +
            '<div class="config-actions" style="display:flex;gap:10px;">' +
            '<button class="btn-load-config" data-config-id="' + safeId + '" style="padding:8px 15px;background:var(--primary-color);color:#000;border:none;border-radius:5px;cursor:pointer;font-weight:bold;">Charger</button>' +
            '<button class="btn-delete-config" data-config-id="' + safeId + '" style="padding:8px 15px;background:var(--danger-color);color:#fff;border:none;border-radius:5px;cursor:pointer;">X</button>' +
            '</div>' +
            '</div>';
    }).join('');

    document.querySelectorAll('.btn-load-config').forEach(function(btn) {
        btn.addEventListener('click', function() {
            loadConfig(this.dataset.configId);
        });
    });

    document.querySelectorAll('.btn-delete-config').forEach(function(btn) {
        btn.addEventListener('click', function() {
            deleteConfig(this.dataset.configId);
        });
    });
}

function openSavedConfigsModal() {
    const modal = document.getElementById('saved-configs-modal');
    if (modal) {
        modal.style.display = 'flex';
        renderConfigSummary();
        renderSavedConfigs();
    }
}

function closeSavedConfigsModal() {
    const modal = document.getElementById('saved-configs-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}
