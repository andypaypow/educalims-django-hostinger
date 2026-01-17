import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educalims_project.settings')
django.setup()

from educalims.models import Discipline, Niveau, Cycle, Unite

def parse_instances_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {
        'discipline': None,
        'niveau_parent': None,
        'series': {}
    }

    current_serie = None
    current_partie = None
    current_chapitres = []

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if 'Discipline' in line and 'NIVEAU' in line:
            parts = line.split()
            discipline_idx = parts.index('Discipline') + 1
            niveau_idx = parts.index('NIVEAU') + 1
            data['discipline'] = parts[discipline_idx]
            data['niveau_parent'] = parts[niveau_idx]

        elif line.startswith('Terminale') and ('C' in line or 'D' in line):
            if current_serie and current_partie and current_chapitres:
                if current_partie not in data['series'][current_serie]:
                    data['series'][current_serie][current_partie] = []
                data['series'][current_serie][current_partie].extend(current_chapitres)
                current_chapitres = []

            current_serie = line
            if current_serie not in data['series']:
                data['series'][current_serie] = {}
            current_partie = None

        elif line.startswith('PARTIE'):
            if current_partie and current_chapitres:
                if current_partie not in data['series'][current_serie]:
                    data['series'][current_serie][current_partie] = []
                data['series'][current_serie][current_partie].extend(current_chapitres)
                current_chapitres = []

            current_partie = line

        elif line.startswith('Chapitre'):
            chapitre_titre = line.replace('Chapitre', '').strip()
            parts = chapitre_titre.split('.', 1)
            if len(parts) > 1:
                chapitre_titre = parts[1].strip()
            current_chapitres.append(chapitre_titre)

    if current_serie and current_partie and current_chapitres:
        if current_partie not in data['series'][current_serie]:
            data['series'][current_serie][current_partie] = []
        data['series'][current_serie][current_partie].extend(current_chapitres)

    return data

def insert_instances_data(file_path):
    print(f"Lecture du fichier {file_path}...")
    data = parse_instances_md(file_path)

    print(f"\nDiscipline: {data['discipline']}")
    print(f"Niveau parent: {data['niveau_parent']}")

    discipline, _ = Discipline.objects.get_or_create(
        nom=data['discipline'],
        defaults={'description': f"Discipline de {data['discipline']}"}
    )
    print(f"\nDiscipline '{discipline.nom}': créée/existante")

    cycle, _ = Cycle.objects.get_or_create(
        nom='Lycée',
        defaults={'description': 'Cycle du Lycée'}
    )

    niveau_parent, _ = Niveau.objects.get_or_create(
        nom=data['niveau_parent'],
        defaults={'ordre': 4, 'cycle': cycle}
    )

    total_parties = 0
    total_chapitres = 0

    for serie_nom, parties in data['series'].items():
        print(f"\n--- Série: {serie_nom} ---")

        niveau_enfant, created = Niveau.objects.get_or_create(
            nom=serie_nom,
            defaults={'ordre': 1, 'cycle': cycle}
        )

        if created or not niveau_enfant.niveau_parent:
            niveau_enfant.niveau_parent = niveau_parent
            niveau_enfant.save()

        for partie_idx, (partie_nom, chapitres) in enumerate(parties.items(), 1):
            partie = Unite.objects.filter(
                nom=partie_nom,
                niveau=niveau_enfant,
                type_unite='P'
            ).first()

            if not partie:
                partie = Unite.objects.create(
                    nom=partie_nom,
                    discipline=discipline,
                    niveau=niveau_enfant,
                    type_unite='P',
                    ordre=partie_idx
                )
                total_parties += 1

            for chapitre_idx, chapitre_nom in enumerate(chapitres, 1):
                chapitre = Unite.objects.filter(
                    nom=chapitre_nom,
                    niveau=niveau_enfant,
                    unite_parent=partie
                ).first()

                if not chapitre:
                    chapitre = Unite.objects.create(
                        nom=chapitre_nom,
                        discipline=discipline,
                        niveau=niveau_enfant,
                        type_unite='C',
                        unite_parent=partie,
                        ordre=chapitre_idx
                    )
                    total_chapitres += 1

    print(f"\nRÉSUMÉ:")
    print(f"Discipline: {Discipline.objects.count()}")
    print(f"Niveaux: {Niveau.objects.count()}")
    print(f"Unités totales: {Unite.objects.count()}")
    print(f"Parties créées: {total_parties}")
    print(f"Chapitres créés: {total_chapitres}")

if __name__ == '__main__':
    file_path = os.path.join(os.path.dirname(__file__), 'instances.md')
    insert_instances_data(file_path)
    print("\nImport terminé avec succès!")
