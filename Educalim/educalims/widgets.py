from django import forms
from django.utils.safestring import mark_safe


class CheckboxSelectMultipleCustom(forms.Widget):
    """
    Widget personnalisé pour afficher des cases à cocher avec mise en forme
    """

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.allow_multiple_selected = True

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}

        # S'assurer d'avoir un ID
        widget_id = attrs.get('id', f'id_{name}')

        # Préparer les valeurs - éviter toute récursion
        final_value = []
        if value is not None:
            if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                final_value = list(value)
            elif isinstance(value, str):
                if value:
                    final_value = [v.strip() for v in value.split(',') if v.strip()]
            else:
                final_value = [value]

        # Commencer le HTML
        html = f'<div id="{widget_id}" class="checkbox-widget-container" data-field-name="{name}">'
        html += '<div class="loading-placeholder">Chargement des options...</div>'
        html += '</div>'

        # Générer les champs cachés pour chaque valeur pré-sélectionnée
        for val in final_value:
            html += f'<input type="hidden" name="{name}" value="{val}">'

        # Ajouter le champ de synchronisation pour JavaScript
        sync_value = ','.join(str(v) for v in final_value if v is not None)
        html += f'<input type="hidden" name="{name}_sync" id="{widget_id}_hidden" value="{sync_value}">'

        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        # Récupérer toutes les valeurs pour ce champ de manière sécurisée
        result = []

        # Essayer d'abord getlist (pour QueryDict)
        if hasattr(data, 'getlist'):
            try:
                values = data.getlist(name)
                # Filtrer les valeurs vides et le champ de synchronisation
                result = [v for v in values if v and v != '_sync' and v != '']
            except:
                pass
        else:
            # Fallback pour dict normal
            try:
                raw_value = data.get(name, [])
                if isinstance(raw_value, str):
                    if raw_value:
                        result = [raw_value]
                elif hasattr(raw_value, '__iter__') and not isinstance(raw_value, str):
                    result = [v for v in raw_value if v and v != '_sync' and v != '']
            except:
                pass

        # Si aucune valeur trouvée avec getlist, essayer de récupérer depuis les champs cachés individuels
        if not result and hasattr(data, 'getlist'):
            # Parcourir toutes les clés pour trouver celles qui correspondent à notre champ
            for key in data.keys():
                if key == name and key not in [name + '_sync']:
                    # C'est un champ caché individuel pour notre champ
                    value = data.get(key)
                    if value and value != '':
                        result.append(value)

        # Convertir en entiers si possible
        final_result = []
        for value in result:
            try:
                final_result.append(int(value))
            except (ValueError, TypeError):
                if value:  # Garder les valeurs non-numériques
                    final_result.append(value)

        return final_result

    def format_value(self, value):
        # Formater la valeur pour l'affichage - éviter toute récursion
        if value is None:
            return []
        elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
            return list(value)
        elif isinstance(value, str):
            if value:
                return [v.strip() for v in value.split(',') if v.strip()]
            return []
        else:
            return [value]