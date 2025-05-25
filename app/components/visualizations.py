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
                value = safe_sum(data, kpi_name) if 'total' in kpi_name.lower() else safe_mean(data, kpi_name)
                format_func = format_currency if 'budget' in kpi_name.lower() or 'cout' in kpi_name.lower() else format_number
                st.metric(kpi_name, format_func(value))

def display_site_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs du site internet."""
    kpis = {
        'Impressions': {
            'value': lambda df: safe_sum(df, 'site_impressions'),
            'format': format_number
        },
        'Visites': {
            'value': lambda df: safe_sum(df, 'site_visites'),
            'format': format_number
        },
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
        'Appels': {
            'value': lambda df: safe_sum(df, 'site_nombre_appels'),
            'format': format_number
        },
        'Formulaires': {
            'value': lambda df: safe_sum(df, 'site_formulaires'),
            'format': format_number
        },
        'Contacts': {
            'value': lambda df: safe_sum(df, 'site_nombre_appels') + safe_sum(df, 'site_formulaires'),
            'format': format_number
        },
        'Coût Contact': {
            'value': lambda df: safe_mean(df, 'site_cout_contact'),
            'format': format_currency
        }
    }
    display_kpis_grid(data, kpis, "📱 Site Internet")

def display_google_ads_kpis(data: pd.DataFrame) -> None:
    """Affiche les KPIs de Google Ads."""
    kpis = {
        'Budget': {
            'value': lambda df: safe_sum(df, 'google_ads_budget'),
            'format': format_currency
        },
        'Impressions': {
            'value': lambda df: safe_sum(df, 'google_ads_impressions'),
            'format': format_number
        },
        'Clics': {
            'value': lambda df: safe_sum(df, 'google_ads_clics'),
            'format': format_number
        },
        'CTR': {
            'value': lambda df: (safe_sum(df, 'google_ads_clics') / safe_sum(df, 'google_ads_impressions') * 100) if safe_sum(df, 'google_ads_impressions') > 0 else 0,
            'format': format_percentage
        },
        'Taux de Conversion': {
            'value': lambda df: (safe_sum(df, 'google_ads_contacts') / safe_sum(df, 'google_ads_clics') * 100) if safe_sum(df, 'google_ads_clics') > 0 else 0,
            'format': format_percentage
        },
        'Appels': {
            'value': lambda df: safe_sum(df, 'google_ads_appels'),
            'format': format_number
        },
        'Formulaires': {
            'value': lambda df: safe_sum(df, 'google_ads_formulaires'),
            'format': format_number
        },
        'Contacts': {
            'value': lambda df: safe_sum(df, 'google_ads_contacts'),
            'format': format_number
        },
        'Coût Contact': {
            'value': lambda df: safe_mean(df, 'google_ads_cout_contact'),
            'format': format_currency
        },
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
        'Budget': {
            'value': lambda df: safe_sum(df, 'meta_ads_budget'),
            'format': format_currency
        },
        'Impressions': {
            'value': lambda df: safe_sum(df, 'meta_ads_impressions'),
            'format': format_number
        },
        'Clics': {
            'value': lambda df: safe_sum(df, 'meta_ads_clics'),
            'format': format_number
        },
        'CTR': {
            'value': lambda df: (safe_sum(df, 'meta_ads_clics') / safe_sum(df, 'meta_ads_impressions') * 100) if safe_sum(df, 'meta_ads_impressions') > 0 else 0,
            'format': format_percentage
        },
        'Taux de Conversion': {
            'value': lambda df: (safe_sum(df, 'meta_ads_contacts') / safe_sum(df, 'meta_ads_clics') * 100) if safe_sum(df, 'meta_ads_clics') > 0 else 0,
            'format': format_percentage
        },
        'Appels': {
            'value': lambda df: safe_sum(df, 'meta_ads_appels'),
            'format': format_number
        },
        'Formulaires': {
            'value': lambda df: safe_sum(df, 'meta_ads_formulaires'),
            'format': format_number
        },
        'Contacts': {
            'value': lambda df: safe_sum(df, 'meta_ads_contacts'),
            'format': format_number
        },
        'Coût Contact': {
            'value': lambda df: safe_mean(df, 'meta_ads_cout_contact'),
            'format': format_currency
        },
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
        'Vues': {
            'value': lambda df: safe_sum(df, 'gmb_impressions'),
            'format': format_number
        },
        'Clics Site': {
            'value': lambda df: safe_sum(df, 'gmb_clics_site'),
            'format': format_number
        },
        'Itinéraires': {
            'value': lambda df: safe_sum(df, 'gmb_demande_d_itineraire'),
            'format': format_number
        },
        'Appels': {
            'value': lambda df: safe_sum(df, 'gmb_appels'),
            'format': format_number
        },
        'Réservations': {
            'value': lambda df: safe_sum(df, 'gmb_reservations'),
            'format': format_number
        },
        'Score Avis': {
            'value': lambda df: safe_mean(df, 'gmb_score_avis'),
            'format': lambda x: f"{x:.1f}/5"
        },
        'Nombre Avis': {
            'value': lambda df: safe_sum(df, 'gmb_nombre_avis'),
            'format': format_number
        },
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
        'Vues Meta Mobile': {
            'value': lambda df: safe_sum(df, 'gmb_vues_meta_adsps_mobile'),
            'format': format_number
        },
        'Vues Meta Desktop': {
            'value': lambda df: safe_sum(df, 'gmb_vues_meta_adsps_desktop'),
            'format': format_number
        },
        'Vues Google Mobile': {
            'value': lambda df: safe_sum(df, 'gmb_vues_recherche_google_mobile'),
            'format': format_number
        },
        'Vues Google Desktop': {
            'value': lambda df: safe_sum(df, 'gmb_vues_recherche_google_desktop'),
            'format': format_number
        }
    }
    display_kpis_grid(data, kpis, "📍 Google My Business")

def display_canal_comparison(data: pd.DataFrame, metric: str) -> None:
    """Affiche une comparaison des métriques entre les produits."""
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
            'site': ('site_visites', 'site_impressions'),  # (clics, impressions)
            'google_ads': ('google_ads_clics', 'google_ads_impressions'),
            'meta_ads': ('meta_ads_clics', 'meta_ads_impressions'),
            'gmb': ('gmb_clics_site', 'gmb_impressions')
        },
        'taux_conversion': {
            'site': ('site_contacts', 'site_visites'),  # (contacts, visites)
            'google_ads': ('google_ads_contacts', 'google_ads_clics'),
            'meta_ads': ('meta_ads_contacts', 'meta_ads_clics'),
            'gmb': ('gmb_appels', 'gmb_impressions')
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
    product_data = []
    for product, col_info in metric_mapping[metric].items():
        if col_info is not None:
            if metric in ['ctr', 'taux_conversion']:
                # Pour les taux, on calcule le ratio global
                clicks_col, impressions_col = col_info
                clicks = safe_sum(data, clicks_col)
                impressions = safe_sum(data, impressions_col)
                value = (clicks / impressions * 100) if impressions > 0 else 0
            elif metric in ['cout_contact', 'taux_rebond', 'duree_moyenne']:
                # Pour ces métriques, on utilise la moyenne
                value = safe_mean(data, col_info)
            else:
                # Pour les autres métriques, on utilise la somme
                value = safe_sum(data, col_info)
            product_data.append({
                'Produit': product.replace('_', ' ').title(),
                'Valeur': value
            })
    
    if not product_data:
        st.error("Aucune donnée disponible pour cette métrique")
        return
    
    # Création du graphique
    fig = px.bar(
        pd.DataFrame(product_data),
        x='Produit',
        y='Valeur',
        title=f"Comparaison des {metric.replace('_', ' ').title()} par produit",
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
    
    # Ajout des valeurs sur les barres avec les unités appropriées
    if metric in ['ctr', 'taux_conversion', 'taux_rebond']:
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    elif metric in ['cout_contact']:
        fig.update_traces(texttemplate='%{y:.2f}€', textposition='outside')
    elif metric in ['duree_moyenne']:
        fig.update_traces(texttemplate='%{y:.1f} min', textposition='outside')
    else:
        fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
    
    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)

def display_performance_analysis(data: pd.DataFrame) -> None:
    """Affiche l'analyse des performances par différents critères."""
    st.header("📊 Analyse des Performances")
    
    # Création des onglets pour chaque type d'analyse
    tab1, tab2, tab3 = st.tabs(["Clients", "Activités", "Localités"])
    
    with tab1:
        st.subheader("Performance par Client")
        # Préparation des données pour les clients
        client_performance = data.groupby('Client').agg({
            'site_score_site_pondéré': 'mean',
            'google_ads_score_google_ads_pondéré': 'mean',
            'meta_ads_score_meta_ads_pondéré': 'mean',
            'gmb_score_gmb_pondéré': 'mean'
        }).reset_index()
        
        # Calcul du score global moyen
        client_performance['score_global'] = client_performance[[
            'site_score_site_pondéré', 
            'google_ads_score_google_ads_pondéré', 
            'meta_ads_score_meta_ads_pondéré', 
            'gmb_score_gmb_pondéré'
        ]].mean(axis=1)
        
        # Tri par score global
        client_performance = client_performance.sort_values('score_global', ascending=False)
        
        # Affichage du classement complet
        st.write("Classement complet des clients par performance :")
        for i, (_, row) in enumerate(client_performance.iterrows(), 1):
            st.write(f"{i}. {row['Client']} - Score global : {row['score_global']:.2f}")
            st.write(f"   - Site : {row['site_score_site_pondéré']:.2f}")
            st.write(f"   - Google Ads : {row['google_ads_score_google_ads_pondéré']:.2f}")
            st.write(f"   - Meta Ads : {row['meta_ads_score_meta_ads_pondéré']:.2f}")
            st.write(f"   - GMB : {row['gmb_score_gmb_pondéré']:.2f}")
            st.write("---")
    
    with tab2:
        st.subheader("Performance par Activité")
        # Préparation des données pour les activités
        activity_performance = data.groupby('Activité').agg({
            'site_score_site_pondéré': 'mean',
            'google_ads_score_google_ads_pondéré': 'mean',
            'meta_ads_score_meta_ads_pondéré': 'mean',
            'gmb_score_gmb_pondéré': 'mean'
        }).reset_index()
        
        # Calcul du score global moyen
        activity_performance['score_global'] = activity_performance[[
            'site_score_site_pondéré', 
            'google_ads_score_google_ads_pondéré', 
            'meta_ads_score_meta_ads_pondéré', 
            'gmb_score_gmb_pondéré'
        ]].mean(axis=1)
        
        # Tri par score global
        activity_performance = activity_performance.sort_values('score_global', ascending=False)
        
        # Affichage du classement complet
        st.write("Classement complet des activités par performance :")
        for i, (_, row) in enumerate(activity_performance.iterrows(), 1):
            st.write(f"{i}. {row['Activité']} - Score global : {row['score_global']:.2f}")
            st.write(f"   - Site : {row['site_score_site_pondéré']:.2f}")
            st.write(f"   - Google Ads : {row['google_ads_score_google_ads_pondéré']:.2f}")
            st.write(f"   - Meta Ads : {row['meta_ads_score_meta_ads_pondéré']:.2f}")
            st.write(f"   - GMB : {row['gmb_score_gmb_pondéré']:.2f}")
            st.write("---")
    
    with tab3:
        st.subheader("Performance par Localité")
        # Préparation des données pour les localités
        locality_performance = data.groupby('Localité').agg({
            'site_score_site_pondéré': 'mean',
            'google_ads_score_google_ads_pondéré': 'mean',
            'meta_ads_score_meta_ads_pondéré': 'mean',
            'gmb_score_gmb_pondéré': 'mean'
        }).reset_index()
        
        # Calcul du score global moyen
        locality_performance['score_global'] = locality_performance[[
            'site_score_site_pondéré', 
            'google_ads_score_google_ads_pondéré', 
            'meta_ads_score_meta_ads_pondéré', 
            'gmb_score_gmb_pondéré'
        ]].mean(axis=1)
        
        # Tri par score global
        locality_performance = locality_performance.sort_values('score_global', ascending=False)
        
        # Affichage du classement complet
        st.write("Classement complet des localités par performance :")
        for i, (_, row) in enumerate(locality_performance.iterrows(), 1):
            st.write(f"{i}. {row['Localité']} - Score global : {row['score_global']:.2f}")
            st.write(f"   - Site : {row['site_score_site_pondéré']:.2f}")
            st.write(f"   - Google Ads : {row['google_ads_score_google_ads_pondéré']:.2f}")
            st.write(f"   - Meta Ads : {row['meta_ads_score_meta_ads_pondéré']:.2f}")
            st.write(f"   - GMB : {row['gmb_score_gmb_pondéré']:.2f}")
            st.write("---")

