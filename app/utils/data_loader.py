import pandas as pd
import numpy as np
import logging
from typing import List, Optional, Union
import json
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.json_path = Path("data/data.json")
        self.csv_path = Path("data/data.csv")
        self._data = None

    def _load_csv_data(self):
        """Charge les données depuis le fichier CSV."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Le fichier {self.csv_path} n'existe pas")
        
        df = pd.read_csv(self.csv_path)
        
        # Créer un DataFrame pour chaque mois des 12 derniers mois
        dfs = []
        today = datetime.now()
        for i in range(12):
            date = (today - relativedelta(months=i)).strftime('%Y-%m')
            df_copy = df.copy()
            df_copy['date'] = date
            dfs.append(df_copy)
        
        # Concaténer tous les DataFrames
        return pd.concat(dfs, ignore_index=True)

    def _create_json_from_csv(self, df):
        """Crée le fichier JSON à partir des données CSV."""
        clients = {}
        
        # Grouper les données par client
        for _, row in df.iterrows():
            client_id = row['Client'].lower().replace(' ', '_')
            if client_id not in clients:
                clients[client_id] = {
                    'id': client_id,
                    'nom': row['Client'],
                    'activite': row['Activité'],
                    'localite': row['Localité'],
                    'historique': []
                }
            
            # Créer l'entrée historique
            historique = {
                'date': row['date']
            }
            
            # Ajouter les données du site
            site_data = {}
            for col in df.columns:
                if col.startswith('site_'):
                    site_data[col.replace('site_', '')] = row[col]
            historique['site'] = site_data
            
            # Ajouter les données Google Ads
            google_data = {}
            for col in df.columns:
                if col.startswith('google_'):
                    google_data[col.replace('google_', '')] = row[col]
            historique['google_ads'] = google_data
            
            # Ajouter les données Meta Ads
            meta_data = {}
            for col in df.columns:
                if col.startswith('meta_'):
                    meta_data[col.replace('meta_', '')] = row[col]
            historique['meta_ads'] = meta_data
            
            # Ajouter les données GMB
            gmb_data = {}
            for col in df.columns:
                if col.startswith('gmb_'):
                    gmb_data[col.replace('gmb_', '')] = row[col]
            historique['gmb'] = gmb_data
            
            clients[client_id]['historique'].append(historique)
        
        # Sauvegarder le JSON
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump({'clients': list(clients.values())}, f, ensure_ascii=False, indent=2)

    def get_data(self):
        """Récupère les données sous forme de DataFrame."""
        if self._data is None:
            # Charger les données CSV
            csv_df = self._load_csv_data()
            
            # Créer le JSON à partir des données CSV
            self._create_json_from_csv(csv_df)
            
            self._data = csv_df
        return self._data

    def get_clients(self):
        """Récupère la liste des clients."""
        if self._data is None:
            self._data = self._load_csv_data()
        return self._data['Client'].unique().tolist()

    def get_activities(self):
        """Récupère la liste des activités."""
        if self._data is None:
            self._data = self._load_csv_data()
        return self._data['Activité'].unique().tolist()

    def get_localities(self):
        """Récupère la liste des localités."""
        if self._data is None:
            self._data = self._load_csv_data()
        return self._data['Localité'].unique().tolist()

    def get_unique_values(self, column: str) -> List[str]:
        """Retourne les valeurs uniques d'une colonne."""
        if self._data is None:
            self._data = self._load_csv_data()
        
        if column not in self._data.columns:
            raise ValueError(f"La colonne {column} n'existe pas")
        
        return sorted(self._data[column].unique().tolist())
    
    def get_metric_summary(self, metric: str, client: Optional[str] = None) -> dict:
        """Retourne un résumé des statistiques pour une métrique donnée."""
        if self._data is None:
            self._data = self._load_csv_data()
        
        data = self.get_data()
        
        if metric not in data.columns:
            raise ValueError(f"La métrique {metric} n'existe pas")
        
        return {
            'total': data[metric].sum(),
            'moyenne': data[metric].mean(),
            'min': data[metric].min(),
            'max': data[metric].max(),
            'ecart_type': data[metric].std()
        } 