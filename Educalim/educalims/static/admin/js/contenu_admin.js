(function($) {
    'use strict';

    // Attendre que jQuery soit disponible
    function waitForJQuery(callback) {
        if (window.jQuery) {
            callback(window.jQuery);
        } else if (window.django && window.django.jQuery) {
            callback(window.django.jQuery);
        } else {
            setTimeout(function() {
                waitForJQuery(callback);
            }, 100);
        }
    }

    waitForJQuery(function($) {
        $(document).ready(function() {
        var disciplineField = $('#id_discipline');
        var niveauField = $('#id_niveau');
        var leconsField = $('#id_lecons');
        var chapitresField = $('#id_chapitres');

        // Fonction pour charger les niveaux selon la discipline
        function loadNiveaux(disciplineId) {
            if (!disciplineId) {
                niveauField.html('<option value="">---------</option>');
                return;
            }

            $.ajax({
                url: '/get-niveaux-by-discipline/',
                data: {'discipline_id': disciplineId},
                dataType: 'json',
                success: function(data) {
                    niveauField.empty();
                    niveauField.append('<option value="">---------</option>');

                    if (data.niveaux && data.niveaux.length > 0) {
                        // Grouper par cycle
                        var cycles = {};
                        data.niveaux.forEach(function(niveau) {
                            if (!cycles[niveau.cycle]) {
                                cycles[niveau.cycle] = [];
                            }
                            cycles[niveau.cycle].push(niveau);
                        });

                        Object.keys(cycles).sort().forEach(function(cycleName) {
                            var optgroup = $('<optgroup label="' + cycleName + '"></optgroup>');
                            cycles[cycleName].forEach(function(niveau) {
                                optgroup.append('<option value="' + niveau.id + '">' + niveau.nom + '</option>');
                            });
                            niveauField.append(optgroup);
                        });
                    }
                },
                error: function() {
                    niveauField.html('<option value="">Erreur de chargement</option>');
                }
            });
        }

        // Fonction pour charger les unités d'apprentissage selon le niveau
        function loadUnitesApprentissage(niveauId) {
            if (!niveauId) {
                // Vider les conteneurs de cases à cocher
                clearCheckboxes('lecons');
                clearCheckboxes('chapitres');
                return;
            }

            $.ajax({
                url: '/get-unites-apprentissage-by-niveau/',
                data: {'niveau_id': niveauId},
                dataType: 'json',
                success: function(data) {
                    // Vider les deux conteneurs
                    clearCheckboxes('lecons');
                    clearCheckboxes('chapitres');

                    if (data.unites && data.unites.length > 0) {
                        if (data.cycle === 'collège') {
                            // Pour le collège: charger les leçons
                            populateCheckboxes('lecons', data.unites);

                            // Désactiver le champ chapitre pour le collège
                            disableCheckboxSection('chapitres');
                            enableCheckboxSection('lecons');

                        } else if (data.cycle === 'lycée') {
                            // Pour le lycée: charger les chapitres
                            populateCheckboxes('chapitres', data.unites);

                            // Désactiver le champ leçon pour le lycée
                            disableCheckboxSection('lecons');
                            enableCheckboxSection('chapitres');
                        }
                    } else {
                        enableCheckboxSection('lecons');
                        enableCheckboxSection('chapitres');
                    }
                },
                error: function() {
                    clearCheckboxes('lecons');
                    clearCheckboxes('chapitres');
                    enableCheckboxSection('lecons');
                    enableCheckboxSection('chapitres');
                }
            });
        }

        // Fonction pour vider un conteneur de cases à cocher
        function clearCheckboxes(fieldName) {
            var $widgetContainer = $('#id_' + fieldName);
            if ($widgetContainer.length) {
                var $checkboxContainer = $widgetContainer.find('.checkbox-container');
                if ($checkboxContainer.length) {
                    $checkboxContainer.empty();
                }
            }
        }

        // Fonction pour peupler les cases à cocher
        function populateCheckboxes(fieldName, unites) {
            var $widgetContainer = $('#id_' + fieldName);
            if (!$widgetContainer.length) {
                console.error('Conteneur de cases à cocher non trouvé pour:', fieldName);
                return;
            }

            var $checkboxContainer = $widgetContainer.find('.checkbox-container');
            if ($checkboxContainer.length === 0) {
                // Créer le conteneur s'il n'existe pas
                $checkboxContainer = $('<div class="checkbox-container"></div>');
                $widgetContainer.append($checkboxContainer);
            }

            var checkboxesHtml = '';
            unites.forEach(function(unite) {
                var displayText = unite.titre;
                if (unite.numero) {
                    displayText = unite.numero + '. ' + displayText;
                }
                if (unite.parent_info) {
                    displayText += ' (' + unite.parent_info + ')';
                }

                checkboxesHtml += '<div class="checkbox-item">' +
                    '<label class="checkbox-label">' +
                    '<input type="checkbox" name="' + fieldName + '" value="' + unite.id + '" class="custom-checkbox-input" data-value="' + unite.id + '" data-label="' + displayText + '">' +
                    '<span class="checkbox-text">' + displayText + '</span>' +
                    '</label>' +
                    '</div>';
            });

            $checkboxContainer.html(checkboxesHtml);

            // Mettre à jour le champ hidden pour Django
            updateHiddenField(fieldName);

            // Ajouter les écouteurs d'événements pour les nouvelles cases à cocher
            addCheckboxListeners(fieldName);
        }

        // Fonction pour désactiver une section de cases à cocher
        function disableCheckboxSection(fieldName) {
            var $widgetContainer = $('#id_' + fieldName);
            if ($widgetContainer.length) {
                $widgetContainer.addClass('disabled');
                $widgetContainer.find('input[type="checkbox"]').prop('disabled', true);
            }
        }

        // Fonction pour activer une section de cases à cocher
        function enableCheckboxSection(fieldName) {
            var $widgetContainer = $('#id_' + fieldName);
            if ($widgetContainer.length) {
                $widgetContainer.removeClass('disabled');
                $widgetContainer.find('input[type="checkbox"]').prop('disabled', false);
            }
        }

        // Fonction pour mettre à jour le champ hidden pour Django
        function updateHiddenField(fieldName) {
            var $widgetContainer = $('#id_' + fieldName);
            if ($widgetContainer.length) {
                var checkedValues = [];
                $widgetContainer.find('input[type="checkbox"]:checked').each(function() {
                    checkedValues.push($(this).val());
                });

                // Supprimer les anciens champs cachés
                $widgetContainer.find('input[type="hidden"][name="' + fieldName + '"]').remove();

                // Ajouter les nouveaux champs cachés pour chaque valeur sélectionnée
                checkedValues.forEach(function(value) {
                    var $hiddenField = $('<input type="hidden" name="' + fieldName + '" value="' + value + '">');
                    $widgetContainer.append($hiddenField);
                });

                // Mettre à jour le champ de synchronisation
                var $syncField = $('#id_' + fieldName + '_hidden');
                if ($syncField.length) {
                    $syncField.val(checkedValues.join(','));
                }
                
                // Debug: afficher les valeurs dans la console
                console.log('Champ ' + fieldName + ' mis à jour avec:', checkedValues);
            }
        }

        // Ajouter des écouteurs d'événements pour les changements de cases à cocher
        function addCheckboxListeners(fieldName) {
            var $widgetContainer = $('#id_' + fieldName);
            if ($widgetContainer.length) {
                $widgetContainer.find('input[type="checkbox"]').on('change', function() {
                    updateHiddenField(fieldName);
                });
            }
        }

        // Écouteurs d'événements
        disciplineField.on('change', function() {
            var disciplineId = $(this).val();
            loadNiveaux(disciplineId);

            // Vider les champs dépendants (cases à cocher)
            clearCheckboxes('lecons');
            clearCheckboxes('chapitres');
            loadUnitesApprentissage('');
        });

        niveauField.on('change', function() {
            var niveauId = $(this).val();
            loadUnitesApprentissage(niveauId);

            // Vider les champs d'unités (cases à cocher)
            clearCheckboxes('lecons');
            clearCheckboxes('chapitres');
        });

        // Initialiser au chargement de la page
        if (disciplineField.val()) {
            loadNiveaux(disciplineField.val());
        }

        if (niveauField.val()) {
            loadUnitesApprentissage(niveauField.val());
        }
          });
    });
})(jQuery);