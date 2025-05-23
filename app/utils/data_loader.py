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
        self._data = None

    def _load_json_data(self):
        """Charge les données depuis le fichier JSON."""
        if not self.json_path.exists():
            raise FileNotFoundError(f"Le fichier {self.json_path} n'existe pas")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        # Convertir en DataFrame à plat
        rows = []
        for client in json_data['clients']:
            for hist in client['historique']:
                row = {
                    'Client': client['nom'],
                    'Activité': client['activite'],
                    'Localité': client['localite'],
                    'date': hist['date']
                }
                # Ajout des sous-dictionnaires (site, google_ads, meta_ads, gmb)
                for canal in ['site', 'google_ads', 'meta_ads', 'gmb']:
                    if canal in hist:
                        for k, v in hist[canal].items():
                            row[f"{canal}_{k}"] = v
                rows.append(row)
        return pd.DataFrame(rows)

    def get_data(self):
        """Récupère les données sous forme de DataFrame."""
        if self._data is None:
            self._data = self._load_json_data()
        return self._data

    def get_clients(self):
        if self._data is None:
            self._data = self._load_json_data()
        return self._data['Client'].unique().tolist()

    def get_activities(self):
        if self._data is None:
            self._data = self._load_json_data()
        return self._data['Activité'].unique().tolist()

    def get_localities(self):
        if self._data is None:
            self._data = self._load_json_data()
        return self._data['Localité'].unique().tolist()

    def get_unique_values(self, column: str) -> List[str]:
        if self._data is None:
            self._data = self._load_json_data()
        if column not in self._data.columns:
            raise ValueError(f"La colonne {column} n'existe pas")
        return sorted(self._data[column].unique().tolist())
    
    def get_metric_summary(self, metric: str, client: Optional[str] = None) -> dict:
        if self._data is None:
            self._data = self._load_json_data()
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