import json
import numpy as np

FICHIER = 'data/data.json'

with open(FICHIER, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Liste des clés numériques à bruiter dans chaque canal
cles_numeriques = [
    'impressions', 'visites', 'ctr', 'taux_rebond', 'duree_moyenne', 'position_moyenne', 'appels', 'formulaires', 'contacts', 'cout_contact',
    'budget', 'clics', 'taux_conversion', 'quality_score', 'relevance_score', 'interaction', 'taux_interaction',
    'vues', 'clics_site', 'demande_itineraire', 'reservations', 'score_avis', 'nombre_avis', 'taux_appel', 'taux_reservation',
    'vues_meta_mobile', 'vues_meta_desktop', 'vues_google_mobile', 'vues_google_desktop'
]

for client in data['clients']:
    for hist in client['historique']:
        for canal in ['site', 'google_ads', 'meta_ads', 'gmb']:
            if canal in hist:
                for k in hist[canal]:
                    if k in cles_numeriques and isinstance(hist[canal][k], (int, float)):
                        bruit = np.random.normal(1, 0.15)
                        val = hist[canal][k]
                        # Pour les taux, on reste entre 0 et 1
                        if 'taux' in k or 'ctr' in k or 'score' in k:
                            hist[canal][k] = float(np.clip(val * bruit, 0, 1))
                        else:
                            hist[canal][k] = max(0, float(val) * bruit)

with open(FICHIER, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Bruit ajouté au JSON avec succès !') 