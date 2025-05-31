#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèles de Machine Learning pour AMDEC & Gamme IA
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import logging
from abc import ABC, abstractmethod

try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.svm import SVR, SVC
    from sklearn.neural_network import MLPRegressor, MLPClassifier
    from sklearn.model_selection import cross_val_score, GridSearchCV
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class BaseMLModel(ABC):
    """Classe de base pour tous les modèles ML"""
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.scaler = None
        self.encoder = None
        self.is_trained = False
        self.feature_names = []
        self.performance_metrics = {}
    
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Entraîne le modèle"""
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Fait des prédictions"""
        pass
    
    def get_feature_importance(self) -> Dict:
        """Retourne l'importance des features si disponible"""
        if hasattr(self.model, 'feature_importances_'):
            return dict(zip(self.feature_names, self.model.feature_importances_))
        return {}

class CriticalityPredictor(BaseMLModel):
    """
    Modèle pour prédire la criticité (F×G×D) d'un composant
    """
    
    def __init__(self):
        super().__init__("CriticalityPredictor")
        if SKLEARN_AVAILABLE:
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.scaler = StandardScaler()
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les features pour l'entraînement"""
        features = df.copy()
        
        # Encoder les variables catégorielles
        categorical_cols = ['Composant', 'Sous-composant', 'Cause']
        
        for col in categorical_cols:
            if col in features.columns:
                if self.encoder is None:
                    self.encoder = {}
                
                if col not in self.encoder:
                    self.encoder[col] = LabelEncoder()
                    features[f'{col}_encoded'] = self.encoder[col].fit_transform(features[col].astype(str))
                else:
                    # Pour les nouvelles données, gérer les valeurs inconnues
                    try:
                        features[f'{col}_encoded'] = self.encoder[col].transform(features[col].astype(str))
                    except ValueError:
                        # Valeur inconnue, utiliser -1
                        features[f'{col}_encoded'] = -1
        
        # Sélectionner les features numériques
        feature_cols = [col for col in features.columns if col.endswith('_encoded')]
        
        # Ajouter d'autres features si disponibles
        if 'F' in features.columns:
            feature_cols.append('F')
        if 'G' in features.columns:
            feature_cols.append('G')
        if 'D' in features.columns:
            feature_cols.append('D')
        
        self.feature_names = feature_cols
        return features[feature_cols]
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Entraîne le modèle de prédiction de criticité"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn n'est pas disponible")
        
        try:
            # Préparer les features
            X_processed = self.prepare_features(X)
            
            # Normaliser les features
            X_scaled = self.scaler.fit_transform(X_processed)
            
            # Entraîner le modèle
            self.model.fit(X_scaled, y)
            
            # Validation croisée
            cv_scores = cross_val_score(self.model, X_scaled, y, cv=5, scoring='neg_mean_squared_error')
            
            # Calculer les métriques
            y_pred = self.model.predict(X_scaled)
            mse = mean_squared_error(y, y_pred)
            
            self.performance_metrics = {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'cv_score_mean': -cv_scores.mean(),
                'cv_score_std': cv_scores.std(),
                'r2_score': self.model.score(X_scaled, y)
            }
            
            self.is_trained = True
            
            logger.info(f"Modèle {self.name} entraîné avec succès. RMSE: {self.performance_metrics['rmse']:.2f}")
            
            return self.performance_metrics
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement du modèle {self.name}: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Prédit la criticité pour de nouvelles données"""
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
        
        # Préparer les features
        X_processed = self.prepare_features(X)
        
        # Normaliser
        X_scaled = self.scaler.transform(X_processed)
        
        # Prédire
        predictions = self.model.predict(X_scaled)
        
        # S'assurer que les prédictions sont dans une plage raisonnable
        predictions = np.clip(predictions, 1, 100)
        
        return predictions.astype(int)

class MaintenancePredictor(BaseMLModel):
    """
    Modèle pour prédire les paramètres de maintenance
    """
    
    def __init__(self):
        super().__init__("MaintenancePredictor")
        if SKLEARN_AVAILABLE:
            # Modèles pour différents aspects
            self.duration_model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.frequency_model = RandomForestClassifier(n_estimators=50, random_state=42)
            self.operations_model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.scaler = StandardScaler()
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les features pour l'entraînement"""
        features = df.copy()
        
        # Features de base
        feature_cols = []
        
        if 'Criticité' in features.columns:
            feature_cols.append('Criticité')
        
        # Encoder le composant et sous-composant
        categorical_cols = ['Composant', 'Sous-composant']
        
        for col in categorical_cols:
            if col in features.columns:
                if self.encoder is None:
                    self.encoder = {}
                
                if col not in self.encoder:
                    self.encoder[col] = LabelEncoder()
                    features[f'{col}_encoded'] = self.encoder[col].fit_transform(features[col].astype(str))
                else:
                    try:
                        features[f'{col}_encoded'] = self.encoder[col].transform(features[col].astype(str))
                    except ValueError:
                        features[f'{col}_encoded'] = -1
                
                feature_cols.append(f'{col}_encoded')
        
        self.feature_names = feature_cols
        return features[feature_cols]
    
    def train(self, X: pd.DataFrame, y_dict: Dict[str, pd.Series]) -> Dict:
        """Entraîne les modèles de maintenance"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn n'est pas disponible")
        
        try:
            # Préparer les features
            X_processed = self.prepare_features(X)
            X_scaled = self.scaler.fit_transform(X_processed)
            
            results = {}
            
            # Entraîner le modèle de durée
            if 'duration' in y_dict:
                self.duration_model.fit(X_scaled, y_dict['duration'])
                duration_score = self.duration_model.score(X_scaled, y_dict['duration'])
                results['duration_r2'] = duration_score
            
            # Entraîner le modèle de fréquence
            if 'frequency' in y_dict:
                self.frequency_model.fit(X_scaled, y_dict['frequency'])
                frequency_score = self.frequency_model.score(X_scaled, y_dict['frequency'])
                results['frequency_accuracy'] = frequency_score
            
            # Entraîner le modèle d'opérations
            if 'operations' in y_dict:
                self.operations_model.fit(X_scaled, y_dict['operations'])
                operations_score = self.operations_model.score(X_scaled, y_dict['operations'])
                results['operations_r2'] = operations_score
            
            self.performance_metrics = results
            self.is_trained = True
            
            logger.info(f"Modèle {self.name} entraîné avec succès")
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement du modèle {self.name}: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Prédit les paramètres de maintenance"""
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
        
        # Préparer les features
        X_processed = self.prepare_features(X)
        X_scaled = self.scaler.transform(X_processed)
        
        predictions = {}
        
        # Prédire la durée
        if hasattr(self, 'duration_model'):
            duration_pred = self.duration_model.predict(X_scaled)
            predictions['duration'] = np.clip(duration_pred, 30, 300).astype(int)
        
        # Prédire la fréquence
        if hasattr(self, 'frequency_model'):
            frequency_pred = self.frequency_model.predict(X_scaled)
            predictions['frequency'] = frequency_pred
        
        # Prédire le nombre d'opérations
        if hasattr(self, 'operations_model'):
            operations_pred = self.operations_model.predict(X_scaled)
            predictions['operations'] = np.clip(operations_pred, 1, 10).astype(int)
        
        return predictions

