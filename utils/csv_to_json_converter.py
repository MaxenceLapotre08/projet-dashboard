import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

def clean_numeric_value(value):
    """Nettoie une valeur numérique."""
    if pd.isna(value):
        return 0
    if isinstance(value, str):
        value = value.replace(',', '.').replace(' ', '')
        try:
            return float(value)
        except ValueError:
            return 0
    return float(value)

def generate_monthly_values(total_value, num_months=12, noise_level=0.1):
    """Génère des valeurs mensuelles réalistes à partir d'une valeur totale."""
    if total_value <= 0:
        return [0] * num_months
    
    # Calculer la moyenne mensuelle
    mean = total_value / num_months
    
    # Calculer l'écart-type en s'assurant qu'il est positif
    std = abs(mean * noise_level)
    
    # Générer des valeurs aléatoires avec un bruit gaussien
    values = np.random.normal(mean, std, num_months)
    
    # S'assurer que toutes les valeurs sont positives
    values = np.maximum(values, 0)
    
    # Ajuster la somme pour qu'elle soit égale à la valeur totale
    if np.sum(values) > 0:  # Éviter la division par zéro
        values = values * total_value / np.sum(values)
    
    return values.tolist()

def generate_monthly_rates(rate, num_months=12, noise_level=0.05):
    """Génère des taux mensuels réalistes à partir d'un taux global."""
    if rate <= 0:
        return [0] * num_months
    
    # Calculer l'écart-type en s'assurant qu'il est positif
    std = abs(rate * noise_level)
    
    # Générer des variations autour du taux d'origine
    values = np.random.normal(rate, std, num_months)
    
    # S'assurer que les valeurs sont entre 0 et 1
    values = np.clip(values, 0, 1)
    
    return values.tolist()

