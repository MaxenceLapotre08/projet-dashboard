import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

# Chargement des variables d'environnement
load_dotenv()

class AIAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def analyze_data(self, data: pd.DataFrame, query: str) -> str:
        """
        Analyse les données avec ChatGPT en fonction de la requête de l'utilisateur.
        
        Args:
            data (pd.DataFrame): Les données à analyser
            query (str): La requête de l'utilisateur
            
        Returns:
            str: L'analyse générée par ChatGPT
        """
        # Préparation des données pour l'analyse
        data_summary = self._prepare_data_summary(data)
        
        # Construction du prompt
        prompt = f"""
        En tant qu'expert en analyse de données marketing, analysez les données suivantes et répondez à cette question : {query}
        
        Données à analyser :
        {data_summary}
        
        Instructions pour la réponse :
        1. Soyez concis et direct
        2. Structurez votre réponse en points clés
        3. Utilisez des chiffres précis
        4. Limitez votre réponse à 3-4 points maximum
        5. Évitez les phrases d'introduction et de conclusion
        6. Allez droit au but
        """
        
        try:
            # Appel à l'API ChatGPT
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en analyse de données marketing. Vos réponses sont concises, directes et basées sur les données."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Réduire la température pour des réponses plus précises
                max_tokens=500    # Réduire le nombre maximum de tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Erreur lors de l'analyse : {str(e)}"
    
    def _prepare_data_summary(self, data: pd.DataFrame) -> str:
        """
        Prépare un résumé des données pour l'analyse.
        
        Args:
            data (pd.DataFrame): Les données à résumer
            
        Returns:
            str: Résumé des données
        """
        summary = []
        
        # Période d'analyse
        dates = sorted(data['date'].unique())
        summary.append(f"Période d'analyse : de {dates[0]} à {dates[-1]}")
        
        # Statistiques globales
        summary.append("\nStatistiques globales :")
        summary.append(f"- Nombre total de clients : {data['Client'].nunique()}")
        summary.append(f"- Nombre total d'activités : {data['Activité'].nunique()}")
        summary.append(f"- Nombre total de localités : {data['Localité'].nunique()}")
        
        # Statistiques par activité
        summary.append("\nStatistiques détaillées par activité :")
        for activite in sorted(data['Activité'].unique()):
            data_activite = data[data['Activité'] == activite]
            total_contacts = (data_activite['site_contacts'].sum() + 
                            data_activite['google_ads_contacts'].sum() + 
                            data_activite['meta_ads_contacts'].sum() + 
                            data_activite['gmb_appels'].sum() + 
                            data_activite['gmb_reservations'].sum())
            total_budget = (data_activite['google_ads_budget'].sum() + 
                          data_activite['meta_ads_budget'].sum() + 
                          (99 * len(data_activite['date'].unique())))
            
            summary.append(f"\n{activite} :")
            summary.append(f"- Nombre de clients : {data_activite['Client'].nunique()}")
            summary.append(f"- Localités couvertes : {', '.join(sorted(data_activite['Localité'].unique()))}")
            summary.append(f"- Contacts totaux : {total_contacts:,.0f}")
            summary.append(f"- Budget total : {total_budget:,.2f}€")
            summary.append(f"- Coût par contact : {(total_budget / total_contacts if total_contacts > 0 else 0):.2f}€")
            
            # Détail par canal pour cette activité
            summary.append("  Détail par canal :")
            # Site
            site_contacts = data_activite['site_contacts'].sum()
            site_cpc = data_activite['site_cout_contact'].mean()
            summary.append(f"  - Site : {site_contacts:,.0f} contacts, coût moyen : {site_cpc:.2f}€")
            # Google Ads
            ga_contacts = data_activite['google_ads_contacts'].sum()
            ga_budget = data_activite['google_ads_budget'].sum()
            ga_cpc = ga_budget / ga_contacts if ga_contacts > 0 else 0
            summary.append(f"  - Google Ads : {ga_contacts:,.0f} contacts, budget : {ga_budget:,.2f}€, coût par contact : {ga_cpc:.2f}€")
            # Meta Ads
            ma_contacts = data_activite['meta_ads_contacts'].sum()
            ma_budget = data_activite['meta_ads_budget'].sum()
            ma_cpc = ma_budget / ma_contacts if ma_contacts > 0 else 0
            summary.append(f"  - Meta Ads : {ma_contacts:,.0f} contacts, budget : {ma_budget:,.2f}€, coût par contact : {ma_cpc:.2f}€")
            # GMB
            gmb_contacts = data_activite['gmb_appels'].sum() + data_activite['gmb_reservations'].sum()
            gmb_budget = 99 * len(data_activite['date'].unique())
            gmb_cpc = gmb_budget / gmb_contacts if gmb_contacts > 0 else 0
            summary.append(f"  - GMB : {gmb_contacts:,.0f} contacts, budget : {gmb_budget:,.2f}€, coût par contact : {gmb_cpc:.2f}€")
        
        # Statistiques par localité
        summary.append("\nStatistiques par localité :")
        for localite in sorted(data['Localité'].unique()):
            data_localite = data[data['Localité'] == localite]
            total_contacts = (data_localite['site_contacts'].sum() + 
                            data_localite['google_ads_contacts'].sum() + 
                            data_localite['meta_ads_contacts'].sum() + 
                            data_localite['gmb_appels'].sum() + 
                            data_localite['gmb_reservations'].sum())
            total_budget = (data_localite['google_ads_budget'].sum() + 
                          data_localite['meta_ads_budget'].sum() + 
                          (99 * len(data_localite['date'].unique())))
            
            summary.append(f"\n{localite} :")
            summary.append(f"- Nombre de clients : {data_localite['Client'].nunique()}")
            summary.append(f"- Activités présentes : {', '.join(sorted(data_localite['Activité'].unique()))}")
            summary.append(f"- Contacts totaux : {total_contacts:,.0f}")
            summary.append(f"- Budget total : {total_budget:,.2f}€")
            summary.append(f"- Coût par contact : {(total_budget / total_contacts if total_contacts > 0 else 0):.2f}€")
        
        # Statistiques par client
        summary.append("\nTop 5 clients par nombre de contacts :")
        client_stats = []
        for client in data['Client'].unique():
            data_client = data[data['Client'] == client]
            total_contacts = (data_client['site_contacts'].sum() + 
                            data_client['google_ads_contacts'].sum() + 
                            data_client['meta_ads_contacts'].sum() + 
                            data_client['gmb_appels'].sum() + 
                            data_client['gmb_reservations'].sum())
            total_budget = (data_client['google_ads_budget'].sum() + 
                          data_client['meta_ads_budget'].sum() + 
                          (99 * len(data_client['date'].unique())))
            client_stats.append({
                'client': client,
                'contacts': total_contacts,
                'budget': total_budget,
                'cpc': total_budget / total_contacts if total_contacts > 0 else 0
            })
        
        # Trier les clients par nombre de contacts
        client_stats.sort(key=lambda x: x['contacts'], reverse=True)
        for i, stat in enumerate(client_stats[:5], 1):
            summary.append(f"\n{i}. {stat['client']} :")
            summary.append(f"   - Contacts : {stat['contacts']:,.0f}")
            summary.append(f"   - Budget : {stat['budget']:,.2f}€")
            summary.append(f"   - Coût par contact : {stat['cpc']:.2f}€")
        
        return "\n".join(summary) 