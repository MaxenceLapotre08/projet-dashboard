import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

def format_currency(value: float) -> str:
    """Formate une valeur en devise."""
    return f"{value:,.2f} €"

def format_percentage(value: float) -> str:
    """Formate une valeur en pourcentage."""
    return f"{value:.2f}%"

def format_number(value: float) -> str:
    """Formate une valeur numérique en entier."""
    return f"{int(value):,}"  # Conversion en entier et formatage avec séparateurs de milliers

def clean_numeric_value(value: str) -> float:
    """Nettoie une valeur numérique en retirant les caractères spéciaux et en convertissant les virgules en points."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remplace les espaces insécables et les espaces normaux
        value = value.replace('\u202f', '').replace(' ', '')
        # Remplace les virgules par des points
        value = value.replace(',', '.')
        try:
            return float(value)
        except ValueError:
            print(f"Impossible de convertir la valeur: {value}")
            return 0.0
    return 0.0

def safe_sum(data: pd.DataFrame, column: str) -> float:
    """Calcule la somme d'une colonne en gérant les valeurs manquantes."""
    if column not in data.columns:
        print(f"Colonne {column} non trouvée dans les données")
        return 0
    try:
        # Nettoie et convertit chaque valeur avant de faire la somme
        return sum(clean_numeric_value(x) for x in data[column])
    except Exception as e:
        print(f"Erreur lors du calcul de la somme pour {column}: {str(e)}")
        return 0

def safe_mean(data: pd.DataFrame, column: str) -> float:
    """Calcule la moyenne d'une colonne en gérant les valeurs manquantes."""
    if column not in data.columns:
        print(f"Colonne {column} non trouvée dans les données")
        return 0
    try:
        # Nettoie et convertit chaque valeur avant de calculer la moyenne
        values = [clean_numeric_value(x) for x in data[column]]
        return sum(values) / len(values) if values else 0
    except Exception as e:
        print(f"Erreur lors du calcul de la moyenne pour {column}: {str(e)}")
        return 0

def display_kpis_grid(data: pd.DataFrame, kpis: dict, title: str) -> None:
    """Affiche une grille de KPIs avec un nombre variable de colonnes."""
    st.subheader(title)
    
    # Calculer le nombre de KPIs
    n_kpis = len(kpis)
    # Déterminer le nombre de colonnes optimal (3 ou 4 selon le nombre de KPIs)
    n_cols = 4 if n_kpis > 9 else 3
    
    # Créer les colonnes
    cols = st.columns(n_cols)
    
    # Afficher chaque KPI dans une colonne
    for i, (kpi_name, kpi_data) in enumerate(kpis.items()):
        col_idx = i % n_cols
        with cols[col_idx]:
            if isinstance(kpi_data, dict):
                # Si c'est un KPI calculé
                value = kpi_data['value'](data)
                format_func = kpi_data.get('format', str)
                st.metric(kpi_name, format_func(value))
            else:
                # Si c'est un KPI direct
                value = safe_sum(data, kpi_data) if 'total' in kpi_name.lower() else safe_mean(data, kpi_data)
                format_func = format_currency if 'budget' in kpi_name.lower() or 'cout' in kpi_name.lower() else format_number
                st.metric(kpi_name, format_func(value))

