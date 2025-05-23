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

def display_site_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs du site internet."""
    total_impressions = safe_sum(data, 'site_impressions')
    total_visits = safe_sum(data, 'site_visites')
    total_forms = safe_sum(data, 'site_formulaires')
    total_calls = safe_sum(data, 'site_nombre_appels')
    total_contacts = total_forms + total_calls
    
    # Calcul des taux réels avec vérification des divisions par zéro
    real_ctr = (total_visits / total_impressions * 100) if total_impressions > 0 else 0
    real_bounce_rate = safe_mean(data, 'site_taux_rebond') * 100  # Conversion en pourcentage
    real_conversion_rate = (total_contacts / total_visits * 100) if total_visits > 0 else 0
    real_cost_per_contact = safe_mean(data, 'site_cout_contact')
    
    # Conversion de la durée moyenne de secondes en minutes
    duree_moyenne = safe_mean(data, 'site_duree_moyenne') / 60  # Conversion en minutes
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Impressions", format_number(total_impressions))
        st.metric("Visites", format_number(total_visits))
        st.metric("CTR", format_percentage(real_ctr))
    
    with col2:
        st.metric("Durée moyenne", f"{duree_moyenne:.1f} min")
        st.metric("Taux de rebond", format_percentage(real_bounce_rate))
        st.metric("Coût par contact", format_currency(real_cost_per_contact))
    
    with col3:
        st.metric("Appels", format_number(total_calls))
        st.metric("Formulaires", format_number(total_forms))
        st.metric("Contacts", format_number(total_contacts))

def display_google_ads_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs de Google Ads."""
    total_budget = safe_sum(data, 'google_budget')
    total_impressions = safe_sum(data, 'google_impressions')
    total_clicks = safe_sum(data, 'google_clics')
    total_forms = safe_sum(data, 'google_formulaires')
    total_calls = safe_sum(data, 'google_appels')
    total_contacts = total_forms + total_calls  # Les contacts sont la somme des appels et formulaires
    
    # Calcul des taux réels
    real_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    real_conversion_rate = (total_contacts / total_clicks * 100) if total_clicks > 0 else 0
    real_cost_per_contact = (total_budget / total_contacts) if total_contacts > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Budget", format_currency(total_budget))
        st.metric("Impressions", format_number(total_impressions))
        st.metric("Clics", format_number(total_clicks))
    
    with col2:
        st.metric("CTR", format_percentage(real_ctr))
        st.metric("Taux de conversion", format_percentage(real_conversion_rate))
        st.metric("Coût par contact", format_currency(real_cost_per_contact))
    
    with col3:
        st.metric("Appels", format_number(total_calls))
        st.metric("Formulaires", format_number(total_forms))
        st.metric("Contacts", format_number(total_contacts))

