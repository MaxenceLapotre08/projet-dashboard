import streamlit as st
from typing import List, Optional, Tuple
import pandas as pd
import numpy as np

def create_filters(data: pd.DataFrame) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Crée les filtres pour l'interface utilisateur.
    
    Args:
        data: DataFrame contenant les données
        
    Returns:
        Tuple contenant (client sélectionné, date de début, date de fin)
    """
    st.sidebar.title("Filtres")
    
    # Filtre par client
    # Suppression des valeurs NaN et conversion en liste
    clients = data['Client'].dropna().unique().tolist()
    clients = sorted(clients)  # Tri de la liste
    
    selected_client = st.sidebar.selectbox(
        "Sélectionner un client",
        ["Tous les clients"] + clients
    )
    selected_client = None if selected_client == "Tous les clients" else selected_client
    
    # Filtre par date
    if 'date' in data.columns:
        dates = pd.to_datetime(data['date'])
        min_date = dates.min()
        max_date = dates.max()
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Date de début",
                min_date,
                min_value=min_date,
                max_value=max_date
            )
        
        with col2:
            end_date = st.date_input(
                "Date de fin",
                max_date,
                min_value=min_date,
                max_value=max_date
            )
        
        # Validation des dates
        if start_date > end_date:
            st.sidebar.error("La date de début doit être antérieure à la date de fin")
            return None, None, None
        
        return selected_client, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    else:
        return selected_client, None, None 