def convert_csv_to_json(csv_path, json_path):
    """Convertit le fichier CSV en JSON avec une structure hiérarchique et un historique de 12 mois."""
    # Lire le CSV
    df = pd.read_csv(csv_path)
    
    # Renommer les colonnes pour la cohérence
    df = df.rename(columns={
        'Activité': 'Activité',
        'Localité': 'Localité',
        'site_nombre_appels': 'site_appels',
        'gmb_impressions': 'gmb_vues',
        'gmb_demande_d_itineraire': 'gmb_demande_itineraire',
        'gmb_taux_d_interaction': 'gmb_taux_interaction',
        'gmb_taux_d_appel': 'gmb_taux_appel',
        'gmb_taux_de_reservation': 'gmb_taux_reservation',
        'gmb_vues_meta_adsps_mobile': 'gmb_vues_meta_mobile',
        'gmb_vues_meta_adsps_desktop': 'gmb_vues_meta_desktop',
        'gmb_vues_recherche_google_mobile': 'gmb_vues_google_mobile',
        'gmb_vues_recherche_google_desktop': 'gmb_vues_google_desktop'
    })
    
    # Créer la structure JSON
    json_data = {
        "clients": []
    }
    
    # Grouper par client
    for client in df['Client'].unique():
        client_data = df[df['Client'] == client].copy()
        
        client_json = {
            "id": client.lower().replace(' ', '_'),
            "nom": client,
            "activite": client_data['Activité'].iloc[0] if 'Activité' in client_data.columns else "",
            "localite": client_data['Localité'].iloc[0] if 'Localité' in client_data.columns else "",
            "historique": []
        }
        
        # Générer les 12 derniers mois
        current_date = datetime.now()
        for i in range(12):
            month_date = (current_date - timedelta(days=30 * i)).strftime('%Y-%m')
            
            # Pour chaque ligne du client, générer un historique mensuel
            for _, row in client_data.iterrows():
                historique = {
                    "date": month_date,
                    "site": {
                        "impressions": generate_monthly_values(clean_numeric_value(row.get('site_impressions', 0)))[i],
                        "visites": generate_monthly_values(clean_numeric_value(row.get('site_visites', 0)))[i],
                        "ctr": generate_monthly_rates(clean_numeric_value(row.get('site_ctr', 0)))[i],
                        "taux_rebond": generate_monthly_rates(clean_numeric_value(row.get('site_taux_rebond', 0)))[i],
                        "duree_moyenne": generate_monthly_values(clean_numeric_value(row.get('site_duree_moyenne', 0)))[i],
                        "position_moyenne": generate_monthly_values(clean_numeric_value(row.get('site_position_moyenne', 0)))[i],
                        "appels": generate_monthly_values(clean_numeric_value(row.get('site_appels', 0)))[i],
                        "formulaires": generate_monthly_values(clean_numeric_value(row.get('site_formulaires', 0)))[i],
                        "contacts": generate_monthly_values(clean_numeric_value(row.get('site_contacts', 0)))[i],
                        "cout_contact": generate_monthly_values(clean_numeric_value(row.get('site_cout_contact', 0)))[i]
                    },
                    "google_ads": {
                        "budget": generate_monthly_values(clean_numeric_value(row.get('google_budget', 0)))[i],
                        "impressions": generate_monthly_values(clean_numeric_value(row.get('google_impressions', 0)))[i],
                        "clics": generate_monthly_values(clean_numeric_value(row.get('google_clics', 0)))[i],
                        "ctr": generate_monthly_rates(clean_numeric_value(row.get('google_ctr', 0)))[i],
                        "taux_conversion": generate_monthly_rates(clean_numeric_value(row.get('google_taux_conversion', 0)))[i],
                        "appels": generate_monthly_values(clean_numeric_value(row.get('google_appels', 0)))[i],
                        "formulaires": generate_monthly_values(clean_numeric_value(row.get('google_formulaires', 0)))[i],
                        "contacts": generate_monthly_values(clean_numeric_value(row.get('google_contacts', 0)))[i],
                        "cout_contact": generate_monthly_values(clean_numeric_value(row.get('google_cout_contact', 0)))[i],
                        "quality_score": generate_monthly_values(clean_numeric_value(row.get('google_quality-score', 0)))[i]
                    },
                    "meta_ads": {
                        "budget": generate_monthly_values(clean_numeric_value(row.get('meta_budget', 0)))[i],
                        "impressions": generate_monthly_values(clean_numeric_value(row.get('meta_impressions', 0)))[i],
                        "clics": generate_monthly_values(clean_numeric_value(row.get('meta_clics', 0)))[i],
                        "ctr": generate_monthly_rates(clean_numeric_value(row.get('meta_ctr', 0)))[i],
                        "taux_conversion": generate_monthly_rates(clean_numeric_value(row.get('meta_taux_conversion', 0)))[i],
                        "appels": generate_monthly_values(clean_numeric_value(row.get('meta_appels', 0)))[i],
                        "formulaires": generate_monthly_values(clean_numeric_value(row.get('meta_formulaires', 0)))[i],
                        "contacts": generate_monthly_values(clean_numeric_value(row.get('meta_contacts', 0)))[i],
                        "cout_contact": generate_monthly_values(clean_numeric_value(row.get('meta_cout_contact', 0)))[i],
                        "relevance_score": generate_monthly_values(clean_numeric_value(row.get('meta_relevance_score', 0)))[i]
                    },
                    "gmb": {
                        "vues": generate_monthly_values(clean_numeric_value(row.get('gmb_vues', 0)))[i],
                        "clics_site": generate_monthly_values(clean_numeric_value(row.get('gmb_clics_site', 0)))[i],
                        "demande_itineraire": generate_monthly_values(clean_numeric_value(row.get('gmb_demande_itineraire', 0)))[i],
                        "appels": generate_monthly_values(clean_numeric_value(row.get('gmb_appels', 0)))[i],
                        "reservations": generate_monthly_values(clean_numeric_value(row.get('gmb_reservations', 0)))[i],
                        "score_avis": generate_monthly_values(clean_numeric_value(row.get('gmb_score_avis', 0)))[i],
                        "nombre_avis": generate_monthly_values(clean_numeric_value(row.get('gmb_nombre_avis', 0)))[i],
                        "taux_interaction": generate_monthly_rates(clean_numeric_value(row.get('gmb_taux_interaction', 0)))[i],
                        "taux_appel": generate_monthly_rates(clean_numeric_value(row.get('gmb_taux_appel', 0)))[i],
                        "taux_reservation": generate_monthly_rates(clean_numeric_value(row.get('gmb_taux_reservation', 0)))[i],
                        "vues_meta_mobile": generate_monthly_values(clean_numeric_value(row.get('gmb_vues_meta_mobile', 0)))[i],
                        "vues_meta_desktop": generate_monthly_values(clean_numeric_value(row.get('gmb_vues_meta_desktop', 0)))[i],
                        "vues_google_mobile": generate_monthly_values(clean_numeric_value(row.get('gmb_vues_google_mobile', 0)))[i],
                        "vues_google_desktop": generate_monthly_values(clean_numeric_value(row.get('gmb_vues_google_desktop', 0)))[i]
                    }
                }
                client_json["historique"].append(historique)
        
        json_data["clients"].append(client_json)
    
    # Créer le dossier de sortie s'il n'existe pas
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder le JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"Conversion terminée. Fichier JSON créé : {json_path}")

if __name__ == "__main__":
    # Chemins des fichiers
    csv_path = "data/data_cleaned.csv"
    json_path = "data/data.json"
    
    # Exécuter la conversion
    convert_csv_to_json(csv_path, json_path) 