def display_meta_ads_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs de Meta Ads."""
    total_budget = safe_sum(data, 'meta_budget')
    total_impressions = safe_sum(data, 'meta_impressions')
    total_clicks = safe_sum(data, 'meta_clics')
    total_forms = safe_sum(data, 'meta_formulaires')
    total_calls = safe_sum(data, 'meta_appels')
    total_contacts = total_forms + total_calls  # Les contacts sont la somme des appels et formulaires
    
    # Calcul des taux réels
    real_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    real_conversion_rate = (total_contacts / total_clicks * 100) if total_clicks > 0 else 0
    real_cost_per_contact = (total_budget / total_contacts) if total_contacts > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Budget", format_currency(total_budget))
        st.metric("Impressions", format_number(total_impressions))
        st.metric("Clics", format_number(total_clicks))
    
    with col2:
        st.metric("CTR", format_percentage(real_ctr))
        st.metric("Taux de conversion", format_percentage(real_conversion_rate))
        st.metric("Coût par contact", format_currency(real_cost_per_contact))
    
    with col3:
        st.metric("Appels", format_number(total_calls))
        st.metric("Formulaires", format_number(total_forms))
        st.metric("Contacts", format_number(total_contacts))

def display_gmb_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs de Google My Business."""
    total_views = safe_sum(data, 'gmb_impressions')
    total_clicks = safe_sum(data, 'gmb_clics_site')
    total_directions = safe_sum(data, 'gmb_demande_d_itineraire')
    total_calls = safe_sum(data, 'gmb_appels')
    
    # Calcul des taux réels avec vérification des divisions par zéro
    total_interactions = total_clicks + total_directions + total_calls
    real_interaction_rate = (total_interactions / total_views * 100) if total_views > 0 else 0
    real_call_rate = (total_calls / total_views * 100) if total_views > 0 else 0
    
    # Conversion du score moyen sur 5
    score_avis = safe_mean(data, 'gmb_score_avis')
    if score_avis > 5:  # Si le score est sur 100, on le convertit sur 5
        score_avis = score_avis / 20
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vues", format_number(total_views))
        st.metric("Clics site", format_number(total_clicks))
        st.metric("Demandes d'itinéraire", format_number(total_directions))
    
    with col2:
        st.metric("Appels", format_number(total_calls))
        st.metric("Taux d'interaction", format_percentage(real_interaction_rate))
        st.metric("Taux d'appel", format_percentage(real_call_rate))
    
    with col3:
        st.metric("Nombre d'avis", format_number(safe_sum(data, 'gmb_nombre_avis')))
        st.metric("Score moyen", f"{score_avis:.1f}/5")
        st.metric("Réservations", format_number(safe_sum(data, 'gmb_reservations')))

def display_canal_comparison(data: pd.DataFrame, metric: str) -> None:
    """Affiche une comparaison des métriques entre les canaux."""
    metric_mapping = {
        'impressions': {
            'site': 'site_impressions',
            'google_ads': 'google_impressions',
            'meta_ads': 'meta_impressions',
            'gmb': 'gmb_impressions'
        },
        'clics': {
            'site': 'site_visites',
            'google_ads': 'google_clics',
            'meta_ads': 'meta_clics',
            'gmb': 'gmb_clics_site'
        },
        'ctr': {
            'site': 'site_ctr',
            'google_ads': 'google_ctr',
            'meta_ads': 'meta_ctr',
            'gmb': 'gmb_taux_interaction'
        },
        'taux_conversion': {
            'site': 'site_taux_conversion',
            'google_ads': 'google_taux_conversion',
            'meta_ads': 'meta_taux_conversion',
            'gmb': 'gmb_taux_appel'
        },
        'cout_contact': {
            'site': 'site_cout_contact',
            'google_ads': 'google_cout_contact',
            'meta_ads': 'meta_cout_contact',
            'gmb': None
        },
        'appels': {
            'site': 'site_nombre_appels',
            'google_ads': 'google_appels',
            'meta_ads': 'meta_appels',
            'gmb': 'gmb_appels'
        },
        'formulaires': {
            'site': 'site_formulaires',
            'google_ads': 'google_formulaires',
            'meta_ads': 'meta_formulaires',
            'gmb': None
        },
        'contacts': {
            'site': 'site_contacts',
            'google_ads': 'google_contacts',
            'meta_ads': 'meta_contacts',
            'gmb': 'gmb_reservations'
        }
    }
    
    if metric not in metric_mapping:
        st.error(f"Métrique {metric} non supportée")
        return
    
    # Préparation des données pour le graphique
    channels = []
    values = []
    
    for channel, column in metric_mapping[metric].items():
        if column is not None:
            value = safe_sum(data, column)
            channels.append(channel.replace('_', ' ').title())
            values.append(value)
    
    # Création du graphique
    fig = go.Figure(data=[
        go.Bar(
            x=channels,
            y=values,
            text=[format_number(v) if metric != 'cout_contact' else format_currency(v) for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=f"Comparaison {metric.replace('_', ' ').title()} par canal",
        xaxis_title="Canal",
        yaxis_title=metric.replace('_', ' ').title(),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True) 