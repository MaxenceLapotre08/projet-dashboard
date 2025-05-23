import pandas as pd
import numpy as np

def clean_numeric_value(value):
    """Nettoie une valeur numérique en retirant les symboles monétaires et les séparateurs."""
    if pd.isna(value):
        return np.nan
    
    if isinstance(value, (int, float)):
        return float(value)
        
    try:
        # Retire le symbole € et les espaces
        value = str(value).replace('€', '').strip()
        # Retire le symbole % et les espaces
        value = value.replace('%', '').strip()
        # Remplace la virgule par un point pour les décimales
        value = value.replace(',', '.')
        # Retire les espaces insécables et les espaces normaux
        value = value.replace('\u202f', '').replace(' ', '')
        return float(value)
    except (ValueError, TypeError):
        return np.nan

def clean_data(input_file, output_file):
    """Nettoie et normalise les données du fichier CSV."""
    # Lecture du fichier CSV
    df = pd.read_csv(input_file)
    
    # Nettoyage des noms de colonnes
    column_mapping = {
        'Site-internet_ImpresSite-internetons': 'site_impressions',
        'Site-internet_Nombre de viSite-internettes': 'site_visites',
        'Site-internet_CTR': 'site_ctr',
        'Site-internet_Durée moyenne des viSite-internettes': 'site_duree_moyenne',
        'Site-internet_Taux de rebond': 'site_taux_rebond',
        'Site-internet_Nombre d\'appels': 'site_appels',
        'Site-internet_Nombre de formulaires': 'site_formulaires',
        'Site-internet_Nombre de contacts': 'site_contacts',
        'Site-internet_Coût par contact': 'site_cout_contact',
        'Site-internet_Taux de converSite-interneton': 'site_taux_conversion',
        'Google-Ads_Budget investi': 'google_budget',
        'Google-Ads_ImpresSite-internetons': 'google_impressions',
        'Google-Ads_Clics': 'google_clics',
        'Google-Ads_CTR': 'google_ctr',
        'Google-Ads_Taux de converSite-interneton': 'google_taux_conversion',
        'Google-Ads_Appels': 'google_appels',
        'Google-Ads_Formulaires': 'google_formulaires',
        'Google-Ads_Contacts': 'google_contacts',
        'Google-Ads_Coût par contact': 'google_cout_contact',
        'Meta-Ads_Budget investi': 'meta_budget',
        'Meta-Ads_ImpresSite-internetons': 'meta_impressions',
        'Meta-Ads_Clics': 'meta_clics',
        'Meta-Ads_CTR': 'meta_ctr',
        'Meta-Ads_Taux de converSite-interneton': 'meta_taux_conversion',
        'Meta-Ads_Appels': 'meta_appels',
        'Meta-Ads_Formulaires': 'meta_formulaires',
        'Meta-Ads_Contacts': 'meta_contacts',
        'Meta-Ads_Coût par contact': 'meta_cout_contact',
        'GMB_Vues': 'gmb_vues',
        'GMB_Clics Site-internette web': 'gmb_clics_site',
        'GMB_DeMeta-Adsnde d\'itinéraire': 'gmb_demandes_itineraire',
        'GMB_Appels': 'gmb_appels',
        'GMB_Taux d\'interaction': 'gmb_taux_interaction',
        'GMB_Taux d\'appel': 'gmb_taux_appel',
        'GMB_Nombre d\'avis': 'gmb_nombre_avis',
        'GMB_Score moyen des avis': 'gmb_score_avis',
        'GMB_Réservations': 'gmb_reservations'
    }
    
    df = df.rename(columns=column_mapping)
    
    # Colonnes à nettoyer
    monetary_columns = [
        'site_cout_contact',
        'google_budget',
        'google_cout_contact',
        'meta_budget',
        'meta_cout_contact'
    ]
    
    percentage_columns = [
        'site_ctr',
        'site_taux_rebond',
        'site_taux_conversion',
        'google_ctr',
        'google_taux_conversion',
        'meta_ctr',
        'meta_taux_conversion',
        'gmb_taux_interaction',
        'gmb_taux_appel'
    ]
    
    # Nettoyage des colonnes monétaires
    for col in monetary_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric_value)
    
    # Nettoyage des colonnes en pourcentage
    for col in percentage_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric_value)
            # Conversion en pourcentage (0-100)
            df[col] = df[col] / 100 if df[col].max() > 1 else df[col]
    
    # Sauvegarde des données nettoyées
    df.to_csv(output_file, index=False)
    print(f"Données nettoyées sauvegardées dans {output_file}")

if __name__ == "__main__":
    clean_data("data/data.csv", "data/data_cleaned.csv") 