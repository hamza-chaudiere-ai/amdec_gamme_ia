#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'entraînement et d'apprentissage sur les datasets AMDEC et Gammes
"""

import pandas as pd
import numpy as np
import os
import logging
import joblib
from typing import Dict, List, Optional, Tuple, Any
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import warnings
warnings.filterwarnings('ignore')

from .utils import (
    normalize_component_name,
    normalize_subcomponent_name,
    ComponentConfig
)

logger = logging.getLogger(__name__)

class DataTrainer:
    """
    Classe pour l'entraînement de modèles ML sur les datasets AMDEC et Gammes
    """
    
    def __init__(self):
        """Initialise le module d'entraînement"""
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.datasets = {}
        
        # Répertoires
        self.data_dir = 'data/dataset'
        self.models_dir = 'ml/saved_models'
        
        # Créer les répertoires nécessaires
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Charger les datasets existants
        self._load_datasets()
    
    def _load_datasets(self):
        """Charge les datasets disponibles"""
        try:
        
            # Dataset AMDEC
            amdec_path = os.path.join(self.data_dir, 'amdec_dataset.xlsx')
            if os.path.exists(amdec_path):
                self.datasets['amdec'] = pd.read_excel(amdec_path, engine='openpyxl')
                self.datasets['amdec'] = pd.read_excel(amdec_path)
                logger.info(f"Dataset AMDEC chargé: {len(self.datasets['amdec'])} entrées")
            else:
                logger.warning(f"Dataset AMDEC non trouvé: {amdec_path}")
                self.datasets['amdec'] = self._create_default_amdec_dataset()
            
            # Dataset Gammes
            gamme_path = os.path.join(self.data_dir, 'gamme_dataset.xlsx')
            if os.path.exists(gamme_path):
                self.datasets['gamme'] = pd.read_excel(gamme_path, engine='openpyxl')
                self.datasets['gamme'] = pd.read_excel(gamme_path)
                logger.info(f"Dataset Gammes chargé: {len(self.datasets['gamme'])} entrées")
            else:
                logger.warning(f"Dataset Gammes non trouvé: {gamme_path}")
                self.datasets['gamme'] = self._create_default_gamme_dataset()
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des datasets: {e}")
            # Créer des datasets par défaut
            self.datasets['amdec'] = self._create_default_amdec_dataset()
            self.datasets['gamme'] = self._create_default_gamme_dataset()
    
    def _create_default_amdec_dataset(self) -> pd.DataFrame:
        """Crée un dataset AMDEC par défaut basé sur l'expertise"""
        data = []
        
        # Données basées sur les modèles existants et l'expertise
        amdec_knowledge = {
            'economiseur_bt': {
                'epingle': [
                    {'cause': 'corrosion', 'f': 3, 'g': 4, 'd': 2, 'mode': 'Corrosion externe'},
                    {'cause': 'erosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Érosion par cendres'},
                    {'cause': 'encrassement', 'f': 4, 'g': 2, 'd': 1, 'mode': 'Encrassement interne'}
                ],
                'collecteur_sortie': [
                    {'cause': 'corrosion', 'f': 3, 'g': 5, 'd': 3, 'mode': 'Caustic attack'},
                    {'cause': 'fissure', 'f': 2, 'g': 4, 'd': 3, 'mode': 'Fissuration contrainte'},
                    {'cause': 'fatigue', 'f': 2, 'g': 4, 'd': 3, 'mode': 'Fatigue thermique'}
                ]
            },
            'economiseur_ht': {
                'collecteur_entree': [
                    {'cause': 'erosion', 'f': 3, 'g': 3, 'd': 2, 'mode': 'Érosion par cendres'},
                    {'cause': 'corrosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Corrosion externe'},
                    {'cause': 'surchauffe', 'f': 2, 'g': 4, 'd': 1, 'mode': 'Déformation thermique'}
                ],
                'tubes_suspension': [
                    {'cause': 'fatigue', 'f': 2, 'g': 3, 'd': 3, 'mode': 'Fatigue mécanique'},
                    {'cause': 'vibration', 'f': 3, 'g': 2, 'd': 1, 'mode': 'Vibration excessive'},
                    {'cause': 'corrosion', 'f': 2, 'g': 2, 'd': 2, 'mode': 'Corrosion supports'}
                ]
            },
            'surchauffeur_bt': {
                'epingle': [
                    {'cause': 'surchauffe', 'f': 2, 'g': 5, 'd': 1, 'mode': 'Short-term overheat'},
                    {'cause': 'corrosion', 'f': 3, 'g': 4, 'd': 2, 'mode': 'Corrosion côté feu'},
                    {'cause': 'fatigue', 'f': 2, 'g': 4, 'd': 3, 'mode': 'Fatigue thermique'}
                ],
                'collecteur_entree': [
                    {'cause': 'corrosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Corrosion interne'},
                    {'cause': 'erosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Érosion interne'},
                    {'cause': 'fissure', 'f': 1, 'g': 4, 'd': 3, 'mode': 'Fissuration'}
                ]
            },
            'surchauffeur_ht': {
                'tube_porteur': [
                    {'cause': 'surchauffe', 'f': 2, 'g': 5, 'd': 2, 'mode': 'Long-term overheat'},
                    {'cause': 'fatigue', 'f': 2, 'g': 4, 'd': 3, 'mode': 'Rupture fluage'},
                    {'cause': 'corrosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Corrosion haute température'}
                ],
                'branches_entree': [
                    {'cause': 'corrosion', 'f': 3, 'g': 3, 'd': 2, 'mode': 'Fireside corrosion'},
                    {'cause': 'fatigue', 'f': 2, 'g': 3, 'd': 3, 'mode': 'Fatigue thermique'},
                    {'cause': 'erosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Érosion externe'}
                ],
                'collecteur_sortie': [
                    {'cause': 'fissure', 'f': 2, 'g': 4, 'd': 3, 'mode': 'SCC (Stress Corrosion Cracking)'},
                    {'cause': 'fatigue', 'f': 2, 'g': 4, 'd': 3, 'mode': 'Fatigue contrainte'},
                    {'cause': 'corrosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Corrosion interfaces'}
                ]
            },
            'rechauffeur_bt': {
                'collecteur_entree': [
                    {'cause': 'corrosion', 'f': 2, 'g': 4, 'd': 3, 'mode': 'Hydrogen damage'},
                    {'cause': 'fissure', 'f': 2, 'g': 3, 'd': 3, 'mode': 'Microfissures'},
                    {'cause': 'encrassement', 'f': 3, 'g': 2, 'd': 2, 'mode': 'Dépôts internes'}
                ],
                'tubes_suspension': [
                    {'cause': 'fatigue', 'f': 3, 'g': 3, 'd': 3, 'mode': 'Fatigue thermique'},
                    {'cause': 'vibration', 'f': 3, 'g': 2, 'd': 1, 'mode': 'Vibration supports'},
                    {'cause': 'corrosion', 'f': 2, 'g': 2, 'd': 2, 'mode': 'Corrosion supports'}
                ],
                'tube_porteur': [
                    {'cause': 'fatigue', 'f': 2, 'g': 3, 'd': 3, 'mode': 'Fatigue cyclique'},
                    {'cause': 'surchauffe', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Contraintes thermiques'},
                    {'cause': 'corrosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Corrosion supports'}
                ]
            },
            'rechauffeur_ht': {
                'branches_sortie': [
                    {'cause': 'corrosion', 'f': 3, 'g': 4, 'd': 2, 'mode': 'Acid attack'},
                    {'cause': 'erosion', 'f': 3, 'g': 3, 'd': 2, 'mode': 'Surface fromage suisse'},
                    {'cause': 'encrassement', 'f': 4, 'g': 2, 'd': 1, 'mode': 'Dépôts acides'}
                ],
                'collecteur_entree': [
                    {'cause': 'corrosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Waterside corrosion'},
                    {'cause': 'encrassement', 'f': 3, 'g': 2, 'd': 2, 'mode': 'Dépôts internes'},
                    {'cause': 'fissure', 'f': 2, 'g': 3, 'd': 3, 'mode': 'Fissures internes'}
                ],
                'collecteur_sortie': [
                    {'cause': 'fissure', 'f': 2, 'g': 4, 'd': 3, 'mode': 'Dissimilar metal weld'},
                    {'cause': 'fatigue', 'f': 2, 'g': 3, 'd': 3, 'mode': 'Contraintes interfaces'},
                    {'cause': 'corrosion', 'f': 2, 'g': 3, 'd': 2, 'mode': 'Corrosion soudures'}
                ]
            }
        }
        
        # Générer le dataset
        for component, subcomponents in amdec_knowledge.items():
            for subcomponent, entries in subcomponents.items():
                for entry in entries:
                    data.append({
                        'Composant': component,
                        'Sous-composant': subcomponent,
                        'Cause': entry['cause'],
                        'F': entry['f'],
                        'G': entry['g'],
                        'D': entry['d'],
                        'C': entry['f'] * entry['g'] * entry['d'],
                        'Mode de Défaillance': entry['mode'],
                        'Fonction': self._get_default_function(component, subcomponent),
                        'Effet': self._get_default_effect(entry['mode'])
                    })
        
        df = pd.DataFrame(data)
        logger.info(f"Dataset AMDEC par défaut créé: {len(df)} entrées")
        return df
    
    def _create_default_gamme_dataset(self) -> pd.DataFrame:
        """Crée un dataset Gammes par défaut"""
        data = []
        
        # Données d'exemple pour les gammes de maintenance
        gamme_patterns = {
            'economiseur_bt': {
                'epingle': {
                    'operations': ['Inspection visuelle', 'Contrôle ultrasons', 'Nettoyage'],
                    'durations': [15, 25, 30],
                    'materials': ['Lampe torche', 'Ultrasons', 'Brosse'],
                    'frequency': 'Semestrielle'
                },
                'collecteur_sortie': {
                    'operations': ['Inspection visuelle', 'Test étanchéité', 'Traitement'],
                    'durations': [20, 30, 30],
                    'materials': ['Lampe', 'Kit test', 'Peinture'],
                    'frequency': 'Trimestrielle'
                }
            },
            'surchauffeur_ht': {
                'tube_porteur': {
                    'operations': ['Inspection', 'Surveillance', 'Analyse contraintes'],
                    'durations': [30, 60, 45],
                    'materials': ['Caméra', 'Capteurs', 'Analyseur'],
                    'frequency': 'Mensuelle'
                }
            }
        }
        
        for component, subcomponents in gamme_patterns.items():
            for subcomponent, pattern in subcomponents.items():
                criticality = ComponentConfig.get_default_criticality(component, subcomponent)
                
                data.append({
                    'Composant': component,
                    'Sous-composant': subcomponent,
                    'Criticité': criticality,
                    'Opérations': ' + '.join(pattern['operations']),
                    'Durée_totale': sum(pattern['durations']),
                    'Matériels': ' + '.join(pattern['materials']),
                    'Fréquence': pattern['frequency'],
                    'Nb_opérations': len(pattern['operations'])
                })
        
        df = pd.DataFrame(data)
        logger.info(f"Dataset Gammes par défaut créé: {len(df)} entrées")
        return df
    
    def _get_default_function(self, component: str, subcomponent: str) -> str:
        """Retourne la fonction par défaut d'un composant"""
        functions = {
            'economiseur_bt': {'epingle': 'Transfert thermique', 'collecteur_sortie': 'Collecte vapeur'},
            'economiseur_ht': {'collecteur_entree': 'Distribution vapeur', 'tubes_suspension': 'Support'},
            'surchauffeur_bt': {'epingle': 'Surchauffe vapeur', 'collecteur_entree': 'Distribution'},
            'surchauffeur_ht': {'tube_porteur': 'Support pression', 'branches_entree': 'Distribution', 'collecteur_sortie': 'Collecte'},
            'rechauffeur_bt': {'collecteur_entree': 'Distribution', 'tubes_suspension': 'Support', 'tube_porteur': 'Support'},
            'rechauffeur_ht': {'branches_sortie': 'Évacuation', 'collecteur_entree': 'Distribution', 'collecteur_sortie': 'Collecte'}
        }
        return functions.get(component, {}).get(subcomponent, 'Support et échange')
    
    def _get_default_effect(self, mode: str) -> str:
        """Retourne l'effet par défaut d'un mode de défaillance"""
        effects = {
            'Corrosion externe': 'Amincissement parois',
            'Érosion par cendres': 'Perte matière',
            'Encrassement interne': 'Réduction débit',
            'Caustic attack': 'Perte matière interne',
            'Short-term overheat': 'Rupture ductile',
            'Long-term overheat': 'Rupture fluage',
            'Fatigue thermique': 'Fissures',
            'SCC (Stress Corrosion Cracking)': 'Fissures intergranulaires'
        }
        return effects.get(mode, 'Impact performance')
    
    def train_models(self, model_type: str = 'both') -> Dict:
        """
        Entraîne les modèles ML
        
        Args:
            model_type: Type de modèle à entraîner ('amdec', 'gamme', ou 'both')
            
        Returns:
            Résultats de l'entraînement
        """
        results = {}
        
        try:
            if model_type in ['amdec', 'both']:
                results['amdec'] = self._train_amdec_models()
            
            if model_type in ['gamme', 'both']:
                results['gamme'] = self._train_gamme_models()
            
            logger.info(f"Entraînement terminé pour: {model_type}")
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement: {e}")
            raise
    
    def _train_amdec_models(self) -> Dict:
        """Entraîne les modèles AMDEC"""
        df = self.datasets['amdec'].copy()
        
        # Préparation des données
        df['Composant'] = df['Composant'].apply(normalize_component_name)
        df['Sous-composant'] = df['Sous-composant'].apply(normalize_subcomponent_name)
        
        # Encodage des variables catégorielles
        le_comp = LabelEncoder()
        le_subcomp = LabelEncoder()
        le_cause = LabelEncoder()
        
        df['Composant_encoded'] = le_comp.fit_transform(df['Composant'])
        df['Sous-composant_encoded'] = le_subcomp.fit_transform(df['Sous-composant'])
        df['Cause_encoded'] = le_cause.fit_transform(df['Cause'])
        
        # Sauvegarder les encodeurs
        self.encoders['amdec'] = {
            'composant': le_comp,
            'sous_composant': le_subcomp,
            'cause': le_cause
        }
        
        # Modèle de prédiction de criticité
        X_crit = df[['Composant_encoded', 'Sous-composant_encoded', 'Cause_encoded']]
        y_crit = df['C']
        
        X_train, X_test, y_train, y_test = train_test_split(X_crit, y_crit, test_size=0.2, random_state=42)
        
        # Modèle Random Forest pour la criticité
        rf_crit = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_crit.fit(X_train, y_train)
        
        y_pred = rf_crit.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        
        self.models['criticality_predictor'] = rf_crit
        
        # Modèle de prédiction des valeurs F, G, D
        models_fgd = {}
        scores_fgd = {}
        
        for target in ['F', 'G', 'D']:
            X_fgd = df[['Composant_encoded', 'Sous-composant_encoded', 'Cause_encoded']]
            y_fgd = df[target]
            
            X_train, X_test, y_train, y_test = train_test_split(X_fgd, y_fgd, test_size=0.2, random_state=42)
            
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_train, y_train)
            
            y_pred = clf.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            models_fgd[target] = clf
            scores_fgd[target] = accuracy
        
        self.models['fgd_predictors'] = models_fgd
        
        # Sauvegarder les modèles
        self._save_models('amdec')
        
        return {
            'criticality_mse': mse,
            'fgd_accuracies': scores_fgd,
            'samples_trained': len(df)
        }
    
    def _train_gamme_models(self) -> Dict:
        """Entraîne les modèles Gammes"""
        df = self.datasets['gamme'].copy()
        
        # Préparation des données
        df['Composant'] = df['Composant'].apply(normalize_component_name)
        df['Sous-composant'] = df['Sous-composant'].apply(normalize_subcomponent_name)
        
        # Encodage
        le_comp = LabelEncoder()
        le_subcomp = LabelEncoder()
        
        df['Composant_encoded'] = le_comp.fit_transform(df['Composant'])
        df['Sous-composant_encoded'] = le_subcomp.fit_transform(df['Sous-composant'])
        
        self.encoders['gamme'] = {
            'composant': le_comp,
            'sous_composant': le_subcomp
        }
        
        # Modèle de prédiction de durée totale
        X_duration = df[['Composant_encoded', 'Sous-composant_encoded', 'Criticité']]
        y_duration = df['Durée_totale']
        
        X_train, X_test, y_train, y_test = train_test_split(X_duration, y_duration, test_size=0.2, random_state=42)
        
        rf_duration = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_duration.fit(X_train, y_train)
        
        y_pred = rf_duration.predict(X_test)
        mse_duration = mean_squared_error(y_test, y_pred)
        
        self.models['duration_predictor'] = rf_duration
        
        # Modèle de prédiction du nombre d'opérations
        y_nb_ops = df['Nb_opérations']
        
        X_train, X_test, y_train, y_test = train_test_split(X_duration, y_nb_ops, test_size=0.2, random_state=42)
        
        rf_ops = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_ops.fit(X_train, y_train)
        
        y_pred_ops = rf_ops.predict(X_test)
        mse_ops = mean_squared_error(y_test, y_pred_ops)
        
        self.models['operations_predictor'] = rf_ops
        
        # Sauvegarder les modèles
        self._save_models('gamme')
        
        return {
            'duration_mse': mse_duration,
            'operations_mse': mse_ops,
            'samples_trained': len(df)
        }
    
    def predict_criticality(self, component: str, subcomponent: str, cause: str = None) -> int:
        """
        Prédit la criticité pour un composant/sous-composant
        
        Args:
            component: Nom du composant
            subcomponent: Nom du sous-composant
            cause: Cause (optionnel)
            
        Returns:
            Criticité prédite
        """
        try:
            # Normaliser les entrées
            component = normalize_component_name(component)
            subcomponent = normalize_subcomponent_name(subcomponent)
            
            # Vérifier si le modèle existe
            if 'criticality_predictor' not in self.models:
                # Utiliser la valeur par défaut
                return ComponentConfig.get_default_criticality(component, subcomponent)
            
            # Encoder les valeurs
            encoders = self.encoders['amdec']
            
            try:
                comp_encoded = encoders['composant'].transform([component])[0]
                subcomp_encoded = encoders['sous_composant'].transform([subcomponent])[0]
                
                if cause:
                    cause_encoded = encoders['cause'].transform([cause])[0]
                else:
                    # Utiliser une cause moyenne si non spécifiée
                    cause_encoded = 0
                
                # Prédiction
                X = [[comp_encoded, subcomp_encoded, cause_encoded]]
                criticality = self.models['criticality_predictor'].predict(X)[0]
                
                return max(1, min(80, int(round(criticality))))  # Limiter entre 1 et 80
                
            except ValueError:
                # Composant non vu pendant l'entraînement
                return ComponentConfig.get_default_criticality(component, subcomponent)
            
        except Exception as e:
            logger.warning(f"Erreur prédiction criticité: {e}")
            return ComponentConfig.get_default_criticality(component, subcomponent)
    
    def predict_maintenance_duration(self, component: str, subcomponent: str, criticality: int) -> int:
        """
        Prédit la durée de maintenance
        
        Args:
            component: Nom du composant
            subcomponent: Nom du sous-composant
            criticality: Criticité
            
        Returns:
            Durée en minutes
        """
        try:
            if 'duration_predictor' not in self.models:
                # Estimation basée sur la criticité
                return max(60, criticality * 3)
            
            # Normaliser et encoder
            component = normalize_component_name(component)
            subcomponent = normalize_subcomponent_name(subcomponent)
            
            encoders = self.encoders['gamme']
            
            try:
                comp_encoded = encoders['composant'].transform([component])[0]
                subcomp_encoded = encoders['sous_composant'].transform([subcomponent])[0]
                
                X = [[comp_encoded, subcomp_encoded, criticality]]
                duration = self.models['duration_predictor'].predict(X)[0]
                
                return max(30, int(round(duration)))  # Minimum 30 minutes
                
            except ValueError:
                return max(60, criticality * 3)
            
        except Exception as e:
            logger.warning(f"Erreur prédiction durée: {e}")
            return max(60, criticality * 3)
    
    def generate_amdec_from_dataset(self, component: str, subcomponent: str = None) -> List[Dict]:
        """
        Génère une AMDEC à partir du dataset d'entraînement
        
        Args:
            component: Composant à analyser
            subcomponent: Sous-composant spécifique (optionnel)
            
        Returns:
            Liste des entrées AMDEC
        """
        try:
            df = self.datasets['amdec'].copy()
            
            # Normaliser le composant
            component = normalize_component_name(component)
            
            # Filtrer par composant
            filtered_df = df[df['Composant'].str.contains(component, case=False, na=False)]
            
            # Filtrer par sous-composant si spécifié
            if subcomponent:
                subcomponent = normalize_subcomponent_name(subcomponent)
                filtered_df = filtered_df[filtered_df['Sous-composant'].str.contains(subcomponent, case=False, na=False)]
            
            if filtered_df.empty:
                logger.warning(f"Aucune donnée trouvée pour {component}")
                return []
            
            # Convertir en liste de dictionnaires
            amdec_data = []
            for _, row in filtered_df.iterrows():
                entry = {
                    'Composant': row['Composant'],
                    'Sous-composant': row['Sous-composant'],
                    'Fonction': row.get('Fonction', 'Non spécifiée'),
                    'Mode de Défaillance': row.get('Mode de Défaillance', 'Non spécifié'),
                    'Cause': row['Cause'],
                    'Effet': row.get('Effet', 'Impact performance'),
                    'F': int(row['F']),
                    'G': int(row['G']),
                    'D': int(row['D']),
                    'C': int(row['C']),
                    'Actions Correctives': row.get('Actions Correctives', 'À définir')
                }
                amdec_data.append(entry)
            
            logger.info(f"AMDEC générée à partir du dataset: {len(amdec_data)} entrées")
            return amdec_data
            
        except Exception as e:
            logger.error(f"Erreur génération AMDEC dataset: {e}")
            return []
    
    def _save_models(self, model_type: str):
        """Sauvegarde les modèles entraînés"""
        try:
            if model_type == 'amdec':
                models_to_save = {
                    'criticality_predictor': self.models.get('criticality_predictor'),
                    'fgd_predictors': self.models.get('fgd_predictors'),
                    'encoders': self.encoders.get('amdec')
                }
                joblib.dump(models_to_save, os.path.join(self.models_dir, 'amdec_models.pkl'))
                
            elif model_type == 'gamme':
                models_to_save = {
                    'duration_predictor': self.models.get('duration_predictor'),
                    'operations_predictor': self.models.get('operations_predictor'),
                    'encoders': self.encoders.get('gamme')
                }
                joblib.dump(models_to_save, os.path.join(self.models_dir, 'gamme_models.pkl'))
            
            logger.info(f"Modèles {model_type} sauvegardés")
            
        except Exception as e:
            logger.warning(f"Erreur sauvegarde modèles {model_type}: {e}")
    
    def load_models(self, model_type: str = 'both'):
        """Charge les modèles sauvegardés"""
        try:
            if model_type in ['amdec', 'both']:
                amdec_path = os.path.join(self.models_dir, 'amdec_models.pkl')
                if os.path.exists(amdec_path):
                    amdec_models = joblib.load(amdec_path)
                    self.models.update({
                        'criticality_predictor': amdec_models['criticality_predictor'],
                        'fgd_predictors': amdec_models['fgd_predictors']
                    })
                    self.encoders['amdec'] = amdec_models['encoders']
                    logger.info("Modèles AMDEC chargés")
            
            if model_type in ['gamme', 'both']:
                gamme_path = os.path.join(self.models_dir, 'gamme_models.pkl')
                if os.path.exists(gamme_path):
                    gamme_models = joblib.load(gamme_path)
                    self.models.update({
                        'duration_predictor': gamme_models['duration_predictor'],
                        'operations_predictor': gamme_models['operations_predictor']
                    })
                    self.encoders['gamme'] = gamme_models['encoders']
                    logger.info("Modèles Gammes chargés")
                    
        except Exception as e:
            logger.warning(f"Erreur chargement modèles: {e}")
    
    def get_model_info(self) -> Dict:
        """Retourne les informations sur les modèles"""
        return {
            'loaded_models': list(self.models.keys()),
            'dataset_sizes': {name: len(df) for name, df in self.datasets.items()},
            'encoders_available': list(self.encoders.keys())
        }