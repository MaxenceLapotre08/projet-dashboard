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

# Tableau des clients avec leurs KPIs
st.header("👥 Tableau des Clients")

# Préparation des données pour le tableau
def prepare_client_data(df, canal_selectionne):
    client_data = []
    
    # Définition des colonnes par canal
    colonnes_par_canal = {
        'Site': [
            'Client', 'Activité', 'Localité',
            'Impressions Site', 'Visites Site', 'CTR Site', 'Taux Rebond Site',
            'Durée Moyenne Site', 'Position Moyenne Site', 'Appels Site', 'Formulaires Site',
            'Contacts Site', 'Coût Contact Site', 'Taux Conversion Site'
        ],
        'Google Ads': [
            'Client', 'Activité', 'Localité',
            'Budget Google', 'Impressions Google', 'Clics Google',
            'CTR Google', 'Taux Conv Google', 'Appels Google',
            'Formulaires Google', 'Contacts Google', 'Coût Contact Google',
            'Quality Score Google', 'Durée Moyenne Google', 'Taux Rebond Google'
        ],
        'Meta Ads': [
            'Client', 'Activité', 'Localité',
            'Budget Meta', 'Impressions Meta', 'Clics Meta',
            'CTR Meta', 'Taux Conv Meta', 'Appels Meta',
            'Formulaires Meta', 'Contacts Meta', 'Coût Contact Meta',
            'Relevance Score Meta', 'Durée Moyenne Meta', 'Taux Rebond Meta',
            'Taux Interaction Meta'
        ],
        'GMB': [
            'Client', 'Activité', 'Localité',
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
        colonnes_a_afficher = colonnes_par_canal[canal_selectionne]
    
    for _, row in df.iterrows():
        client = {
            'Client': row['Client'],
            'Activité': row['Activité'],
            'Localité': row['Localité'],
            # Site
            'Impressions Site': format_number(clean_numeric_value(row['site_impressions'])),
            'Visites Site': format_number(clean_numeric_value(row['site_visites'])),
            'CTR Site': format_percentage(clean_numeric_value(row['site_ctr']) * 100),
            'Taux Rebond Site': format_percentage(clean_numeric_value(row['site_taux_rebond']) * 100),
            'Durée Moyenne Site': f"{clean_numeric_value(row['site_duree_moyenne'])/60:.1f} min",
            'Position Moyenne Site': f"{clean_numeric_value(row['site_position_moyenne']):.1f}",
            'Appels Site': format_number(clean_numeric_value(row['site_nombre_appels'])),
            'Formulaires Site': format_number(clean_numeric_value(row['site_formulaires'])),
            'Contacts Site': format_number(clean_numeric_value(row['site_contacts'])),
            'Coût Contact Site': format_currency(clean_numeric_value(row['site_cout_contact'])),
            'Taux Conversion Site': format_percentage(clean_numeric_value(row['site_taux_conversion']) * 100),
            # Google Ads
            'Budget Google': format_currency(clean_numeric_value(row['google_budget'])),
            'Impressions Google': format_number(clean_numeric_value(row['google_impressions'])),
            'Clics Google': format_number(clean_numeric_value(row['google_clics'])),
            'CTR Google': format_percentage(clean_numeric_value(row['google_ctr']) * 100),
            'Taux Conv Google': format_percentage(clean_numeric_value(row['google_taux_conversion']) * 100),
            'Appels Google': format_number(clean_numeric_value(row['google_appels'])),
            'Formulaires Google': format_number(clean_numeric_value(row['google_formulaires'])),
            'Contacts Google': format_number(clean_numeric_value(row['google_contacts'])),
            'Coût Contact Google': format_currency(clean_numeric_value(row['google_cout_contact'])),
            'Quality Score Google': f"{clean_numeric_value(row['google_quality-score']):.1f}/10",
            'Durée Moyenne Google': f"{clean_numeric_value(row['google_durée_moyenne_visite'])/60:.1f} min",
            'Taux Rebond Google': format_percentage(clean_numeric_value(row['google_taux_de_rebond']) * 100),
            # Meta Ads
            'Budget Meta': format_currency(clean_numeric_value(row['meta_budget'])),
            'Impressions Meta': format_number(clean_numeric_value(row['meta_impressions'])),
            'Clics Meta': format_number(clean_numeric_value(row['meta_clics'])),
            'CTR Meta': format_percentage(clean_numeric_value(row['meta_ctr']) * 100),
            'Taux Conv Meta': format_percentage(clean_numeric_value(row['meta_taux_conversion']) * 100),
            'Appels Meta': format_number(clean_numeric_value(row['meta_appels'])),
            'Formulaires Meta': format_number(clean_numeric_value(row['meta_formulaires'])),
            'Contacts Meta': format_number(clean_numeric_value(row['meta_contacts'])),
            'Coût Contact Meta': format_currency(clean_numeric_value(row['meta_cout_contact'])),
            'Relevance Score Meta': f"{clean_numeric_value(row['meta_relevance_score']):.1f}/10",
            'Durée Moyenne Meta': f"{clean_numeric_value(row['meta_durée_moyenne_visite'])/60:.1f} min",
            'Taux Rebond Meta': format_percentage(clean_numeric_value(row['meta_taux_de_rebond']) * 100),
            'Taux Interaction Meta': format_percentage(clean_numeric_value(row['meta_taux_interaction']) * 100),
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
client_table = prepare_client_data(data_filtree, canal_selectionne)
st.dataframe(client_table, use_container_width=True)

# Si un client est sélectionné via la recherche, afficher un lien vers son dashboard
if client_search and len(data) == 1:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### Dashboard de {data.iloc[0]['Client']}")
    if st.sidebar.button("Voir le dashboard détaillé"):
        # Ici, vous pouvez ajouter la logique pour afficher le dashboard détaillé du client
        st.session_state['selected_client'] = data.iloc[0]['Client']
        st.experimental_rerun() 