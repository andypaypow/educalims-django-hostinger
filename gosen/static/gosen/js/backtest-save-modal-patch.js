// Patch modal sauvegarde backtest avec nom, date et arrivee editables
(function() {
    document.addEventListener("DOMContentLoaded", function() {
        setTimeout(function() {
            if (typeof saveBacktestResult !== "undefined") {
                saveBacktestResult = function() { showSaveBacktestModal(); };
                console.log("[BACKTEST-SAVE-MODAL] Fonction remplacee");
            }
        }, 2000);

        function showSaveBacktestModal() {
            const arriveeInput = document.getElementById("backtest-input");
            const currentArrival = arriveeInput ? arriveeInput.value.trim() : "";
            const today = new Date().toISOString().split("T")[0];

            const modal = document.createElement("div");
            modal.id = "save-backtest-modal";
            modal.style.cssText = "display: flex; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 99999; justify-content: center; align-items: center;";

            modal.innerHTML = `
                <div style="background: white; padding: 30px; border-radius: 12px; max-width: 500px; width: 90%; max-height: 80vh; overflow-y: auto;">
                    <h3 style="color: #009E60; margin-bottom: 20px;">Sauvegarder l'analyse</h3>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: bold; margin-bottom: 8px;">Nom de la sauvegarde *</label>
                        <input type="text" id="save-backtest-name" placeholder="Ex: Course R1 - 06/03/2026" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px;">
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: bold; margin-bottom: 8px;">Date de la course</label>
                        <input type="date" id="save-backtest-date" value="${today}" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px;">
                        <small style="color: #666;">Date à laquelle la course a eu lieu</small>
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: bold; margin-bottom: 8px;">Arrivée testée</label>
                        <input type="text" id="save-backtest-arrival" placeholder="Ex: 1-2-3-4-5-6-7-8" value="${currentArrival}" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px;">
                        <small style="color: #666;">L'arrivée que vous avez testée (corrigible)</small>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 25px;">
                        <button id="cancel-save-backtest" style="flex: 1; padding: 12px; background: #666; color: white; border: none; border-radius: 6px; cursor: pointer;">Annuler</button>
                        <button id="confirm-save-backtest" style="flex: 1; padding: 12px; background: #009E60; color: white; border: none; border-radius: 6px; cursor: pointer;">Sauvegarder</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            const nameInput = document.getElementById("save-backtest-name");
            const dateInput = document.getElementById("save-backtest-date");
            const arrivalInput = document.getElementById("save-backtest-arrival");

            setTimeout(() => nameInput.focus(), 100);

            document.getElementById("cancel-save-backtest").onclick = function() { modal.remove(); };
            modal.onclick = function(e) { if (e.target === modal) modal.remove(); };

            document.getElementById("confirm-save-backtest").onclick = function() {
                const nom = nameInput.value.trim();
                const date = dateInput.value;
                const arrivee = arrivalInput.value.trim();

                if (!nom) { alert("Veuillez entrer un nom"); nameInput.focus(); return; }
                if (!arrivee) { alert("Veuillez entrer une arrivee"); arrivalInput.focus(); return; }

                const backtestInput = document.getElementById("backtest-input");
                if (backtestInput) backtestInput.value = arrivee;

                saveBacktestWithParams(nom, date, arrivee);
                modal.remove();
            };
        }

        async function saveBacktestWithParams(nomModal, dateModal, arriveeModal) {
            const textToSave = document.getElementById("backtest-results-output").textContent;
            if (!textToSave) { alert("Aucun resultat a sauvegarder"); return; }

            try {
                const arrivee = arriveeModal.match(/\d+/g);
                if (!arrivee) { alert("Arrivee invalide"); return; }
                const arriveeNum = arrivee.map(Number).sort((a, b) => a - b);

                const combos = window.currentFilteredCombinations || [];
                const arriveeSet = new Set(arriveeNum);
                const trouvees = combos.filter(c => {
                    const s = new Set(c);
                    for (const n of arriveeSet) { if (!s.has(n)) return false; }
                    return true;
                });

                const parsedDiv = document.getElementById("parsed-groups");
                const rawGroups = window.currentRawGroups || [];
                const pronostics = Array.from(parsedDiv.children).map((g, i) => ({
                    name: rawGroups[i] ? rawGroups[i].name : "Groupe " + (i + 1),
                    horses: rawGroups[i] ? rawGroups[i].horses : [],
                    min: parseInt(g.querySelector(".group-min").value),
                    max: parseInt(g.querySelector(".group-max").value)
                }));

                const data = {
                    num_partants: parseInt(document.getElementById("num-partants").value),
                    taille_combinaison: parseInt(document.getElementById("taille-combinaison").value),
                    pronostics: pronostics,
                    criteres_filtres: window.collectFilterCriteria ? window.collectFilterCriteria() : {},
                    arrivee: arriveeNum,
                    combinaisons_filtrees: combos,
                    combinaisons_trouvees: trouvees,
                    nombre_trouvees: trouvees.length,
                    rapport: textToSave,
                    nom: nomModal,
                    date_course: dateModal
                };

                const resp = await fetch("/api/backtest/save/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
                    body: JSON.stringify(data)
                });

                const res = await resp.json();
                if (res.success) {
                    alert("Analyse sauvegardee !");
                    if (typeof loadSavedAnalyses === "function") loadSavedAnalyses();
                } else {
                    alert("Erreur: " + (res.error || "Erreur"));
                }
            } catch (e) {
                console.error(e);
                alert("Erreur connexion");
            }
        }

        function getCsrfToken() {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const parts = cookies[i].trim().split("=");
                if (parts[0] === "csrftoken") return decodeURIComponent(parts[1]);
            }
            return "";
        }

        console.log("[BACKTEST-SAVE-MODAL] Module charge");
    });
})();