class ComponentClassifier(BaseMLModel):
    """
    Modèle pour classifier et identifier les composants
    """
    
    def __init__(self):
        super().__init__("ComponentClassifier")
        if SKLEARN_AVAILABLE:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )
            self.scaler = StandardScaler()
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Entraîne le classificateur de composants"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn n'est pas disponible")
        
        try:
            # Préparer les features textuelles
            X_processed = self._extract_text_features(X)
            
            # Normaliser
            X_scaled = self.scaler.fit_transform(X_processed)
            
            # Entraîner
            self.model.fit(X_scaled, y)
            
            # Validation croisée
            cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)
            
            # Métriques
            y_pred = self.model.predict(X_scaled)
            accuracy = accuracy_score(y, y_pred)
            
            self.performance_metrics = {
                'accuracy': accuracy,
                'cv_score_mean': cv_scores.mean(),
                'cv_score_std': cv_scores.std()
            }
            
            self.is_trained = True
            
            logger.info(f"Modèle {self.name} entraîné avec succès. Précision: {accuracy:.2f}")
            
            return self.performance_metrics
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement du modèle {self.name}: {e}")
            raise
    
    def _extract_text_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Extrait des features à partir du texte"""
        # Méthode simple : longueur des chaînes, mots-clés, etc.
        features = pd.DataFrame()
        
        if 'text' in X.columns:
            features['text_length'] = X['text'].str.len()
            features['word_count'] = X['text'].str.split().str.len()
            
            # Mots-clés indicateurs
            keywords = ['corrosion', 'fissure', 'erosion', 'fatigue', 'surchauffe']
            for keyword in keywords:
                features[f'has_{keyword}'] = X['text'].str.contains(keyword, case=False).astype(int)
        
        # Si pas de features textuelles, créer des features par défaut
        if features.empty:
            features['default'] = [1] * len(X)
        
        return features
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Classifie les composants"""
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
        
        # Préparer les features
        X_processed = self._extract_text_features(X)
        X_scaled = self.scaler.transform(X_processed)
        
        # Prédire
        predictions = self.model.predict(X_scaled)
        
        return predictions

# Factory pour créer les modèles
class ModelFactory:
    """Factory pour créer et gérer les modèles ML"""
    
    @staticmethod
    def create_model(model_type: str) -> BaseMLModel:
        """Crée un modèle selon le type spécifié"""
        if model_type == 'criticality':
            return CriticalityPredictor()
        elif model_type == 'maintenance':
            return MaintenancePredictor()
        elif model_type == 'classifier':
            return ComponentClassifier()
        else:
            raise ValueError(f"Type de modèle non supporté: {model_type}")
    
    @staticmethod
    def get_available_models() -> List[str]:
        """Retourne la liste des modèles disponibles"""
        return ['criticality', 'maintenance', 'classifier']

# Configuration des hyperparamètres pour l'optimisation
HYPERPARAMETER_GRIDS = {
    'RandomForestRegressor': {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10]
    },
    'RandomForestClassifier': {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10]
    }
}

def optimize_hyperparameters(model: BaseMLModel, X: pd.DataFrame, y: pd.Series, 
                           param_grid: Dict = None) -> Dict:
    """Optimise les hyperparamètres d'un modèle"""
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn n'est pas disponible")
    
    if param_grid is None:
        model_name = model.model.__class__.__name__
        param_grid = HYPERPARAMETER_GRIDS.get(model_name, {})
    
    if not param_grid:
        logger.warning("Aucune grille d'hyperparamètres définie")
        return {}
    
    # Recherche par grille
    grid_search = GridSearchCV(
        model.model, 
        param_grid, 
        cv=3, 
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X, y)
    
    # Mettre à jour le modèle avec les meilleurs paramètres
    model.model = grid_search.best_estimator_
    
    return {
        'best_params': grid_search.best_params_,
        'best_score': grid_search.best_score_,
        'cv_results': grid_search.cv_results_
    }