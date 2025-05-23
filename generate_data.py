import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def clean_numeric_string(value):
    """Nettoie une chaîne de caractères pour la convertir en nombre."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    
    # Remplace les caractères spéciaux
    value = str(value).replace('€', '').replace('%', '')
    value = value.replace('\u202f', '').replace(' ', '')  # Supprime les espaces insécables
    value = value.replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return np.nan

# Lecture du fichier original
df_original = pd.read_csv('data/data.csv')

# Création d'une liste de dates pour les 12 derniers mois
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
dates = pd.date_range(start=start_date, end=end_date, freq='ME')

# Création d'un nouveau DataFrame pour stocker les données mensuelles
df_monthly = pd.DataFrame()

# Pour chaque client dans le fichier original
for _, row in df_original.iterrows():
    client = row['Client']
    
    # Pour chaque mois
    for date in dates:
        # Création d'une nouvelle ligne avec des variations aléatoires
        new_row = row.copy()
        new_row['date'] = date.strftime('%Y-%m')
        
        # Application de variations aléatoires pour les colonnes numériques
        for col in df_original.columns:
            if col != 'Client' and col != 'date':
                if pd.notna(row[col]):
                    # Variation de ±20% pour les valeurs numériques
                    variation = random.uniform(0.8, 1.2)
                    original_value = clean_numeric_string(row[col])
                    
                    if not pd.isna(original_value):
                        if '€' in str(row[col]):
                            new_row[col] = f"{original_value * variation:.2f}€"
                        elif '%' in str(row[col]):
                            new_row[col] = f"{min(original_value * variation, 100):.2f}%"
                        else:
                            new_row[col] = original_value * variation
        
        df_monthly = pd.concat([df_monthly, pd.DataFrame([new_row])], ignore_index=True)

# Sauvegarde du nouveau fichier CSV
df_monthly.to_csv('data/data_with_dates.csv', index=False)
print("Fichier data_with_dates.csv créé avec succès!") 