def display_site_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs du site internet."""
    kpis = {
        'Impressions': 'site_impressions',
        'Visites': 'site_visites',
        'CTR': {
            'value': lambda df: (safe_sum(df, 'site_visites') / safe_sum(df, 'site_impressions') * 100) if safe_sum(df, 'site_impressions') > 0 else 0,
            'format': format_percentage
        },
        'Taux de Rebond': {
            'value': lambda df: safe_mean(df, 'site_taux_rebond') * 100,
            'format': format_percentage
        },
        'Durée Moyenne': {
            'value': lambda df: safe_mean(df, 'site_duree_moyenne') / 60,
            'format': lambda x: f"{x:.1f} min"
        },
        'Position Moyenne': {
            'value': lambda df: safe_mean(df, 'site_position_moyenne'),
            'format': lambda x: f"{x:.1f}"
        },
        'Appels': 'site_nombre_appels',
        'Formulaires': 'site_formulaires',
        'Contacts': {
            'value': lambda df: safe_sum(df, 'site_nombre_appels') + safe_sum(df, 'site_formulaires'),
            'format': format_number
        },
        'Coût Contact': 'site_cout_contact'
    }
    display_kpis_grid(data, kpis, "📱 Site Internet")

def display_google_ads_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs de Google Ads."""
    kpis = {
        'Budget': 'google_ads_budget',
        'Impressions': 'google_ads_impressions',
        'Clics': 'google_ads_clics',
        'CTR': {
            'value': lambda df: (safe_sum(df, 'google_ads_clics') / safe_sum(df, 'google_ads_impressions') * 100) if safe_sum(df, 'google_ads_impressions') > 0 else 0,
            'format': format_percentage
        },
        'Taux de Conversion': {
            'value': lambda df: (safe_sum(df, 'google_ads_contacts') / safe_sum(df, 'google_ads_clics') * 100) if safe_sum(df, 'google_ads_clics') > 0 else 0,
            'format': format_percentage
        },
        'Appels': 'google_ads_appels',
        'Formulaires': 'google_ads_formulaires',
        'Contacts': 'google_ads_contacts',
        'Coût Contact': 'google_ads_cout_contact',
        'Quality Score': {
            'value': lambda df: safe_mean(df, 'google_ads_quality_score'),
            'format': lambda x: f"{x:.1f}/100"
        },
        'Durée Moyenne': {
            'value': lambda df: safe_mean(df, 'google_ads_durée_moyenne_visite') / 60,
            'format': lambda x: f"{x:.1f} min"
        },
        'Taux de Rebond': {
            'value': lambda df: safe_mean(df, 'google_ads_taux_de_rebond') * 100,
            'format': format_percentage
        }
    }
    display_kpis_grid(data, kpis, "🔍 Google Ads")

def display_meta_ads_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs de Meta Ads."""
    kpis = {
        'Budget': 'meta_ads_budget',
        'Impressions': 'meta_ads_impressions',
        'Clics': 'meta_ads_clics',
        'CTR': {
            'value': lambda df: (safe_sum(df, 'meta_ads_clics') / safe_sum(df, 'meta_ads_impressions') * 100) if safe_sum(df, 'meta_ads_impressions') > 0 else 0,
            'format': format_percentage
        },
        'Taux de Conversion': {
            'value': lambda df: (safe_sum(df, 'meta_ads_contacts') / safe_sum(df, 'meta_ads_clics') * 100) if safe_sum(df, 'meta_ads_clics') > 0 else 0,
            'format': format_percentage
        },
        'Appels': 'meta_ads_appels',
        'Formulaires': 'meta_ads_formulaires',
        'Contacts': 'meta_ads_contacts',
        'Coût Contact': 'meta_ads_cout_contact',
        'Relevance Score': {
            'value': lambda df: safe_mean(df, 'meta_ads_relevance_score'),
            'format': lambda x: f"{x:.1f}/10"
        },
        'Durée Moyenne': {
            'value': lambda df: safe_mean(df, 'meta_ads_durée_moyenne_visite') / 60,
            'format': lambda x: f"{x:.1f} min"
        },
        'Taux de Rebond': {
            'value': lambda df: safe_mean(df, 'meta_ads_taux_de_rebond') * 100,
            'format': format_percentage
        },
        'Taux d\'Interaction': {
            'value': lambda df: safe_mean(df, 'meta_ads_taux_interaction') * 100,
            'format': format_percentage
        }
    }
    display_kpis_grid(data, kpis, "📘 Meta Ads")

def display_gmb_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs de Google My Business."""
    kpis = {
        'Vues': 'gmb_impressions',
        'Clics Site': 'gmb_clics_site',
        'Itinéraires': 'gmb_demande_d_itineraire',
        'Appels': 'gmb_appels',
        'Réservations': 'gmb_reservations',
        'Score Avis': {
            'value': lambda df: safe_mean(df, 'gmb_score_avis'),
            'format': lambda x: f"{x:.1f}/5"
        },
        'Nombre Avis': 'gmb_nombre_avis',
        'Taux d\'Interaction': {
            'value': lambda df: safe_mean(df, 'gmb_taux_d_interaction') * 100,
            'format': format_percentage
        },
        'Taux d\'Appel': {
            'value': lambda df: safe_mean(df, 'gmb_taux_d_appel') * 100,
            'format': format_percentage
        },
        'Taux de Réservation': {
            'value': lambda df: safe_mean(df, 'gmb_taux_de_reservation') * 100,
            'format': format_percentage
        },
        'Vues Meta Mobile': 'gmb_vues_meta_adsps_mobile',
        'Vues Meta Desktop': 'gmb_vues_meta_adsps_desktop',
        'Vues Google Mobile': 'gmb_vues_recherche_google_mobile',
        'Vues Google Desktop': 'gmb_vues_recherche_google_desktop'
    }
    display_kpis_grid(data, kpis, "📍 Google My Business")

