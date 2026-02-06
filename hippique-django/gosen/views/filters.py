from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from itertools import combinations


def combination_generator(arr, k):
    """Générateur de combinaisons"""
    return combinations(arr, k)


def get_longest_consecutive(arr):
    """Retourne la plus longue suite consécutive"""
    if len(arr) < 2:
        return len(arr)
    sorted_arr = sorted(arr)
    max_len = 1
    current_len = 1
    for i in range(1, len(sorted_arr)):
        if sorted_arr[i] == sorted_arr[i-1] + 1:
            current_len += 1
        else:
            max_len = max(max_len, current_len)
            current_len = 1
    return max(max_len, current_len)


def calculate_alternances(combination, source_array):
    """Calcule le nombre d'alternances"""
    if len(source_array) == 0:
        return 0
    combination_set = set(str(h) for h in combination)
    alternances = 0
    for i in range(len(source_array) - 1):
        current_in = source_array[i] in combination_set
        next_in = source_array[i+1] in combination_set
        if current_in != next_in:
            alternances += 1
    return alternances


@require_http_methods(["POST"])
@csrf_exempt
def api_filter_combinations(request):
    """
    API principale de filtrage - TOUT les calculs se font côté serveur
    Accessible à tous les utilisateurs (formules protégées sur le serveur)
    """

    try:
        data = json.loads(request.body)

        # Paramètres de base
        n = int(data.get('n', 16))
        k = int(data.get('k', 6))
        
        if k > n:
            return JsonResponse({
                'success': False,
                'error': 'La taille de combinaison ne peut pas être supérieure au nombre de partants'
            })
        
        # Groupes de pronostics
        groups = data.get('groups', [])
        
        # Filtres
        or_filters = data.get('orFilters', [])
        and_filters = data.get('andFilters', [])
        weight_filters = data.get('weightFilters', [])
        even_odd_filters = data.get('evenOddFilters', [])
        small_large_filters = data.get('smallLargeFilters', [])
        consecutive_filters = data.get('consecutiveFilters', [])
        alternance_filters = data.get('alternanceFilters', [])
        
        # Génération des combinaisons
        partants = list(range(1, n + 1))
        filtered_combinations = []
        
        for combi in combination_generator(partants, k):
            is_kept = True
            
            # Filtre Group Min/Max
            if is_kept and groups:
                for group_filter in groups:
                    horses_in_group = sum(1 for h in combi if h in group_filter['horses'])
                    if horses_in_group < group_filter['min'] or horses_in_group > group_filter['max']:
                        is_kept = False
                        break
            
            # Filtre Pairs/Impairs
            if is_kept and even_odd_filters:
                even_count = sum(1 for num in combi if num % 2 == 0)
                for f in even_odd_filters:
                    if even_count < f['min'] or even_count > f['max']:
                        is_kept = False
                        break
            
            # Filtre Petits/Grands
            if is_kept and small_large_filters:
                for f in small_large_filters:
                    small_count = sum(1 for num in combi if num <= f['limit'])
                    if small_count < f['min'] or small_count > f['max']:
                        is_kept = False
                        break
            
            # Filtre Suite consécutive
            if is_kept and consecutive_filters:
                longest = get_longest_consecutive(combi)
                for f in consecutive_filters:
                    if longest < f['min'] or longest > f['max']:
                        is_kept = False
                        break
            
            # Filtre Poids
            if is_kept and weight_filters:
                for f in weight_filters:
                    total_weight = sum(f['map'].get(str(horse), 0) for horse in combi)
                    if total_weight < f['min'] or total_weight > f['max']:
                        is_kept = False
                        break
            
            # Filtre Alternance
            if is_kept and alternance_filters:
                for f in alternance_filters:
                    if f['source']:
                        alternance_count = calculate_alternances(combi, f['source'])
                        if alternance_count < f['min'] or alternance_count > f['max']:
                            is_kept = False
                            break
            
            # Filtres Expert 1 (OR)
            if is_kept and or_filters and groups:
                for f in or_filters:
                    groups_with_min = sum(1 for g in groups 
                                        if sum(1 for c in combi if c in g['horses']) >= f['chevauxMin'])
                    if groups_with_min < f['groupesMin']:
                        is_kept = False
                        break
            
            # Filtres Expert 2 (AND)
            if is_kept and and_filters and groups:
                for f in and_filters:
                    horses_group_counts = {}
                    for h in combi:
                        horses_group_counts[h] = sum(1 for g in groups if h in g['horses'])
                    horses_with_min = sum(1 for h in horses_group_counts 
                                         if horses_group_counts[h] >= f['groupesMin'])
                    if horses_with_min < f['chevauxMin']:
                        is_kept = False
                        break
            
            if is_kept:
                filtered_combinations.append(list(combi))
        
        # Calcul du total de combinaisons possibles
        from math import comb
        total_combinations = comb(n, k)
        
        # IMPORTANT: Conserver le vrai nombre de combinaisons filtrées AVANT de vider
        filtered_count = len(filtered_combinations)

        # Vérification de l'abonnement
        from django.contrib.auth.models import AnonymousUser
        from gosen.models import UserProfile

        user = request.user
        is_subscribed = False
        combinations_to_return = filtered_combinations

        # 1. Vérifier si l'utilisateur est connecté et abonné
        if not isinstance(user, AnonymousUser) and hasattr(user, 'profile'):
            is_subscribed = user.profile.est_abonne

        # 2. Si pas connecté, vérifier par numéro de téléphone en paramètre POST
        if not is_subscribed and data.get('phone'):
            phone = data.get('phone', '').replace('+', '').replace(' ', '')
            profile = UserProfile.objects.filter(telephone__icontains=phone).first()
            if profile and profile.est_abonne:
                is_subscribed = True
                # Connecter automatiquement l'utilisateur pour les prochaines requêtes
                from django.contrib.auth import login
                login(request, profile.user)

        # 3. Si toujours pas abonné, vérifier le cookie user_phone
        if not is_subscribed:
            cookie_phone = request.COOKIES.get('user_phone')
            if cookie_phone:
                phone_normalized = cookie_phone.replace('+', '').replace(' ', '')
                profile = UserProfile.objects.filter(telephone__icontains=phone_normalized).first()
                if profile and profile.est_abonne:
                    is_subscribed = True
                    # Connecter automatiquement l'utilisateur
                    from django.contrib.auth import login
                    login(request, profile.user)

        # Pour les non-abonnés, on renvoie un tableau vide mais on garde filtered_count
        if not is_subscribed:
            combinations_to_return = []

        return JsonResponse({
            'success': True,
            'filtered': combinations_to_return,
            'total': total_combinations,
            'filtered_count': filtered_count,
            'count': len(combinations_to_return),
            'is_subscribed': is_subscribed
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du filtrage: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def api_check_filter_access(request):
    """Vérifie si l'utilisateur a accès au filtrage (toujours vrai)"""
    return JsonResponse({
        'can_filter': True,
        'is_admin': False
    })
