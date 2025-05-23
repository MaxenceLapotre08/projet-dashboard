import pandas as pd
import numpy as np
import logging
from typing import List, Optional, Union

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, file_path: str = "data/data_cleaned.csv"):
        """Initialise le DataLoader avec le chemin du fichier CSV."""
        self.file_path = file_path
        self.data = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Charge les données depuis le fichier CSV."""
        try:
            self.data = pd.read_csv(self.file_path)
            logger.info(f"Données chargées avec succès : {len(self.data)} lignes")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données : {str(e)}")
            raise
    
    def get_data(self, client: Optional[str] = None) -> pd.DataFrame:
        """Retourne les données, filtrées par client si spécifié."""
        if self.data is None:
            raise ValueError("Aucune donnée n'a été chargée")
        
        if client:
            return self.data[self.data['client'] == client]
        return self.data
    
    def get_unique_values(self, column: str) -> List[str]:
        """Retourne les valeurs uniques d'une colonne."""
        if self.data is None:
            raise ValueError("Aucune donnée n'a été chargée")
        
        if column not in self.data.columns:
            raise ValueError(f"La colonne {column} n'existe pas")
        
        return sorted(self.data[column].unique().tolist())
    
    def get_metric_summary(self, metric: str, client: Optional[str] = None) -> dict:
        """Retourne un résumé des statistiques pour une métrique donnée."""
        if self.data is None:
            raise ValueError("Aucune donnée n'a été chargée")
        
        data = self.get_data(client)
        
        if metric not in data.columns:
            raise ValueError(f"La métrique {metric} n'existe pas")
        
        return {
            'total': data[metric].sum(),
            'moyenne': data[metric].mean(),
            'min': data[metric].min(),
            'max': data[metric].max(),
            'ecart_type': data[metric].std()
        } 