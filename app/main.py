import streamlit as st
import pandas as pd
from utils.data_loader import DataLoader
from components.visualizations import (
    display_site_kpis,
    display_google_ads_kpis,
    display_meta_ads_kpis,
    display_gmb_kpis,
    display_canal_comparison,
    format_number,
    format_currency,
    format_percentage,
    clean_numeric_value
)
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Marketing",
    page_icon="📊",
    layout="wide"
)

# Titre de l'application
st.title("📊 Dashboard Marketing")

# Chargement des données
@st.cache_data
def load_data():
    loader = DataLoader()
    return loader.get_data()

data = load_data()

# Filtres
st.sidebar.header("Filtres")

# Filtre par date
dates_disponibles = sorted(data['date'].unique().tolist())
date_debut = st.sidebar.date_input(
    "Date de début",
    value=datetime.strptime(dates_disponibles[0], '%Y-%m').date(),
    min_value=datetime.strptime(dates_disponibles[0], '%Y-%m').date(),
    max_value=datetime.strptime(dates_disponibles[-1], '%Y-%m').date()
)
date_fin = st.sidebar.date_input(
    "Date de fin",
    value=datetime.strptime(dates_disponibles[-1], '%Y-%m').date(),
    min_value=datetime.strptime(dates_disponibles[0], '%Y-%m').date(),
    max_value=datetime.strptime(dates_disponibles[-1], '%Y-%m').date()
)

# Convertir les dates en format YYYY-MM
date_debut_str = date_debut.strftime('%Y-%m')
date_fin_str = date_fin.strftime('%Y-%m')

# Liste des clients pour l'autocomplétion
liste_clients = sorted(data['Client'].unique().tolist())

# Barre de recherche de client avec autocomplétion
client_search = st.sidebar.selectbox(
    "🔍 Rechercher un client",
    options=[""] + liste_clients,
    format_func=lambda x: x if x else "Tous les clients"
)

# Filtrage des données si un client est sélectionné
if client_search:
    data = data[data['Client'] == client_search]

# Filtre par activité
activites = ["Tous"] + sorted(data['Activité'].unique().tolist())
activite_selectionnee = st.sidebar.selectbox("Activité", activites)

# Filtre par localité
localites = ["Tous"] + sorted(data['Localité'].unique().tolist())
localite_selectionnee = st.sidebar.selectbox("Localité", localites)

# Filtre par canal
canaux = ["Tous", "Site", "Google Ads", "Meta Ads", "GMB"]
canal_selectionne = st.sidebar.selectbox("Canal", canaux)

# Application des filtres
data_filtree = data.copy()

# Filtre par date pour les KPIs
data_filtree = data_filtree[
    (data_filtree['date'] >= date_debut_str) & 
    (data_filtree['date'] <= date_fin_str)
]

if activite_selectionnee != "Tous":
    data_filtree = data_filtree[data_filtree['Activité'] == activite_selectionnee]
if localite_selectionnee != "Tous":
    data_filtree = data_filtree[data_filtree['Localité'] == localite_selectionnee]

# Affichage des KPIs par canal
if canal_selectionne in ["Tous", "Site"]:
    st.header("📱 Site Internet")
    display_site_kpis(data_filtree)

if canal_selectionne in ["Tous", "Google Ads"]:
    st.header("🔍 Google Ads")
    display_google_ads_kpis(data_filtree)

if canal_selectionne in ["Tous", "Meta Ads"]:
    st.header("📘 Meta Ads")
    display_meta_ads_kpis(data_filtree)

if canal_selectionne in ["Tous", "GMB"]:
    st.header("📍 Google My Business")
    display_gmb_kpis(data_filtree)