def display_financial_metrics(data: pd.DataFrame) -> None:
    """Affiche les métriques financières (coût par contact et ROI) par produit et global."""
    st.header("💰 Métriques Financières")
    
    # Création des onglets pour chaque type d'analyse
    tab1, tab2, tab3 = st.tabs(["Par Produit", "Par Client", "Global"])
    
    with tab1:
        st.subheader("Coût par Contact et ROI par Produit")
        
        # Calcul des métriques par produit
        product_metrics = []
        
        # Site
        site_budget = 249 * len(data['date'].unique())  # Budget total sur la période
        site_contacts = safe_sum(data, 'site_contacts')
        site_cpc = safe_mean(data, 'site_cout_contact')  # Utilisation directe du coût par contact du site
        
        # Google Ads
        google_budget = safe_sum(data, 'google_ads_budget')
        google_contacts = safe_sum(data, 'google_ads_contacts')
        google_cpc = google_budget / google_contacts if google_contacts > 0 else 0
        
        # Meta Ads
        meta_budget = safe_sum(data, 'meta_ads_budget')
        meta_contacts = safe_sum(data, 'meta_ads_contacts')
        meta_cpc = meta_budget / meta_contacts if meta_contacts > 0 else 0
        
        # GMB
        gmb_budget = 99 * len(data['date'].unique())  # Budget mensuel de 99€
        gmb_contacts = safe_sum(data, 'gmb_appels') + safe_sum(data, 'gmb_reservations')  # Somme des appels et réservations
        gmb_cpc = gmb_budget / gmb_contacts if gmb_contacts > 0 else 0  # Coût par contact = budget total / nombre total de contacts
        
        # Ajout des métriques par produit
        product_metrics.extend([
            {
                'Produit': 'Site',
                'Budget': site_budget,
                'Contacts': site_contacts,
                'Coût par Contact': site_cpc
            },
            {
                'Produit': 'Google Ads',
                'Budget': google_budget,
                'Contacts': google_contacts,
                'Coût par Contact': google_cpc
            },
            {
                'Produit': 'Meta Ads',
                'Budget': meta_budget,
                'Contacts': meta_contacts,
                'Coût par Contact': meta_cpc
            },
            {
                'Produit': 'GMB',
                'Budget': gmb_budget,
                'Contacts': gmb_contacts,
                'Coût par Contact': gmb_cpc
            }
        ])
        
        # Création du DataFrame
        df_metrics = pd.DataFrame(product_metrics)
        
        # Affichage des métriques
        st.subheader("Coût par Contact")
        fig_cpc = px.bar(
            df_metrics,
            x='Produit',
            y='Coût par Contact',
            title="Coût par Contact par Produit",
            labels={'Coût par Contact': '€'}
        )
        fig_cpc.update_traces(texttemplate='%{y:.2f}€', textposition='outside')
        st.plotly_chart(fig_cpc, use_container_width=True)
    
    with tab2:
        st.subheader("Coût par Contact par Client")
        
        # Calcul des métriques par client
        client_metrics = []
        
        for client in data['Client'].unique():
            client_data = data[data['Client'] == client]
            
            # Calcul des métriques pour ce client
            total_budget = (
                safe_sum(client_data, 'google_ads_budget') +
                safe_sum(client_data, 'meta_ads_budget')
            )
            
            total_contacts = (
                safe_sum(client_data, 'site_contacts') +
                safe_sum(client_data, 'google_ads_contacts') +
                safe_sum(client_data, 'meta_ads_contacts') +
                safe_sum(client_data, 'gmb_appels')
            )
            
            cpc = total_budget / total_contacts if total_contacts > 0 else 0
            
            client_metrics.append({
                'Client': client,
                'Budget': total_budget,
                'Contacts': total_contacts,
                'Coût par Contact': cpc
            })
        
        # Création du DataFrame
        df_client_metrics = pd.DataFrame(client_metrics)
        df_client_metrics = df_client_metrics.sort_values('Coût par Contact', ascending=True)
        
        # Affichage des métriques
        st.subheader("Coût par Contact")
        fig_cpc = px.bar(
            df_client_metrics,
            x='Client',
            y='Coût par Contact',
            title="Coût par Contact par Client",
            labels={'Coût par Contact': '€'}
        )
        fig_cpc.update_traces(texttemplate='%{y:.2f}€', textposition='outside')
        st.plotly_chart(fig_cpc, use_container_width=True)
    
    with tab3:
        st.subheader("Métriques Financières Globales")
        
        # Calcul des métriques globales
        total_budget = (
            safe_sum(data, 'google_ads_budget') +
            safe_sum(data, 'meta_ads_budget')
        )
        
        total_contacts = (
            safe_sum(data, 'site_contacts') +
            safe_sum(data, 'google_ads_contacts') +
            safe_sum(data, 'meta_ads_contacts') +
            safe_sum(data, 'gmb_appels')
        )
        
        global_cpc = total_budget / total_contacts if total_contacts > 0 else 0
        
        # Affichage des métriques globales
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Budget Total", format_currency(total_budget))
        
        with col2:
            st.metric("Coût par Contact Global", format_currency(global_cpc)) 