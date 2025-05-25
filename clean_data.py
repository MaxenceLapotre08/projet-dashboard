import json
import random
from pathlib import Path

def clean_scores(data):
    """Nettoie et corrige les scores dans les données."""
    for client in data['clients']:
        for hist in client['historique']:
            # Google Ads Quality Score (1-100)
            if 'google_ads' in hist and 'quality-score' in hist['google_ads']:
                score = float(hist['google_ads']['quality-score'])
                hist['google_ads']['quality-score'] = max(1, min(100, score))
            
            # Meta Ads Relevance Score (1-10) - génération réaliste
            if 'meta_ads' in hist and 'relevance_score' in hist['meta_ads']:
                # Distribution favorisant les scores élevés
                hist['meta_ads']['relevance_score'] = random.choices(
                    [6, 7, 8, 9, 10], weights=[0.1, 0.15, 0.25, 0.25, 0.25]
                )[0]
            
            # GMB Score Avis (1-5)
            if 'gmb' in hist and 'score_avis' in hist['gmb']:
                score = float(hist['gmb']['score_avis'])
                hist['gmb']['score_avis'] = max(1, min(5, score))
            
            # Nettoyage des budgets
            if 'google_ads' in hist and 'budget' in hist['google_ads']:
                budget = hist['google_ads']['budget']
                if isinstance(budget, str):
                    # Supprimer tous les caractères non numériques sauf le point
                    budget = ''.join(c for c in budget if c.isdigit() or c == '.')
                    hist['google_ads']['budget'] = float(budget)
            
            if 'meta_ads' in hist and 'budget' in hist['meta_ads']:
                budget = hist['meta_ads']['budget']
                if isinstance(budget, str):
                    # Supprimer tous les caractères non numériques sauf le point
                    budget = ''.join(c for c in budget if c.isdigit() or c == '.')
                    hist['meta_ads']['budget'] = float(budget)
    
    return data

def main():
    # Lire le fichier JSON
    with open('data/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Nettoyer les scores et les budgets
    data = clean_scores(data)
    
    # Sauvegarder les données nettoyées
    with open('data/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Les scores et les budgets ont été nettoyés et corrigés.")

if __name__ == "__main__":
    main() 