# Comparaison des canaux
if canal_selectionne == "Tous":
    st.header("📊 Comparaison des Canaux")
    metric = st.selectbox(
        "Sélectionnez une métrique à comparer",
        ["impressions", "clics", "ctr", "taux_conversion", "cout_contact", "appels", "formulaires", "contacts"]
    )
    display_canal_comparison(data_filtree, metric)

    # Graphique d'évolution des KPIs uniquement si un client est sélectionné
    if client_search:
        st.header("📈 Évolution des KPIs")
        
        # Sélection de plusieurs canaux pour le graphique d'évolution
        canaux_evolution = st.multiselect(
            "Sélectionnez un ou plusieurs canaux pour l'évolution",
            ["Site", "Google Ads", "Meta Ads", "GMB"],
            default=["Site"]
        )
        
        # Définition des KPIs disponibles par canal
        kpis_disponibles = {
            'Site': {
                'Impressions': 'site_impressions',
                'Visites': 'site_visites',
                'CTR': 'site_ctr',
                'Taux de Rebond': 'site_taux_rebond',
                'Durée Moyenne': 'site_duree_moyenne',
                'Position Moyenne': 'site_position_moyenne',
                'Appels': 'site_nombre_appels',
                'Formulaires': 'site_formulaires',
                'Contacts': 'site_contacts',
                'Coût Contact': 'site_cout_contact'
            },
            'Google Ads': {
                'Budget': 'google_ads_budget',
                'Impressions': 'google_ads_impressions',
                'Clics': 'google_ads_clics',
                'CTR': 'google_ads_ctr',
                'Taux de Conversion': 'google_ads_taux_conversion',
                'Appels': 'google_ads_appels',
                'Formulaires': 'google_ads_formulaires',
                'Contacts': 'google_ads_contacts',
                'Coût Contact': 'google_ads_cout_contact',
                'Quality Score': 'google_ads_quality_score'
            },
            'Meta Ads': {
                'Budget': 'meta_ads_budget',
                'Impressions': 'meta_ads_impressions',
                'Clics': 'meta_ads_clics',
                'CTR': 'meta_ads_ctr',
                'Taux de Conversion': 'meta_ads_taux_conversion',
                'Appels': 'meta_ads_appels',
                'Formulaires': 'meta_ads_formulaires',
                'Contacts': 'meta_ads_contacts',
                'Coût Contact': 'meta_ads_cout_contact',
                'Relevance Score': 'meta_ads_relevance_score'
            },
            'GMB': {
                'Vues': 'gmb_impressions',
                'Clics': 'gmb_clics_site',
                'Itinéraires': 'gmb_demande_d_itineraire',
                'Appels': 'gmb_appels',
                'Réservations': 'gmb_reservations',
                'Score': 'gmb_score_avis',
                'Nombre Avis': 'gmb_nombre_avis'
            }
        }
        
        # Sélection des KPIs à afficher (communs à tous les canaux sélectionnés)
        kpis_communs = set.intersection(*[set(kpis_disponibles[canal].keys()) for canal in canaux_evolution]) if canaux_evolution else set()
        kpis_selectionnes = st.multiselect(
            "Sélectionnez les KPIs à afficher",
            options=sorted(list(kpis_communs)),
            default=list(kpis_communs)[:3] if kpis_communs else []
        )
        
        if kpis_selectionnes and canaux_evolution:
            # Filtrer les données pour le client sélectionné et créer une copie explicite
            data_client = data[data['Client'] == client_search].loc[:].copy()
            # Nettoyer les données
            for col in data_client.columns:
                if col not in ['Client', 'Activité', 'Localité', 'date']:
                    data_client.loc[:, col] = pd.to_numeric(data_client[col], errors='coerce').fillna(0)
            # Créer le graphique
            fig = go.Figure()
            # Trier les données par date
            data_triee = data_client.sort_values('date')
            for canal in canaux_evolution:
                for kpi in kpis_selectionnes:
                    colonne = kpis_disponibles[canal][kpi]
                    if colonne in data_triee.columns:
                        if 'ctr' in colonne or 'taux' in colonne or 'score' in colonne:
                            valeurs = data_triee[colonne] * 100
                            suffixe = '%'
                        elif 'budget' in colonne or 'cout' in colonne:
                            valeurs = data_triee[colonne]
                            suffixe = '€'
                        elif 'duree' in colonne:
                            valeurs = data_triee[colonne] / 60
                            suffixe = ' min'
                        else:
                            valeurs = data_triee[colonne]
                            suffixe = ''
                        fig.add_trace(go.Scatter(
                            x=data_triee['date'],
                            y=valeurs,
                            name=f"{kpi} - {canal}{' ' + suffixe if suffixe else ''}",
                            mode='lines+markers'
                        ))
            fig.update_layout(
                title=f"Évolution des KPIs",
                xaxis_title="Date",
                yaxis_title="Valeur",
                hovermode='x unified',
                showlegend=True,
                height=600
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    else:
        st.info("Veuillez sélectionner un client pour afficher l'évolution des KPIs.")

# Tableau des clients avec leurs KPIs
st.header("👥 Tableau des Clients")

# Préparation des données pour le tableau
def prepare_client_data(df, canal_selectionne):
    # Filtrer les données par date
    df = df[(df['date'] >= date_debut_str) & (df['date'] <= date_fin_str)]
    
    # Nettoyer les données
    for col in df.columns:
        if col not in ['Client', 'Activité', 'Localité', 'date']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Si un client est sélectionné, ne pas agréger les données
    if client_search:
        df_agg = df
    else:
        # Agréger les données par client
        df_agg = df.groupby(['Client', 'Activité', 'Localité']).agg({
            # Site
            'site_impressions': 'sum',
            'site_visites': 'sum',
            'site_ctr': 'mean',
            'site_taux_rebond': 'mean',
            'site_duree_moyenne': 'mean',
            'site_position_moyenne': 'mean',
            'site_nombre_appels': 'sum',
            'site_formulaires': 'sum',
            'site_cout_contact': 'mean',
            # Google Ads
            'google_ads_budget': 'sum',
            'google_ads_impressions': 'sum',
            'google_ads_clics': 'sum',
            'google_ads_ctr': 'mean',
            'google_ads_taux_conversion': 'mean',
            'google_ads_appels': 'sum',
            'google_ads_formulaires': 'sum',
            'google_ads_contacts': 'sum',
            'google_ads_cout_contact': 'mean',
            'google_ads_quality_score': 'mean',
            'google_ads_durée_moyenne_visite': 'mean',
            'google_ads_taux_de_rebond': 'mean',
            # Meta Ads
            'meta_ads_budget': 'sum',
            'meta_ads_impressions': 'sum',
            'meta_ads_clics': 'sum',
            'meta_ads_ctr': 'mean',
            'meta_ads_taux_conversion': 'mean',
            'meta_ads_appels': 'sum',
            'meta_ads_formulaires': 'sum',
            'meta_ads_contacts': 'sum',
            'meta_ads_cout_contact': 'mean',
            'meta_ads_relevance_score': 'mean',
            'meta_ads_durée_moyenne_visite': 'mean',
            'meta_ads_taux_de_rebond': 'mean',
            'meta_ads_taux_interaction': 'mean',
            # GMB
            'gmb_impressions': 'sum',
            'gmb_clics_site': 'sum',
            'gmb_demande_d_itineraire': 'sum',
            'gmb_appels': 'sum',
            'gmb_reservations': 'sum',
            'gmb_score_avis': 'mean',
            'gmb_nombre_avis': 'sum',
            'gmb_taux_d_interaction': 'mean',
            'gmb_taux_d_appel': 'mean',
            'gmb_taux_de_reservation': 'mean',
            'gmb_vues_meta_adsps_mobile': 'sum',
            'gmb_vues_meta_adsps_desktop': 'sum',
            'gmb_vues_recherche_google_mobile': 'sum',
            'gmb_vues_recherche_google_desktop': 'sum'
        }).reset_index()
    
    # Remplacer les valeurs NaN par 0
    df_agg = df_agg.fillna(0)
    
    client_data = []
    
    # Définition des colonnes par canal
    colonnes_par_canal = {
        'Site': [
            'Client', 'Activité', 'Localité', 'date' if client_search else None,
            'Impressions Site', 'Visites Site', 'CTR Site', 'Taux Rebond Site',
            'Durée Moyenne Site', 'Position Moyenne Site', 'Appels Site', 'Formulaires Site',
            'Contacts Site', 'Coût Contact Site', 'Taux Conversion Site'
        ],
        'Google Ads': [
            'Client', 'Activité', 'Localité', 'date' if client_search else None,
            'Budget Google', 'Impressions Google', 'Clics Google',
            'CTR Google', 'Taux Conv Google', 'Appels Google',
            'Formulaires Google', 'Contacts Google', 'Coût Contact Google',
            'Quality Score Google', 'Durée Moyenne Google', 'Taux Rebond Google'
        ],
        'Meta Ads': [
            'Client', 'Activité', 'Localité', 'date' if client_search else None,
            'Budget Meta', 'Impressions Meta', 'Clics Meta',
            'CTR Meta', 'Taux Conv Meta', 'Appels Meta',
            'Formulaires Meta', 'Contacts Meta', 'Coût Contact Meta',
            'Relevance Score Meta', 'Durée Moyenne Meta', 'Taux Rebond Meta',
            'Taux Interaction Meta'
        ],
        'GMB': [
            'Client', 'Activité', 'Localité', 'date' if client_search else None,
            'Vues GMB', 'Clics GMB', 'Itinéraires GMB',
            'Appels GMB', 'Réservations GMB', 'Score GMB',
            'Nombre Avis GMB', 'Taux Interaction GMB', 'Taux Appel GMB',
            'Taux Réservation GMB', 'Vues Meta Mobile', 'Vues Meta Desktop',
            'Vues Google Mobile', 'Vues Google Desktop'
        ]
    }
    
    # Sélection des colonnes à afficher
    if canal_selectionne == "Tous":
        colonnes_a_afficher = None  # Afficher toutes les colonnes
    else:
        colonnes_a_afficher = [col for col in colonnes_par_canal[canal_selectionne] if col is not None]
    
    for _, row in df_agg.iterrows():
        # Convertir la date en format lettré si un client est sélectionné
        if client_search:
            date_obj = datetime.strptime(row['date'], '%Y-%m')
            date_formatted = date_obj.strftime('%B %Y').capitalize()
        
        # Calculer le taux de conversion pour le site
        total_contacts = clean_numeric_value(row['site_nombre_appels']) + clean_numeric_value(row['site_formulaires'])
        total_visits = clean_numeric_value(row['site_visites'])
        taux_conversion = (total_contacts / total_visits * 100) if total_visits > 0 else 0
        
        # Calculer le CTR site
        impressions = clean_numeric_value(row['site_impressions'])
        clics = clean_numeric_value(row['site_visites'])
        ctr_site = (clics / impressions * 100) if impressions > 0 else 0
        
        client = {
            'Client': row['Client'],
            'Activité': row['Activité'],
            'Localité': row['Localité'],
            'date': date_formatted if client_search else None,
            # Site
            'Impressions Site': format_number(impressions),
            'Visites Site': format_number(clics),
            'CTR Site': format_percentage(ctr_site),
            'Taux Rebond Site': format_percentage(clean_numeric_value(row['site_taux_rebond']) * 100),
            'Durée Moyenne Site': f"{clean_numeric_value(row['site_duree_moyenne'])/60:.1f} min",
            'Position Moyenne Site': f"{clean_numeric_value(row['site_position_moyenne']):.1f}",
            'Appels Site': format_number(clean_numeric_value(row['site_nombre_appels'])),
            'Formulaires Site': format_number(clean_numeric_value(row['site_formulaires'])),
            'Contacts Site': format_number(total_contacts),
            'Coût Contact Site': format_currency(clean_numeric_value(row['site_cout_contact'])),
            'Taux Conversion Site': format_percentage(taux_conversion),
            # Google Ads
            'Budget Google': format_currency(clean_numeric_value(row['google_ads_budget'])),
            'Impressions Google': format_number(clean_numeric_value(row['google_ads_impressions'])),
            'Clics Google': format_number(clean_numeric_value(row['google_ads_clics'])),
            'CTR Google': format_percentage(clean_numeric_value(row['google_ads_ctr']) * 100),
            'Taux Conv Google': format_percentage(clean_numeric_value(row['google_ads_taux_conversion']) * 100),
            'Appels Google': format_number(clean_numeric_value(row['google_ads_appels'])),
            'Formulaires Google': format_number(clean_numeric_value(row['google_ads_formulaires'])),
            'Contacts Google': format_number(clean_numeric_value(row['google_ads_contacts'])),
            'Coût Contact Google': format_currency(clean_numeric_value(row['google_ads_cout_contact'])),
            'Quality Score Google': f"{clean_numeric_value(row['google_ads_quality_score']):.1f}/100",
            'Durée Moyenne Google': f"{clean_numeric_value(row['google_ads_durée_moyenne_visite'])/60:.1f} min",
            'Taux Rebond Google': format_percentage(clean_numeric_value(row['google_ads_taux_de_rebond']) * 100),
            # Meta Ads
            'Budget Meta': format_currency(clean_numeric_value(row['meta_ads_budget'])),
            'Impressions Meta': format_number(clean_numeric_value(row['meta_ads_impressions'])),
            'Clics Meta': format_number(clean_numeric_value(row['meta_ads_clics'])),
            'CTR Meta': format_percentage(clean_numeric_value(row['meta_ads_ctr']) * 100),
            'Taux Conv Meta': format_percentage(clean_numeric_value(row['meta_ads_taux_conversion']) * 100),
            'Appels Meta': format_number(clean_numeric_value(row['meta_ads_appels'])),
            'Formulaires Meta': format_number(clean_numeric_value(row['meta_ads_formulaires'])),
            'Contacts Meta': format_number(clean_numeric_value(row['meta_ads_contacts'])),
            'Coût Contact Meta': format_currency(clean_numeric_value(row['meta_ads_cout_contact'])),
            'Relevance Score Meta': f"{clean_numeric_value(row['meta_ads_relevance_score']):.1f}/10",
            'Durée Moyenne Meta': f"{clean_numeric_value(row['meta_ads_durée_moyenne_visite'])/60:.1f} min",
            'Taux Rebond Meta': format_percentage(clean_numeric_value(row['meta_ads_taux_de_rebond']) * 100),
            'Taux Interaction Meta': format_percentage(clean_numeric_value(row['meta_ads_taux_interaction']) * 100),
            # GMB
            'Vues GMB': format_number(clean_numeric_value(row['gmb_impressions'])),
            'Clics GMB': format_number(clean_numeric_value(row['gmb_clics_site'])),
            'Itinéraires GMB': format_number(clean_numeric_value(row['gmb_demande_d_itineraire'])),
            'Appels GMB': format_number(clean_numeric_value(row['gmb_appels'])),
            'Réservations GMB': format_number(clean_numeric_value(row['gmb_reservations'])),
            'Score GMB': f"{clean_numeric_value(row['gmb_score_avis']):.1f}/5",
            'Nombre Avis GMB': format_number(clean_numeric_value(row['gmb_nombre_avis'])),
            'Taux Interaction GMB': format_percentage(clean_numeric_value(row['gmb_taux_d_interaction']) * 100),
            'Taux Appel GMB': format_percentage(clean_numeric_value(row['gmb_taux_d_appel']) * 100),
            'Taux Réservation GMB': format_percentage(clean_numeric_value(row['gmb_taux_de_reservation']) * 100),
            'Vues Meta Mobile': format_number(clean_numeric_value(row['gmb_vues_meta_adsps_mobile'])),
            'Vues Meta Desktop': format_number(clean_numeric_value(row['gmb_vues_meta_adsps_desktop'])),
            'Vues Google Mobile': format_number(clean_numeric_value(row['gmb_vues_recherche_google_mobile'])),
            'Vues Google Desktop': format_number(clean_numeric_value(row['gmb_vues_recherche_google_desktop']))
        }
        client_data.append(client)
    
    df_result = pd.DataFrame(client_data)
    if colonnes_a_afficher:
        df_result = df_result[colonnes_a_afficher]
    return df_result

# Affichage du tableau
client_table = prepare_client_data(data, canal_selectionne)
st.dataframe(client_table, use_container_width=True) 