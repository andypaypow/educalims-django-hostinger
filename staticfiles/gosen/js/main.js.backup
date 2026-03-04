        document.addEventListener('DOMContentLoaded', () => {
            // --- SÉLECTION DES ÉLÉMENTS DU DOM ---
            const numPartantsInput = document.getElementById('num-partants');
            const tailleCombinaisonInput = document.getElementById('taille-combinaison');
            const pronosticsTextarea = document.getElementById('pronostics');
            const totalCombinaisonsInfo = document.getElementById('total-combinaisons-info');
            const parsedGroupsDiv = document.getElementById('parsed-groups');
            const resultsSummaryDiv = document.getElementById('results-summary');
            const resultsOutputDiv = document.getElementById('results-output');
            const loader = document.getElementById('loader');
            
            const filterContainer = document.getElementById('filter-container');
            const uploadImageBtn = document.getElementById('upload-image-btn');
            const imageUploadInput = document.getElementById('image-upload-input');
            const cameraInput = document.getElementById('camera-input');
            const ocrStatus = document.getElementById('ocr-status');

            // --- BACKTEST ELEMENTS ---
            const backtestInput = document.getElementById('backtest-input');
            const runBacktestBtn = document.getElementById('run-backtest-btn');
            const backtestResultsContainer = document.getElementById('backtest-results-container');
            const backtestResultsOutput = document.getElementById('backtest-results-output');
            const saveBacktestBtn = document.getElementById('save-backtest-btn');

            // --- OCR Image Processing ---
            const imageSourceModal = document.getElementById('image-source-modal');
            const selectFileBtn = document.getElementById('select-file-btn');
            const takePhotoBtn = document.getElementById('take-photo-btn');
            const closeImageSourceModalBtn = document.getElementById('close-image-source-modal-btn');

            const handleImageFile = async (file) => {
                if (!file || typeof Tesseract === 'undefined') {
                    if (typeof Tesseract === 'undefined') {
                        console.error('Tesseract.js n\'est pas chargé.');
                        ocrStatus.textContent = 'Erreur: La bibliothèque d\'analyse n\'a pas pu être chargée.';
                        ocrStatus.style.display = 'block';
                    }
                    return;
                }

                ocrStatus.textContent = 'Analyse de l\'image en cours...';
                ocrStatus.style.display = 'block';
                uploadImageBtn.disabled = true;

                try {
                    const { data: { text } } = await Tesseract.recognize(
                        file,
                        'fra', // Langue: Français
                        {
                            logger: m => {
                                if (m.status === 'recognizing text') {
                                    ocrStatus.textContent = `Analyse en cours... ${Math.round(m.progress * 100)}%`;
                                }
                            }
                        }
                    );

                    pronosticsTextarea.value = text;
                    // Déclenche la mise à jour de l'application
                    handlePronosticsTextareaChange();

                    ocrStatus.textContent = 'Texte extrait avec succès !';
                    setTimeout(() => { ocrStatus.style.display = 'none'; }, 3000);

                } catch (error) {
                    console.error('Erreur OCR:', error);
                    ocrStatus.textContent = 'Erreur lors de l\'analyse de l\'image.';
                    setTimeout(() => { ocrStatus.style.display = 'none'; }, 5000);
                } finally {
                    uploadImageBtn.disabled = false;
                    imageUploadInput.value = ''; // Permet de re-télécharger le même fichier
                    cameraInput.value = '';
                }
            };

            if (uploadImageBtn) {
                uploadImageBtn.addEventListener('click', () => {
                    imageSourceModal.style.display = 'flex';
                });
            }

            if (closeImageSourceModalBtn) {
                closeImageSourceModalBtn.addEventListener('click', () => {
                    imageSourceModal.style.display = 'none';
                });
            }

            if (selectFileBtn) {
                selectFileBtn.addEventListener('click', () => {
                    imageUploadInput.click();
                    imageSourceModal.style.display = 'none';
                });
            }

            if (takePhotoBtn) {
                takePhotoBtn.addEventListener('click', () => {
                    cameraInput.click();
                    imageSourceModal.style.display = 'none';
                });
            }

            if (imageUploadInput) {
                imageUploadInput.addEventListener('change', (event) => {
                    const file = event.target.files[0];
                    if (file) {
                        handleImageFile(file);
                    }
                });
            }

            if (cameraInput) {
                cameraInput.addEventListener('change', (event) => {
                    const file = event.target.files[0];
                    if (file) {
                        handleImageFile(file);
                    }
                });
            }

            // --- MODAL ELEMENTS ---
            const addFilterButton = document.getElementById('add-extra-filter');
            const modal = document.getElementById('add-filter-modal');
            const closeModalButton = document.getElementById('close-modal-btn');
            const addStandardFilterBtn = document.getElementById('add-standard-filter-btn');
            const addAdvancedFilterBtn = document.getElementById('add-advanced-filter-btn');
            const addWeightFilterBtn = document.getElementById('add-weight-filter-btn');
            const addStatisticFilterBtn = document.getElementById('add-statistic-filter-btn');
            const addAlternanceFilterBtn = document.getElementById('add-alternance-filter-btn');

            // --- VARIABLES GLOBALES ---
            let worker;
            let debounceTimer;
            let filterIdCounter = 0;
            let synthesisData = { citation: [], position: [], results: [], expert: [] };
            let currentFilteredCombinations = []; // For backtesting

            // --- TEMPLATES DE FILTRE ---
            const standardFilterTemplate = (index) => `
                <div class="filter-box standard-filter" data-id="${index}">
                    <div class="filter-header"><h3>Expert 1</h3><div class="controls"><label class="switch"><input type="checkbox" class="filter-enable" checked><span class="slider"></span></label><button class="remove-filter-btn">&times;</button></div></div>
                    <p class="rule-description">"Garder si au moins <strong>X</strong> chevaux sont dans au moins <strong>Y</strong> groupes"</p>
                    <div class="filter-controls horizontal">
                        <div class="form-group compact"><label> Chevaux min (X):</label><input type="number" class="chevaux-min" value="0" min="0"></div>
                        <div class="form-group compact"><label>Groupes min (Y):</label><input type="number" class="groupes-min" value="0" min="0"></div>
                    </div>
                </div>`;

            const advancedFilterTemplate = (index) => `
                <div class="filter-box advanced-filter" data-id="${index}">
                    <div class="filter-header"><h3>Expert 2</h3><div class="controls"><label class="switch"><input type="checkbox" class="filter-enable" checked><span class="slider"></span></label><button class="remove-filter-btn">&times;</button></div></div>
                    <p class="rule-description">"Garder si au moins <strong>X</strong> chevaux <strong>communs</strong> existent dans au moins <strong>Y</strong> groupes"</p>
                    <div class="filter-controls horizontal">
                        <div class="form-group compact"><label>Chevaux communs min (X):</label><input type="number" class="chevaux-min" value="0" min="0"></div>
                        <div class="form-group compact"><label>Groupes min (Y):</label><input type="number" class="groupes-min" value="0" min="0"></div>
                    </div>
                </div>`;
            
            const weightFilterTemplate = (index) => `
                <div class="filter-box weight-filter" data-id="${index}">
                    <div class="filter-header"><h3>Poids</h3><div class="controls"><label class="switch"><input type="checkbox" class="filter-enable" checked><span class="slider"></span></label><button class="remove-filter-btn">&times;</button></div></div>
                    <div class="filter-controls">
                        <div class="form-group"><label>Source des poids :</label>
                            <select class="form-control weight-source">
                                <option value="default">Par Défaut (N° du cheval)</option>
                                <option value="manual">Sélection Manuelle</option>
                                <option value="citation">Synthèse par Citation</option>
                                <option value="position">Synthèse par Position</option>
                                <option value="results">Synthèse des Chevaux Filtrés</option>
                                <option value="expert">Synthèse de l Expert</option>
                            </select>
                        </div>
                        <div class="form-group manual-input-container" style="display:none;"><label>Liste manuelle des chevaux :</label><textarea class="manual-input" rows="3" placeholder="Saisir les numéros séparés par des espaces, virgules ou tirets..."></textarea></div>
                        <div class="form-group"><label>Poids Total Minimum :</label><input type="number" class="weight-min" value="21"></div>
                        <div class="form-group"><label>Poids Total Maximum :</label><input type="number" class="weight-max" value="81"></div>
                        <div class="weight-range-info" style="font-size: 0.85rem; text-align: center; color: #6c757d;"></div>
                    </div>
                </div>`;

            const statisticFilterTemplate = (index) => `
                <div class="filter-box statistic-filter" data-id="${index}">
                    <div class="filter-header"><h3>Statistiques</h3><div class="controls"><label class="switch"><input type="checkbox" class="filter-enable" checked><span class="slider"></span></label><button class="remove-filter-btn">&times;</button></div></div>
                    <div class="filter-controls">
                        <div class="sub-filter">
                            <label class="switch small-switch"><input type="checkbox" class="sub-filter-enable" data-subfilter="evenOdd" checked><span class="slider"></span></label>
                            <div class="compact">
                                <label>Nb de Pairs entre:</label>
                                <input type="number" class="even-min" value="0" min="0">
                                <span>et</span>
                                <input type="number" class="even-max" value="6" min="0">
                            </div>
                        </div>
                        <div class="sub-filter">
                            <label class="switch small-switch"><input type="checkbox" class="sub-filter-enable" data-subfilter="smallLarge" checked><span class="slider"></span></label>
                            <div class="compact">
                                <label>Nb. Petits (≤ <input type="number" class="limit" value="10" min="1">) entre:</label>
                                <input type="number" class="small-min" value="0" min="0">
                                <span>et</span>
                                <input type="number" class="small-max" value="6" min="0">
                            </div>
                        </div>
                        <div class="sub-filter">
                            <label class="switch small-switch"><input type="checkbox" class="sub-filter-enable" data-subfilter="consecutive" checked><span class="slider"></span></label>
                            <div class="compact">
                                <label>Suite de longueur entre:</label>
                                <input type="number" class="consecutive-min" value="0" min="0">
                                <span>et</span>
                                <input type="number" class="consecutive-max" value="7" min="0">
                            </div>
                        </div>
                    </div>
                </div>`;

            const alternanceFilterTemplate = (index) => `
                <div class="filter-box alternance-filter" data-id="${index}">
                    <div class="filter-header">
                        <h3>Alternance</h3>
                        <div class="controls">
                            <button type="button" class="details-btn info-btn" style="width: 24px; height: 24px; font-size: 0.9rem;" title="Expliquer le filtre d alternance">i</button>
                            <label class="switch"><input type="checkbox" class="filter-enable" checked><span class="slider"></span></label>
                            <button class="remove-filter-btn">&times;</button>
                        </div>
                    </div>
                    <p class="rule-description">"Garder si le nombre d alternances est entre <strong>Min</strong> et <strong>Max</strong>"</p>
                    <div class="filter-controls">
                        <div class="form-group"><label>Source de la liste ordonnée :</label>
                            <select class="form-control alternance-source">
                                <option value="default">Par Défaut (N° du cheval)</option>
                                <option value="manual">Sélection Manuelle</option>
                                <option value="citation">Synthèse par Citation</option>
                                <option value="position">Synthèse par Position</option>
                                <option value="results">Synthèse des Chevaux Filtrés</option>
                                <option value="expert">Synthèse de l Expert</option>
                            </select>
                        </div>
                        <div class="form-group manual-input-container" style="display:none;"><label>Liste manuelle des chevaux (ordre important) :</label><textarea class="manual-input" rows="3" placeholder="Saisir les numéros ordonnés, séparés par des espaces, virgules..."></textarea></div>
                        <div class="form-group"><label>Alternances Minimum :</label><input type="number" class="alternance-min" value="0" min="0"></div>
                        <div class="form-group" style="display: flex; align-items: center; gap: 8px;">
                            <label for="alternance-max-${index}">Alternances Maximum :</label>
                            <input type="number" id="alternance-max-${index}" class="alternance-max" value="5" min="0">
                        </div>
                    </div>
                </div>`;

            // --- FONCTIONS ---

            function combinationsCount(n, k) {
                if (k < 0 || k > n) return 0;
                if (k === 0 || k === n) return 1;
                if (k > n / 2) k = n - k;
                let res = 1;
                for (let i = 1; i <= k; i++) { res = res * (n - i + 1) / i; }
                return Math.round(res);
            }

            function updateTotalCombinaisonsInfo() {
                const n = parseInt(numPartantsInput.value);
                const k = parseInt(tailleCombinaisonInput.value);
                if (n < k || n < 8 || k < 2) { totalCombinaisonsInfo.innerHTML = "Paramètres invalides."; return; }
                const count = combinationsCount(n, k);
                totalCombinaisonsInfo.innerHTML = `<strong>${count.toLocaleString('fr-FR')}</strong> combinaisons possibles`;

                const floatingCounter = document.getElementById('floating-counter');
                if (floatingCounter) {
                    floatingCounter.textContent = `${count.toLocaleString('fr-FR')}/${count.toLocaleString('fr-FR')}`;
                }
            }

            function calculateAlternances(combination, sourceArray) {
                if (sourceArray.length === 0) return 0;
                const combinationSet = new Set(combination.map(String));
                let alternances = 0;
                for (let i = 0; i < sourceArray.length - 1; i++) {
                    const currentIn = combinationSet.has(sourceArray[i]);
                    const nextIn = combinationSet.has(sourceArray[i+1]);
                    if (currentIn !== nextIn) {
                        alternances++;
                    }
                }
                return alternances;
            }

            let currentRawGroups = []; // Global variable to store raw groups

            function parsePronostics() {
                const text = pronosticsTextarea.value.trim();
                const lines = text.split('\n');
                currentRawGroups = lines.map(line => {
                    const parts = line.split(':');
                    let name = `Groupe ${lines.indexOf(line) + 1}`; // Default name
                    let horseNumbers = [];

                    if (parts.length > 1) {
                        name = parts[0].trim();
                        horseNumbers = parts[1].match(/\d+/g) ? [...new Set(parts[1].match(/\d+/g).map(Number))] : [];
                    } else {
                        // If no colon, treat the whole line as numbers
                        horseNumbers = line.match(/\d+/g) ? [...new Set(line.match(/\d+/g).map(Number))] : [];
                        if (horseNumbers.length > 0) {
                            name = `Groupe ${lines.indexOf(line) + 1}`; // Still use default if no explicit name
                        } else {
                            return null; // Skip empty lines
                        }
                    }
                    
                    if (horseNumbers.length === 0) return null; // Skip groups with no horses

                    return { name: name, horses: horseNumbers };
                }).filter(g => g !== null); // Filter out nulls (empty lines or lines with no horses)
                
                return currentRawGroups; // Return raw groups
            }

            function renderParsedGroups(rawGroups) {
                parsedGroupsDiv.innerHTML = rawGroups.map((group, index) => `
                    <div class="group">
                        <span class="group-title">${group.name}:</span>
                        [${group.horses.join(', ')}]
                        <div class="group-filter-controls">
                            <input type="number" class="group-min" value="0" min="0">
                            <span>-</span>
                            <input type="number" class="group-max" value="${group.horses.length}" min="0" max="${group.horses.length}">
                        </div>
                    </div>`).join('');

                // No longer attach event listeners here, handled by handlePronosticsTextareaChange
            }

            function updatePronosticsSyntheses(groups) { // 'groups' here will be currentRawGroups, which are now objects
                if (groups.length === 0) {
                    synthesisData.citation = [];
                    synthesisData.position = [];
                    renderPronosSynthesis('citation', [], 'fois');
                    renderPronosSynthesis('position', [], 'pts');
                    return;
                }
                const citationCounts = {};
                groups.forEach(group => { // Iterate over group objects
                    group.horses.forEach(horse => { // Access horses array
                        citationCounts[horse] = (citationCounts[horse] || 0) + 1;
                    });
                });
                synthesisData.citation = Object.entries(citationCounts).sort((a, b) => b[1] - a[1]);

                const positionScores = {};
                groups.forEach(group => { // Iterate over group objects
                    group.horses.forEach((horse, index) => { // Access horses array
                        positionScores[horse] = (positionScores[horse] || 0) + (group.horses.length - index); // Use group.horses.length
                    });
                });
                synthesisData.position = Object.entries(positionScores).sort((a, b) => b[1] - a[1]);

                renderPronosSynthesis('citation', synthesisData.citation, 'fois');
                renderPronosSynthesis('position', synthesisData.position, 'pts');
            }

            function renderPronosSynthesis(type, sortedData, unit) {
                const compactView = document.getElementById(`${type}-compact-view`);
                const detailsView = document.getElementById(`${type}-details-view`);
                if (!compactView || !detailsView) return;

                if(sortedData.length === 0) {
                    compactView.textContent = 'En attente de pronostics...';
                    detailsView.innerHTML = '';
                    return;
                }

                compactView.textContent = sortedData.map(([horse]) => horse).join(' - ');
                detailsView.innerHTML = sortedData.map(([horse, score]) => `<div class="synthesis-item"><div class="horse-number">${horse}</div><div class="horse-count">${score} ${unit}</div></div>`).join('');
            }

            function calculateAndRenderExpertSynthesis() {
                const { citation, position, results } = synthesisData;
                const expertCompactView = document.getElementById('expert-compact-view');
                const expertDetailsGrid = document.getElementById('expert-details-view').querySelector('.synthesis-output-grid');

                if (citation.length === 0 || position.length === 0 || results.length === 0) {
                    expertCompactView.textContent = 'En attente des résultats du filtrage...';
                    expertDetailsGrid.innerHTML = '';
                    synthesisData.expert = [];
                    return;
                }

                const weights = { citation: 1.0, position: 1.5, results: 2.0 };
                const allHorses = [...new Set([...citation.map(h => h[0]), ...position.map(h => h[0]), ...results.map(h => h[0])])];
                
                const rankPoints = {
                    citation: new Map(citation.map(([h, _], i) => [h, citation.length - i])),
                    position: new Map(position.map(([h, _], i) => [h, position.length - i])),
                    results: new Map(results.map(([h, _], i) => [h, results.length - i]))
                };

                const finalScores = {};
                allHorses.forEach(horse => {
                    const pCitation = rankPoints.citation.get(horse) || 0;
                    const pPosition = rankPoints.position.get(horse) || 0;
                    const pResults = rankPoints.results.get(horse) || 0;
                    finalScores[horse] = (pCitation * weights.citation) + (pPosition * weights.position) + (pResults * weights.results);
                });

                synthesisData.expert = Object.entries(finalScores).sort((a, b) => b[1] - a[1]);

                expertCompactView.textContent = synthesisData.expert.map(([h]) => h).join(' - ');
                expertDetailsGrid.innerHTML = synthesisData.expert.map(([h, s]) => `<div class="synthesis-item"><div class="horse-number">${h}</div><div class="horse-count">${s.toFixed(1)} pts</div></div>`).join('');
            }

            function buildWeightMap(filterBox) {
                const source = filterBox.querySelector('.weight-source').value;
                const n = parseInt(numPartantsInput.value);
                const weightMap = new Map();
                let sortedWeights = [];

                // Initialize all with penalty
                for (let i = 1; i <= n; i++) { weightMap.set(i.toString(), n + 1); }

                switch(source) {
                    case 'default':
                        for(let i=1; i<=n; i++) { weightMap.set(i.toString(), i); }
                        sortedWeights = Array.from({length: n}, (_, i) => i + 1);
                        break;
                    case 'manual':
                        const manualInput = filterBox.querySelector('.manual-input').value;
                        const manualHorses = manualInput.match(/\d+/g) || [];
                        manualHorses.forEach((horse, index) => { weightMap.set(horse, index + 1); });
                        sortedWeights = Array.from({length: manualHorses.length}, (_, i) => i + 1);
                        break;
                    case 'citation':
                    case 'position':
                    case 'results':
                    case 'expert':
                        const synthesisList = synthesisData[source];
                        if (synthesisList.length > 0) {
                            synthesisList.forEach(([horse, _], index) => { weightMap.set(horse, index + 1); });
                            sortedWeights = Array.from({length: synthesisList.length}, (_, i) => i + 1);
                        } else {
                            sortedWeights = []; // No data, no weights
                        }
                        break;
                }
                return { weightMap, sortedWeights };
            }

            function updateAllWeightFiltersUI() {
                document.querySelectorAll('.weight-filter').forEach(box => {
                    const { sortedWeights } = buildWeightMap(box);
                    const k = parseInt(tailleCombinaisonInput.value);
                    const infoDiv = box.querySelector('.weight-range-info');
                    const source = box.querySelector('.weight-source').value;
                    const manualContainer = box.querySelector('.manual-input-container');
                    manualContainer.style.display = source === 'manual' ? 'block' : 'none';

                    if (sortedWeights.length < k) {
                        infoDiv.textContent = source === 'manual' || source === 'default' ? 'Pas assez de chevaux pour une combinaison.' : 'Données de synthèse indisponibles.';
                        return;
                    }
                    const minWeight = sortedWeights.slice(0, k).reduce((a, b) => a + b, 0);
                    const maxWeight = sortedWeights.slice(-k).reduce((a, b) => a + b, 0);
                    infoDiv.textContent = `Poids théorique min: ${minWeight}, max: ${maxWeight}`;
                });
            }

            function updateAlternanceFiltersUI() {
                const k = parseInt(tailleCombinaisonInput.value);
                if (isNaN(k)) return;

                // The theoretical maximum number of alternations for a combination of size k is 2*k.
                // This occurs in a pattern like U,S,U,S...U,S where U=unselected, S=selected.
                const maxAlternances = 2 * k;

                document.querySelectorAll('.alternance-filter').forEach(box => {
                    const maxInput = box.querySelector('.alternance-max');
                    
                    maxInput.max = maxAlternances;
                    maxInput.value = maxAlternances; // Set the value directly
                });
            }

            function updateNumericFilterInputs() {
                const k = parseInt(tailleCombinaisonInput.value);
                if (isNaN(k) || k < 0) return;

                document.querySelectorAll('.statistic-filter').forEach(box => {
                    box.querySelectorAll('input[type="number"]').forEach(input => {
                        if (!input.classList.contains('limit')) { // Ne pas limiter le champ "limite"
                           input.max = k;
                           if (parseInt(input.value) > k) input.value = k; // Ajuster si la valeur est trop haute
                        }
                    });
                });
            }

            async function triggerFilter() {
                const n = parseInt(numPartantsInput.value);
                const k = parseInt(tailleCombinaisonInput.value);

                // Récupérer les groupes de pronostics
                const rawGroups = currentRawGroups;
                const groupsWithMinMax = Array.from(parsedGroupsDiv.children).map((groupDiv, index) => {
                    const minInput = groupDiv.querySelector('.group-min');
                    const maxInput = groupDiv.querySelector('.group-max');
                    return {
                        name: rawGroups[index].name,
                        horses: rawGroups[index].horses,
                        min: parseInt(minInput.value),
                        max: parseInt(maxInput.value)
                    };
                });

                // Récupérer tous les filtres activés
                const orFilters = Array.from(document.querySelectorAll('.standard-filter')).filter(b => b.querySelector('.filter-enable').checked).map(b => ({chevauxMin: parseInt(b.querySelector('.chevaux-min').value), groupesMin: parseInt(b.querySelector('.groupes-min').value) }));
                const andFilters = Array.from(document.querySelectorAll('.advanced-filter')).filter(b => b.querySelector('.filter-enable').checked).map(b => ({chevauxMin: parseInt(b.querySelector('.chevaux-min').value), groupesMin: parseInt(b.querySelector('.groupes-min').value) }));

                const weightFilters = Array.from(document.querySelectorAll('.weight-filter')).filter(b => b.querySelector('.filter-enable').checked).map(b => {
                    const { weightMap } = buildWeightMap(b);
                    const mapForWorker = {};
                    for (let [key, value] of weightMap) { mapForWorker[key] = value; }
                    return {
                        min: parseInt(b.querySelector('.weight-min').value),
                        max: parseInt(b.querySelector('.weight-max').value),
                        map: mapForWorker
                    };
                });

                const alternanceFilters = Array.from(document.querySelectorAll('.alternance-filter')).filter(b => b.querySelector('.filter-enable').checked).map(b => {
                    const source = b.querySelector('.alternance-source').value;
                    const n_val = parseInt(numPartantsInput.value);
                    let sourceArray = [];

                    switch(source) {
                        case 'default':
                            sourceArray = Array.from({length: n_val}, (_, i) => (i + 1).toString());
                            break;
                        case 'manual':
                            const manualInput = b.querySelector('.manual-input').value;
                            sourceArray = (manualInput.match(/\d+/g) || []);
                            break;
                        case 'citation':
                        case 'position':
                        case 'results':
                        case 'expert':
                            const synthesisList = synthesisData[source];
                            if (synthesisList && synthesisList.length > 0) {
                                sourceArray = synthesisList.map(([horse, _]) => horse);
                            }
                            break;
                    }

                    return {
                        min: parseInt(b.querySelector('.alternance-min').value),
                        max: parseInt(b.querySelector('.alternance-max').value),
                        source: sourceArray
                    };
                });

                let evenOddFilters = [];
                let smallLargeFilters = [];
                let consecutiveFilters = [];

                const statisticFilterBox = document.querySelector('.statistic-filter');
                if (statisticFilterBox && statisticFilterBox.querySelector('.filter-enable').checked) {
                    const evenOddSub = statisticFilterBox.querySelector('[data-subfilter="evenOdd"]');
                    if (evenOddSub && evenOddSub.checked) {
                        evenOddFilters.push({
                            min: parseInt(statisticFilterBox.querySelector('.even-min').value),
                            max: parseInt(statisticFilterBox.querySelector('.even-max').value)
                        });
                    }
                    const smallLargeSub = statisticFilterBox.querySelector('[data-subfilter="smallLarge"]');
                    if (smallLargeSub && smallLargeSub.checked) {
                        smallLargeFilters.push({
                            limit: parseInt(statisticFilterBox.querySelector('.limit').value),
                            min: parseInt(statisticFilterBox.querySelector('.small-min').value),
                            max: parseInt(statisticFilterBox.querySelector('.small-max').value)
                        });
                    }
                    const consecutiveSub = statisticFilterBox.querySelector('[data-subfilter="consecutive"]');
                    if (consecutiveSub && consecutiveSub.checked) {
                        consecutiveFilters.push({
                            min: parseInt(statisticFilterBox.querySelector('.consecutive-min').value),
                            max: parseInt(statisticFilterBox.querySelector('.consecutive-max').value)
                        });
                    }
                }

                if (n < k) {
                    resultsSummaryDiv.innerHTML = "La taille de la combinaison ne peut être supérieure au nombre de partants.";
                    resultsOutputDiv.innerHTML = '';
                    displayResults([], combinationsCount(n, k) || 0);
                    return;
                }

                loader.style.display = 'block';
                resultsOutputDiv.innerHTML = '';
                resultsSummaryDiv.innerHTML = 'Filtrage en cours...';

                const floatingCounter = document.getElementById('floating-counter');
                if (floatingCounter) {
                    floatingCounter.textContent = '...';
                }

                // ====== APPEL API CÔTÉ SERVEUR ======
                try {
                    const response = await fetch('/api/filter/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            n, k,
                            groups: groupsWithMinMax,
                            orFilters,
                            andFilters,
                            weightFilters,
                            evenOddFilters,
                            smallLargeFilters,
                            consecutiveFilters,
                            alternanceFilters
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Vérifier si l'utilisateur est abonné
                        if (data.is_subscribed) {
                            displayResults(data.filtered, data.total);
                        } else {
                            // Non abonné : afficher les produits
                            showSubscriptionProducts(data);
                        }
                    } else {
                        // Erreur
                        loader.style.display = 'none';
                        resultsSummaryDiv.innerHTML = `<span style="color: var(--danger-color);">⚠️ ${data.error || 'Erreur lors du filtrage'}</span>`;
                    }
                } catch (error) {
                    loader.style.display = 'none';
                    resultsSummaryDiv.innerHTML = `<span style="color: var(--danger-color);">⚠️ Erreur de connexion au serveur. Vérifiez votre connexion.</span>`;
                    console.error('Erreur:', error);
                }

                loader.style.display = 'none';
            }



            function displayResults(filtered, total) {
                currentFilteredCombinations = filtered.map(c => c.sort((a, b) => a - b)); // Store sorted combinations for backtesting
                const filteredCount = filtered.length;
                const rate = total > 0 ? ((total - filteredCount) / total * 100).toFixed(2) : 0;
                resultsSummaryDiv.innerHTML = `<strong>${filteredCount.toLocaleString('fr-FR')}</strong> combinaisons conservées sur <strong>${total.toLocaleString('fr-FR')}</strong> | Taux de filtrage : <strong style="color: ${rate > 90 ? 'var(--success-color)' : 'var(--danger-color)'}">${rate}%</strong>`;
                resultsOutputDiv.innerHTML = filtered.map(combi => `<span class="combination-item">${combi.join(' - ')}</span>`).join('');

                const floatingCounter = document.getElementById('floating-counter');
                if (floatingCounter) {
                    floatingCounter.textContent = `${filteredCount.toLocaleString('fr-FR')}/${total.toLocaleString('fr-FR')}`;
                }

                const synthesisSection = document.getElementById('synthesis-section');
                const compactView = document.getElementById('synthesis-compact-view');
                const detailsView = document.getElementById('synthesis-details-view');

                if (filteredCount === 0) {
                    synthesisSection.style.display = 'none';
                    synthesisData.results = [];
                } else {
                    const horseCounts = {};
                    filtered.flat().forEach(horse => { horseCounts[horse] = (horseCounts[horse] || 0) + 1; });
                    synthesisData.results = Object.entries(horseCounts).sort((a, b) => b[1] - a[1]);

                    compactView.textContent = synthesisData.results.map(([h]) => h).join(' - ');
                    detailsView.innerHTML = synthesisData.results.map(([h, c]) => `<div class="synthesis-item"><div class="horse-number">${h}</div><div class="horse-count">cité ${c} fois</div></div>`).join('');
                    synthesisSection.style.display = 'block';
                    detailsView.style.display = 'none';
                }
                calculateAndRenderExpertSynthesis();
                updateAllWeightFiltersUI();
            }

            function addFilter(type) {
                filterIdCounter++;
                let template;
                if (type === 'standard') template = standardFilterTemplate(filterIdCounter);
                else if (type === 'advanced') template = advancedFilterTemplate(filterIdCounter);
                else if (type === 'weight') template = weightFilterTemplate(filterIdCounter);
                else if (type === 'statistic') {
                    template = statisticFilterTemplate(filterIdCounter);
                    const btn = document.getElementById('add-statistic-filter-btn');
                    if(btn) btn.disabled = true;
                } 
                else if (type === 'alternance') {
                    template = alternanceFilterTemplate(filterIdCounter);
                }
                else return;

                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = template;
                const newFilter = tempDiv.firstElementChild;
                filterContainer.appendChild(newFilter);

                newFilter.querySelector('.remove-filter-btn').addEventListener('click', () => {
                    newFilter.remove();
                    if (type === 'statistic') {
                        const btn = document.getElementById('add-statistic-filter-btn');
                        if(btn) btn.disabled = false;
                    }
                    handleInputChange();
                });

                if (type === 'alternance') {
                    const infoBtn = newFilter.querySelector('.info-btn');

                    const sourceSelect = newFilter.querySelector('.alternance-source');
                    if (sourceSelect) {
                        sourceSelect.addEventListener('change', () => {
                            const manualContainer = newFilter.querySelector('.manual-input-container');
                            manualContainer.style.display = sourceSelect.value === 'manual' ? 'block' : 'none';
                            handleInputChange(); // Trigger recalculation
                        });
                    }
                    if (infoBtn) {
                        infoBtn.addEventListener('click', (e) => {
                            e.preventDefault();
                            alert("Principe du Filtre d\'Alternance:\n\nCe filtre compte le nombre de 'sauts' entre un cheval sélectionné (S) et un non-sélectionné (N), en parcourant la liste ordonnée des partants.\n\nExemple : Pour la combinaison [1, 3, 5], les sauts sont :\n1(S) > 2(N) > 3(S) > 4(N) > 5(S).\nCela fait 4 alternances.\n\n---\n\nMax Intelligent :\nLe maximum d\'alternances pour une taille K est 2*K. Cette valeur est mise à jour automatiquement.");
                        });
                    }
                }

                updateEventListeners();
                updateNumericFilterInputs();
                updateAlternanceFiltersUI(); // Also call it here to set the initial value
                modal.style.display = 'none';
            }

            function updateEventListeners() {
                // Event listener for pronosticsTextarea
                pronosticsTextarea.removeEventListener('input', handlePronosticsTextareaChange);
                pronosticsTextarea.addEventListener('input', handlePronosticsTextareaChange);

                // Event listeners for other inputs (excluding pronosticsTextarea)
                const otherInputs = document.querySelectorAll('input[type="number"]:not(#pronostics), .filter-enable, .weight-source, .manual-input');
                otherInputs.forEach(input => {
                    input.removeEventListener('input', handleInputChange); // Remove existing to prevent duplicates
                    input.addEventListener('input', handleInputChange);
                    if(input.classList.contains('weight-source')) {
                         input.removeEventListener('change', handleInputChange);
                         input.addEventListener('change', handleInputChange);
                    }
                });
            }

            function handleInputChange() {
                updateTotalCombinaisonsInfo();
                // parsePronostics() and renderParsedGroups() are now called by handlePronosticsTextareaChange
                updatePronosticsSyntheses(currentRawGroups); // Use global raw groups
                calculateAndRenderExpertSynthesis();
                updateAllWeightFiltersUI();
                updateNumericFilterInputs();
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(triggerFilter, 300);
            }

            function handlePronosticsTextareaChange() {
                const rawGroups = parsePronostics(); // Parse and update global currentRawGroups
                renderParsedGroups(rawGroups); // Render the groups with inputs

                // Attach event listeners to the newly created min/max inputs
                parsedGroupsDiv.querySelectorAll('.group-min, .group-max').forEach(input => {
                    input.removeEventListener('input', handleInputChange); // Remove existing to prevent duplicates
                    input.addEventListener('input', handleInputChange); // Now these directly trigger handleInputChange
                });

                handleInputChange(); // Trigger the main filter logic
            }

            // Specific listener for the combination size to update the Alternance Filter UI
            tailleCombinaisonInput.addEventListener('input', () => {
                updateAlternanceFiltersUI();
            });

            // --- BACKTEST LOGIC ---
            function runBacktest() {
                // S'assurer que les pronostics sont bien parsés avec les valeurs actuelles
                parsePronostics();

                // DEBUG: Afficher les groupes dans la console
                console.log('DEBUG: currentRawGroups =', currentRawGroups);

                const arriveeInput = backtestInput.value;
                if (!arriveeInput.trim()) {
                    alert("Veuillez entrer une arrivée à tester.");
                    return;
                }

                const arrivee = arriveeInput.match(/\d+/g).map(Number).sort((a, b) => a - b);
                if (arrivee.length === 0) {
                    alert("L'arrivée entrée est invalide.");
                    return;
                }

                // Find matching combinations
                const arriveeSet = new Set(arrivee);
                const matchingCombinations = currentFilteredCombinations.filter(c => {
                    const combinationSet = new Set(c);
                    for (const num of arriveeSet) {
                        if (!combinationSet.has(num)) return false;
                    }
                    return true;
                });
                const matchingCount = matchingCombinations.length;

                // --- Build Report ---
                let report = `--- RAPPORT DE BACKTEST ---
`;
                report += `Arrivée testée : ${arrivee.join(' - ')}
`;
                report += `Date du test : ${new Date().toLocaleString('fr-FR')}
`;

                // --- Pronostics Saisis ---
                // FORCER l'affichage en reparsant si nécessaire
                if (currentRawGroups.length === 0) {
                    parsePronostics(); // Réessayer
                    console.log('DEBUG: Après retry, currentRawGroups =', currentRawGroups);
                }

                if (currentRawGroups.length > 0) {
                    report += `
--- PRONOSTICS SAISIS ---
`;
                    currentRawGroups.forEach(group => {
                        report += `${group.name} : [${group.horses.join(', ')}]
`;
                    });
                    report += `
`;
                }
                
                // --- Presence Report ---
                report += `
--- STATUT DE PRÉSENCE ---
`;
                if (matchingCount > 0) {
                    report += `✅ TROUVÉE : L'arrivée [${arrivee.join(', ')}] est contenue dans ${matchingCount} combinaison(s) de votre sélection.
`;
                } else {
                    report += `❌ ABSENTE : Aucun des numéros de l'arrivée [${arrivee.join(', ')}] n'a été trouvé ensemble dans une même combinaison de votre sélection.
`;
                }

                // --- Details of Matching Combinations ---
                if (matchingCount > 0) {
                    report += `
--- DÉTAILS DES COMBINAISONS TROUVÉES ---
`;

                    // Pre-fetch active filter settings to avoid recalculating in the loop
                    const activeWeightFilters = Array.from(document.querySelectorAll('.weight-filter:has(.filter-enable:checked)')).map(b => ({ id: b.dataset.id, map: buildWeightMap(b).weightMap }));
                    
                    const activeAlternanceFilters = Array.from(document.querySelectorAll('.alternance-filter:has(.filter-enable:checked)')).map(b => {
                        const source = b.querySelector('.alternance-source').value;
                        const n = parseInt(numPartantsInput.value);
                        let sourceArray = [];
                        switch(source) {
                            case 'default': sourceArray = Array.from({length: n}, (_, i) => (i + 1).toString()); break;
                            case 'manual': sourceArray = (b.querySelector('.manual-input').value.match(/\d+/g) || []); break;
                            default:
                                const synthesisList = synthesisData[source];
                                if (synthesisList && synthesisList.length > 0) sourceArray = synthesisList.map(([h]) => h);
                                break;
                        }
                        return { id: b.dataset.id, source: sourceArray };
                    });

                    matchingCombinations.forEach((combi, index) => {
                        report += `
#${index + 1} Combinaison : [${combi.join(', ')}]
`;
                        
                        // Even numbers
                        const evenCount = combi.filter(num => num % 2 === 0).length;
                        report += `  - Nb. Pairs : ${evenCount}
`;

                        // Weight
                        activeWeightFilters.forEach(wf => {
                            const totalWeight = combi.reduce((sum, horse) => sum + (wf.map.get(horse.toString()) || 0), 0);
                            report += `  - Poids (Filtre #${wf.id}) : ${totalWeight}
`;
                        });

                        // Alternance
                        activeAlternanceFilters.forEach(af => {
                            const alternanceCount = calculateAlternances(combi, af.source);
                            report += `  - Alternances (Filtre #${af.id}) : ${alternanceCount}
`;
                        });
                    });
                }

                // --- Group Analysis ---
                if (currentRawGroups.length > 0) {
                    report += `
--- ANALYSE DES GROUPES (pour l arrivee [${arrivee.join(', ')}] ---
`;
                    const groupAnalysis = {};
                    currentRawGroups.forEach(group => {
                        const intersection = group.horses.filter(h => arrivee.includes(h));
                        const count = intersection.length;
                        if (count > 0) groupAnalysis[count] = (groupAnalysis[count] || 0) + 1;
                    });

                    if (Object.keys(groupAnalysis).length > 0) {
                        for (let i = Math.max(...Object.keys(groupAnalysis)); i >= 1; i--) {
                            const groupsWithAtLeastI = Object.entries(groupAnalysis).filter(([count]) => parseInt(count) >= i).reduce((sum, [, groupCount]) => sum + groupCount, 0);
                            if (groupsWithAtLeastI > 0) report += `${groupsWithAtLeastI} groupe(s) contien(nen)t au moins ${i} numéro(s) de l arrivee.
`;
                        }
                    } else {
                        report += `Aucun des numéros de l arrivee n a été trouvé dans vos groupes de pronostics.
`;
                    }
                }

                // --- Criteria Recall ---
                report += `
--- CRITÈRES UTILISÉS ---
`;
                report += `Configuration: ${numPartantsInput.value} partants, combinaisons de ${tailleCombinaisonInput.value}
`;
                document.querySelectorAll('.filter-box').forEach(box => {
                    const h3 = box.querySelector('h3');
                    if (!h3) return;
                    if (!box.querySelector('.filter-enable')?.checked) {
                        report += `
[DÉSACTIVÉ] ${h3.textContent}
`;
                        return;
                    }
                    report += `
Filtre: ${h3.textContent}
`;
                    if (box.classList.contains('standard-filter') || box.classList.contains('advanced-filter')) {
                        report += `  -Chevaux min: ${box.querySelector('.chevaux-min').value}, Groupes min: ${box.querySelector('.groupes-min').value}
`;
                    } else if (box.classList.contains('weight-filter')) {
                        report += `  - Source: ${box.querySelector('.weight-source').selectedOptions[0].text}
`;
                        report += `  - Poids Min: ${box.querySelector('.weight-min').value}, Poids Max: ${box.querySelector('.weight-max').value}
`;
                    } else if (box.classList.contains('alternance-filter')) {
                        report += `  - Source: ${box.querySelector('.alternance-source').selectedOptions[0].text}
`;
                        report += `  - Alternances Min: ${box.querySelector('.alternance-min').value}, Max: ${box.querySelector('.alternance-max').value}
`;
                    } else if (box.classList.contains('statistic-filter')) {
                        if (box.querySelector('[data-subfilter="evenOdd"]').checked) report += `  - Pairs: entre ${box.querySelector('.even-min').value} et ${box.querySelector('.even-max').value}
`;
                        if (box.querySelector('[data-subfilter="smallLarge"]').checked) report += `  - Petits (≤${box.querySelector('.limit').value}): entre ${box.querySelector('.small-min').value} et ${box.querySelector('.small-max').value}
`;
                        if (box.querySelector('[data-subfilter="consecutive"]').checked) report += `  - Suite: entre ${box.querySelector('.consecutive-min').value} et ${box.querySelector('.consecutive-max').value}
`;
                    }
                });

                backtestResultsOutput.textContent = report;
                backtestResultsContainer.style.display = 'block';
            }

            function saveBacktestResult() {
                saveBacktestToDatabase();
            }
            // --- GESTIONNAIRES D ÉVÉNEMENTS ---
            // --- Tab Switching Logic ---
            const tabButtons = document.querySelectorAll('.tab-btn');
            const tabContents = document.querySelectorAll('.tab-content');

            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabContents.forEach(content => content.style.display = 'none');
                    
                    button.classList.add('active');
                    const activeTab = document.getElementById(button.dataset.tab);
                    if (activeTab) {
                        activeTab.style.display = 'block';
                    }
                });
            });

            runBacktestBtn.addEventListener('click', runBacktest);
            saveBacktestBtn.addEventListener('click', saveBacktestResult);
            
            addFilterButton.addEventListener('click', () => { modal.style.display = 'flex'; });
            closeModalButton.addEventListener('click', () => { modal.style.display = 'none'; });
            modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
            addStandardFilterBtn.addEventListener('click', () => addFilter('standard'));
            addAdvancedFilterBtn.addEventListener('click', () => addFilter('advanced'));
            addWeightFilterBtn.addEventListener('click', () => addFilter('weight'));
            addStatisticFilterBtn.addEventListener('click', () => addFilter('statistic'));
            addAlternanceFilterBtn.addEventListener('click', () => addFilter('alternance'));

            document.querySelectorAll('.toggle-details-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const targetSelector = e.currentTarget.dataset.target;
                    const detailsView = document.querySelector(targetSelector);
                    if (detailsView) {
                        const isHidden = detailsView.style.display === 'none';
                        detailsView.style.display = isHidden ? 'grid' : 'none';
                    }
                });
            });

            // --- INITIALISATION ---
            addFilter('standard'); // Expert 1
            addFilter('statistic'); // Statistiques
            addFilter('weight'); // Poids
            updateEventListeners();
            handleInputChange();

            // Fonction pour afficher les produits d'abonnement (pour les non-abonnés)
            async function showSubscriptionProducts(data) {
                const realCount = data.filtered_count || data.total;
                loader.style.display = 'none';
                resultsSummaryDiv.innerHTML = `<strong>${realCount.toLocaleString('fr-FR')}</strong> combinaisons conservées sur <strong>${data.total.toLocaleString('fr-FR')}</strong>`;
                
                // Mettre à jour le bouton flottant
                const floatingCounter = document.getElementById('floating-counter');
                if (floatingCounter) {
                    floatingCounter.textContent = `${realCount}/${data.total}`;
                }

                // Charger les produits
                try {
                    const response = await fetch('/api/subscriptions/products/');
                    const result = await response.json();
                    
                    if (result.products && result.products.length > 0) {
                        const productsHtml = result.products.map(product => `
                            <div style="background: linear-gradient(135deg, rgba(0, 198, 255, 0.1) 0%, rgba(26, 26, 26, 1) 100%); border: 2px solid var(--primary-color); border-radius: 15px; padding: 25px; margin: 15px 0;">
                                <h3 style="color: var(--primary-color); margin-bottom: 10px; font-size: 1.3rem;">${product.nom}</h3>
                                <div style="font-size: 2rem; font-weight: 800; color: var(--primary-color); margin-bottom: 5px;">${product.prix.toLocaleString('fr-FR')} ${product.devise}</div>
                                <div style="color: #888; font-size: 0.9rem; margin-bottom: 20px;">Durée: ${product.duree_affichage}</div>
                                <div style="display: flex; flex-direction: column; gap: 10px;">
                                    ${product.url_moov_money ? `<a href="${product.url_moov_money}" target="_blank" style="display: block; padding: 12px; background: #FF6600; color: white; text-decoration: none; border-radius: 8px; text-align: center; font-weight: 600;">💳 Payer avec Moov Money</a>` : ''}
                                    ${product.url_airtel_money ? `<a href="${product.url_airtel_money}" target="_blank" style="display: block; padding: 12px; background: #ED1C24; color: white; text-decoration: none; border-radius: 8px; text-align: center; font-weight: 600;">💳 Payer avec Airtel Money</a>` : ''}
                                </div>
                            </div>
                        `).join('');

                        resultsOutputDiv.innerHTML = `
                            <div style="text-align: center; padding: 30px 20px;">
                                <h3 style="color: var(--primary-color); font-size: 1.5rem; margin-bottom: 15px;">🔒 Résultats réservés aux abonnés</h3>
                                <p style="color: #888; margin-bottom: 25px;">Choisissez votre abonnement pour voir les ${realCount} combinaisons :</p>
                                <div style="max-width: 350px; margin: 0 auto;">
                                    ${productsHtml}
                                </div>
                            </div>
                        `;
                    } else {
                        resultsOutputDiv.innerHTML = `
                            <div style="text-align: center; padding: 40px; color: var(--primary-color);">
                                <h3>🔒 Résultats réservés aux abonnés</h3>
                                <p style="margin-top: 15px;">Aucun abonnement disponible.</p>
                                <a href="https://wa.me/241077045354" target="_blank" style="display: inline-block; margin-top: 15px; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white;">
                                    💬 WhatsApp
                                </a>
                            </div>
                        `;
                    }
                } catch (error) {
                    console.error('Error loading products:', error);
                    resultsOutputDiv.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: var(--primary-color);">
                            <h3>🔒 Résultats réservés aux abonnés</h3>
                            <p style="margin-top: 15px;">Contactez-nous pour vous abonner.</p>
                        </div>
                    `;
                }
            }

            // --- CHARGEMENT DES PARTENAIRES ---
            async function loadPartners() {
                try {
                    const response = await fetch('/api/partners/');
                    const result = await response.json();
                    
                    const container = document.getElementById('partners-container');
                    if (!container) return;

                    if (result.partners && result.partners.length > 0) {
                        let html = '';
                        result.partners.forEach(function(partner) {
                            const logo = partner.logo || '';
                            const lien = partner.lien || '#';
                            const nom = partner.nom || '';
                            html += '<div style="text-align: center;">';
                            html += '<a href="' + lien + '" target="_blank" style="text-decoration: none;">';
                            if (logo) {
                                html += '<img src="' + logo + '" alt="' + nom + '" style="max-height: 100px; width: auto; transition: transform 0.3s ease; border-radius: 8px;" onmouseover="this.style.transform=\'scale(1.1)\'" onmouseout="this.style.transform=\'scale(1)\'">';
                            }
                            if (nom) {
                            html += '<p style="margin-top: 10px; color: var(--primary-color); font-weight: 600;">' + nom + '</p>';
                        }
                            html += '</a></div>';
                        });
                        container.innerHTML = html;
                    } else {
                        container.innerHTML = '<p style="color: #666;">Aucun partenaire pour le moment.</p>';
                    }
                } catch (error) {
                    console.error('Error loading partners:', error);
                    const container = document.getElementById('partners-container');
                    if (container) {
                        container.innerHTML = '<p style="color: #666;">Impossible de charger les partenaires.</p>';
                    }
                }
            }

            // --- BACKTEST SAVE & LOAD ---
            async function saveBacktestToDatabase() {
                const textToSave = backtestResultsOutput.textContent;
                if (!textToSave) {
                    alert("Aucun resultat a sauvegarder");
                    return;
                }
                const nom = prompt("Nommez cette analyse (optionnel) :");
                if (nom === null) return;
                try {
                    const arrivee = backtestInput.value.match(/\d+/g).map(Number).sort((a, b) => a - b);
                    const arriveeSet = new Set(arrivee);
                    const combinaisons_trouvees = currentFilteredCombinations.filter(c => {
                        const s = new Set(c);
                        for (const n of arriveeSet) { if (!s.has(n)) return false; }
                        return true;
                    });
                    const data = {
                        num_partants: parseInt(numPartantsInput.value),
                        taille_combinaison: parseInt(tailleCombinaisonInput.value),
                        pronostics: currentRawGroups,
                        criteres_filtres: collectFilterCriteria(),
                        arrivee: arrivee,
                        combinaisons_filtrees: currentFilteredCombinations,
                        combinaisons_trouvees: combinaisons_trouvees,
                        nombre_trouvees: combinaisons_trouvees.length,
                        rapport: textToSave,
                        nom: nom || ""
                    };
                    const response = await fetch("/api/backtest/save/", {
                        method: "POST",
                        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert("Analyse sauvegardee !");
                        loadSavedAnalyses();
                    } else {
                        alert("Erreur: " + (result.error || "Erreur"));
                    }
                } catch (e) {
                    console.error(e);
                    alert("Erreur connexion");
                }
            }
            function collectFilterCriteria() {
                const criteria = { filters: [] };
                document.querySelectorAll(".filter-box").forEach(box => {
                    const h3 = box.querySelector("h3");
                    if (!h3) return;
                    const f = { title: h3.textContent, enabled: box.querySelector(".filter-enable")?.checked || false, type: null, params: {} };
                    if (box.classList.contains("standard-filter") || box.classList.contains("advanced-filter")) {
                        f.type = "expert";
                        f.params = { chevaux_min: box.querySelector(".chevaux-min")?.value, groupes_min: box.querySelector(".groupes-min")?.value };
                    } else if (box.classList.contains("weight-filter")) {
                        f.type = "weight";
                        f.params = { source: box.querySelector(".weight-source")?.value, poids_min: box.querySelector(".weight-min")?.value, poids_max: box.querySelector(".weight-max")?.value };
                    } else if (box.classList.contains("alternance-filter")) {
                        f.type = "alternance";
                        f.params = { source: box.querySelector(".alternance-source")?.value, alternances_min: box.querySelector(".alternance-min")?.value, alternances_max: box.querySelector(".alternance-max")?.value };
                    } else if (box.classList.contains("statistic-filter")) {
                        f.type = "statistic";
                        f.params = {
                            evenOdd: box.querySelector('[data-subfilter="evenOdd"]')?.checked,
                            even_min: box.querySelector(".even-min")?.value,
                            even_max: box.querySelector(".even-max")?.value,
                            smallLarge: box.querySelector('[data-subfilter="smallLarge"]')?.checked,
                            small_min: box.querySelector(".small-min")?.value,
                            small_max: box.querySelector(".small-max")?.value,
                            consecutive: box.querySelector('[data-subfilter="consecutive"]')?.checked,
                            consecutive_min: box.querySelector(".consecutive-min")?.value,
                            consecutive_max: box.querySelector(".consecutive-max")?.value
                        };
                    }
                    criteria.filters.push(f);
                });
                return criteria;
            }
            async function loadSavedAnalyses() {
                try {
                    const response = await fetch("/api/backtest/list/");
                    const result = await response.json();
                    if (result.success) displaySavedAnalyses(result.analyses);
                } catch (e) { console.error(e); }
            }
            function displaySavedAnalyses(analyses) {
                const container = document.getElementById("saved-analyses-container");
                if (!container) return;
                if (analyses.length === 0) {
                    container.innerHTML = "<p>Aucune analyse.</p>";
                    return;
                }
                container.innerHTML = analyses.map(a => "<div class=\"saved-analysis-item\" data-id=\"" + a.id + "\"><div class=\"analysis-header\"><span class=\"analysis-name\">" + escapeHtml(a.nom) + "</span><span class=\"analysis-date\">" + new Date(a.date_creation).toLocaleString("fr-FR") + "</span></div><div class=\"analysis-details\">Arrivee: [" + a.arrivee + "] | Trouve: " + a.nombre_trouvees + "</div><div class=\"analysis-actions\"><button class=\"load-analysis-btn\" data-id=\"" + a.id + "\">Charger</button><button class=\"view-report-btn\" data-id=\"" + a.id + "\">Voir</button><button class=\"delete-analysis-btn\" data-id=\"" + a.id + "\">Supprimer</button></div></div>").join("");
                container.querySelectorAll(".load-analysis-btn").forEach(btn => btn.addEventListener("click", () => loadAndRestoreAnalysis(parseInt(btn.dataset.id))));
                container.querySelectorAll(".view-report-btn").forEach(btn => btn.addEventListener("click", () => viewAnalysisReport(parseInt(btn.dataset.id))));
                container.querySelectorAll(".delete-analysis-btn").forEach(btn => btn.addEventListener("click", () => deleteAnalysis(parseInt(btn.dataset.id))));
            }
            async function loadAndRestoreAnalysis(id) {
                try {
                    const response = await fetch("/api/backtest/load/" + id + "/");
                    const result = await response.json();
                    if (result.success) {
                        const a = result.analysis;
                        numPartantsInput.value = a.num_partants;
                        tailleCombinaisonInput.value = a.taille_combinaison;
                        pronosticsTextarea.value = formatPronosticsFromData(a.pronostics);
                        parsePronostics();
                        restoreFilters(a.criteres_filtres);
                        currentFilteredCombinations = a.combinaisons_filtrees;
                        backtestInput.value = a.arrivee.join(", ");
                        document.querySelector('[data-tab="results-tab-content"]').click();
                        alert("Analyse chargee !");
                    } else { alert("Erreur: " + (result.error || "Erreur")); }
                } catch (e) { console.error(e); alert("Erreur connexion"); }
            }
            function formatPronosticsFromData(pronostics) {
                if (!pronostics || pronostics.length === 0) return "";
                return pronostics.map(g => g.name + " : " + g.horses.join(", ")).join("\n");
            }
            function restoreFilters(criteria) {
                document.querySelectorAll(".filter-box").forEach(b => b.remove());
                if (!criteria || !criteria.filters) return;
                updateSynthesis();
            }
            async function viewAnalysisReport(id) {
                try {
                    const response = await fetch("/api/backtest/load/" + id + "/");
                    const result = await response.json();
                    if (result.success) {
                        document.querySelector('[data-tab="backtest-tab-content"]').click();
                        backtestResultsOutput.textContent = result.analysis.rapport;
                        backtestResultsContainer.style.display = "block";
                        backtestInput.value = result.analysis.arrivee.join(", ");
                    } else { alert("Erreur: " + (result.error || "Erreur")); }
                } catch (e) { console.error(e); alert("Erreur connexion"); }
            }
            async function deleteAnalysis(id) {
                if (!confirm("Supprimer cette analyse ?")) return;
                try {
                    const response = await fetch("/api/backtest/delete/" + id + "/", { method: "DELETE", headers: { "X-CSRFToken": getCsrfToken() } });
                    const result = await response.json();
                    if (result.success) {
                        alert("Analyse supprimee !");
                        loadSavedAnalyses();
                    } else { alert("Erreur: " + (result.error || "Erreur")); }
                } catch (e) { console.error(e); alert("Erreur connexion"); }
            }
            function getCsrfToken() {
                const cookies = document.cookie.split(";");
                for (const c of cookies) {
                    const [name, value] = c.trim().split("=");
                    if (name === "csrftoken") return decodeURIComponent(value);
                }
                return "";
            }
            function escapeHtml(t) { const d = document.createElement("div"); d.textContent = t; return d.innerHTML; }
            // Charger les partenaires au chargement de la page
            loadPartners();
            loadSavedAnalyses();
            });
