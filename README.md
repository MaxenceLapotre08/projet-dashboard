# Dashboard Marketing

Un dashboard interactif pour suivre les performances marketing de vos clients.

## Fonctionnalités

- Visualisation des KPIs par canal (Site, Google Ads, Meta Ads, GMB)
- Filtrage par client, activité et localité
- Comparaison des canaux
- Historique des performances par client
- Interface intuitive et responsive

## Installation

1. Cloner le repository :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_PROJET]
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
# ou
venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Structure du projet

```
.
├── app/
│   ├── main.py              # Dashboard principal
│   ├── pages/              # Pages additionnelles
│   │   └── client_dashboard.py
│   ├── components/         # Composants réutilisables
│   │   └── visualizations.py
│   └── utils/             # Utilitaires
│       └── data_loader.py
├── data/                  # Données (non versionné)
├── requirements.txt       # Dépendances
└── README.md             # Documentation
```

## Utilisation

1. Lancer l'application :
```bash
streamlit run app/main.py
```

2. Accéder au dashboard dans votre navigateur :
```
http://localhost:8501
```

## Configuration

1. Placer votre fichier Excel de données dans le dossier `data/`
2. Le fichier doit contenir une colonne `date` au format "YYYY-MM-DD" ou "YYYY-MM"
3. Les colonnes doivent suivre la nomenclature définie dans le code

## Dépendances

- Python 3.8+
- Streamlit
- Pandas
- Autres dépendances listées dans `requirements.txt`

## Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

[Votre licence ici] 