def display_canal_comparison(data: pd.DataFrame, metric: str) -> None:
    """Affiche une comparaison des métriques entre les canaux."""
    metric_mapping = {
        'impressions': {
            'site': 'site_impressions',
            'google_ads': 'google_ads_impressions',
            'meta_ads': 'meta_ads_impressions',
            'gmb': 'gmb_impressions'
        },
        'clics': {
            'site': 'site_visites',
            'google_ads': 'google_ads_clics',
            'meta_ads': 'meta_ads_clics',
            'gmb': 'gmb_clics_site'
        },
        'ctr': {
            'site': 'site_ctr',
            'google_ads': 'google_ads_ctr',
            'meta_ads': 'meta_ads_ctr',
            'gmb': 'gmb_taux_interaction'
        },
        'taux_conversion': {
            'site': 'site_taux_conversion',
            'google_ads': 'google_ads_taux_conversion',
            'meta_ads': 'meta_ads_taux_conversion',
            'gmb': 'gmb_taux_appel'
        },
        'cout_contact': {
            'site': 'site_cout_contact',
            'google_ads': 'google_ads_cout_contact',
            'meta_ads': 'meta_ads_cout_contact',
            'gmb': None
        },
        'appels': {
            'site': 'site_nombre_appels',
            'google_ads': 'google_ads_appels',
            'meta_ads': 'meta_ads_appels',
            'gmb': 'gmb_appels'
        },
        'formulaires': {
            'site': 'site_formulaires',
            'google_ads': 'google_ads_formulaires',
            'meta_ads': 'meta_ads_formulaires',
            'gmb': None
        },
        'contacts': {
            'site': 'site_contacts',
            'google_ads': 'google_ads_contacts',
            'meta_ads': 'meta_ads_contacts',
            'gmb': None
        }
    }
    
    if metric not in metric_mapping:
        st.error(f"Métrique {metric} non supportée")
        return
    
    # Préparation des données pour le graphique
    canal_data = []
    for canal, col_name in metric_mapping[metric].items():
        if col_name is not None:
            value = safe_sum(data, col_name)
            if metric in ['ctr', 'taux_conversion']:
                value = value * 100  # Conversion en pourcentage
            canal_data.append({
                'Canal': canal.replace('_', ' ').title(),
                'Valeur': value
            })
    
    if not canal_data:
        st.error("Aucune donnée disponible pour cette métrique")
        return
    
    # Création du graphique
    fig = px.bar(
        pd.DataFrame(canal_data),
        x='Canal',
        y='Valeur',
        title=f"Comparaison des {metric.replace('_', ' ').title()} par canal",
        labels={'Valeur': metric.replace('_', ' ').title()}
    )
    
    # Personnalisation du graphique
    fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="",
        title_x=0.5,
        title_y=0.95
    )
    
    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True) 