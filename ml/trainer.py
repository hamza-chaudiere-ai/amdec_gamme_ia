#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'entraînement ML pour AMDEC & Gamme IA
Orchestrateur pour l'entraînement de tous les modèles
"""

import pandas as pd
import numpy as np
import logging
import os
import joblib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .models import ModelFactory, CriticalityPredictor, MaintenancePredictor, ComponentClassifier
from .predictor import SmartPredictor

logger = logging.getLogger(__name__)

class MLTrainer:
    """
    Classe principale pour l'entraînement des modèles ML
    """
    
    def __init__(self, data_dir: str = 'data/dataset', models_dir: str = 'ml/saved_models'):
        """
        Initialise l'entraîneur ML
        
        Args:
            data_dir: Répertoire des datasets
            models_dir: Répertoire de sauvegarde des modèles
        """
        self.data_dir = data_dir
        self.models_dir = models_dir
        self.datasets = {}
        self.models = {}
        self.training_history = []
        
        # Créer les répertoires nécessaires
        os.makedirs(models_dir, exist_ok=True)
        
        # Charger les datasets
        self._load_datasets()
    
    def _load_datasets(self):
        """Charge tous les datasets disponibles"""
        try:
            # Dataset AMDEC
            amdec_path = os.path.join(self.data_dir, 'amdec_dataset.xlsx')
            if os.path.exists(amdec_path):
                self.datasets['amdec'] = pd.read_excel(amdec_path)
                logger.info(f"Dataset AMDEC chargé: {len(self.datasets['amdec'])} entrées")
            else:
                logger.warning(f"Dataset AMDEC non trouvé: {amdec_path}")
            
            # Dataset Gammes
            gamme_path = os.path.join(self.data_dir, 'gamme_dataset.xlsx')
            if os.path.exists(gamme_path):
                self.datasets['gamme'] = pd.read_excel(gamme_path)
                logger.info(f"Dataset Gammes chargé: {len(self.datasets['gamme'])} entrées")
            else:
                logger.warning(f"Dataset Gammes non trouvé: {gamme_path}")
            
            if not self.datasets:
                logger.error("Aucun dataset trouvé. Création de datasets par défaut.")
                self._create_default_datasets()
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des datasets: {e}")
            self._create_default_datasets()
    
    def _create_default_datasets(self):
        """Crée des datasets par défaut en cas d'absence"""
        # Dataset AMDEC minimal
        default_amdec = pd.DataFrame([
            {'Composant': 'economiseur_bt', 'Sous-composant': 'epingle', 'Cause': 'corrosion', 'F': 3, 'G': 4, 'D': 2, 'C': 24},
            {'Composant': 'surchauffeur_ht', 'Sous-composant': 'tube_porteur', 'Cause': 'surchauffe', 'F': 2, 'G': 5, 'D': 2, 'C': 20},
            {'Composant': 'rechauffeur_ht', 'Sous-composant': 'branches_sortie', 'Cause': 'corrosion', 'F': 3, 'G': 4, 'D': 2, 'C': 24}
        ])
        
        # Dataset Gammes minimal
        default_gamme = pd.DataFrame([
            {'Composant': 'economiseur_bt', 'Sous-composant': 'epingle', 'Criticité': 24, 'Durée_Totale_Min': 60, 'Nb_Opérations': 3, 'Fréquence_Maintenance': 'Trimestrielle'},
            {'Composant': 'surchauffeur_ht', 'Sous-composant': 'tube_porteur', 'Criticité': 20, 'Durée_Totale_Min': 135, 'Nb_Opérations': 4, 'Fréquence_Maintenance': 'Mensuelle'},
            {'Composant': 'rechauffeur_ht', 'Sous-composant': 'branches_sortie', 'Criticité': 36, 'Durée_Totale_Min': 120, 'Nb_Opérations': 4, 'Fréquence_Maintenance': 'Mensuelle'}
        ])
        
        self.datasets = {
            'amdec': default_amdec,
            'gamme': default_gamme
        }
        
        logger.info("Datasets par défaut créés")
    
    def train_all_models(self, test_size: float = 0.2, random_state: int = 42) -> Dict:
        """
        Entraîne tous les modèles ML disponibles
        
        Args:
            test_size: Proportion des données pour le test
            random_state: Graine aléatoire pour la reproductibilité
            
        Returns:
            Résultats d'entraînement pour tous les modèles
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn n'est pas disponible")
            return {'error': 'scikit-learn requis pour l\'entraînement ML'}
        
        logger.info("Début de l'entraînement de tous les modèles ML")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'models_trained': [],
            'performance': {},
            'errors': []
        }
        
        try:
            # 1. Entraîner le modèle de criticité
            if 'amdec' in self.datasets:
                criticality_results = self._train_criticality_model(test_size, random_state)
                results['models_trained'].append('criticality')
                results['performance']['criticality'] = criticality_results
            else:
                results['errors'].append('Dataset AMDEC non disponible pour le modèle de criticité')
            
            # 2. Entraîner le modèle de maintenance
            if 'gamme' in self.datasets:
                maintenance_results = self._train_maintenance_model(test_size, random_state)
                results['models_trained'].append('maintenance')
                results['performance']['maintenance'] = maintenance_results
            else:
                results['errors'].append('Dataset Gammes non disponible pour le modèle de maintenance')
            
            # 3. Entraîner le classificateur (si données textuelles disponibles)
            classifier_results = self._train_classifier_model(test_size, random_state)
            if classifier_results:
                results['models_trained'].append('classifier')
                results['performance']['classifier'] = classifier_results
            
            # 4. Sauvegarder les modèles entraînés
            self._save_all_models()
            
            # 5. Enregistrer dans l'historique
            self._record_training_session(results)
            
            logger.info(f"Entraînement terminé. Modèles entraînés: {results['models_trained']}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement des modèles: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _train_criticality_model(self, test_size: float, random_state: int) -> Dict:
        """Entraîne le modèle de prédiction de criticité"""
        logger.info("Entraînement du modèle de criticité...")
        
        try:
            df = self.datasets['amdec'].copy()
            
            # Préparer les features et targets
            X = df[['Composant', 'Sous-composant', 'Cause', 'F', 'G', 'D']]
            y = df['C']
            
            # Créer et entraîner le modèle
            model = CriticalityPredictor()
            
            # Division train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Entraînement
            train_results = model.train(X_train, y_train)
            
            # Évaluation sur le test set
            y_pred = model.predict(X_test)
            test_mse = mean_squared_error(y_test, y_pred)
            test_rmse = np.sqrt(test_mse)
            
            # Stocker le modèle
            self.models['criticality'] = model
            
            results = {
                'train_metrics': train_results,
                'test_mse': test_mse,
                'test_rmse': test_rmse,
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'feature_importance': model.get_feature_importance()
            }
            
            logger.info(f"Modèle de criticité entraîné. RMSE test: {test_rmse:.2f}")
            return results
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèle criticité: {e}")
            raise
    
    def _train_maintenance_model(self, test_size: float, random_state: int) -> Dict:
        """Entraîne le modèle de prédiction de maintenance"""
        logger.info("Entraînement du modèle de maintenance...")
        
        try:
            df = self.datasets['gamme'].copy()
            
            # Préparer les features
            X = df[['Composant', 'Sous-composant', 'Criticité']]
            
            # Préparer les targets multiples
            y_dict = {}
            if 'Durée_Totale_Min' in df.columns:
                y_dict['duration'] = df['Durée_Totale_Min']
            if 'Nb_Opérations' in df.columns:
                y_dict['operations'] = df['Nb_Opérations']
            if 'Fréquence_Maintenance' in df.columns:
                y_dict['frequency'] = df['Fréquence_Maintenance']
            
            if not y_dict:
                raise ValueError("Aucune variable cible trouvée dans le dataset gammes")
            
            # Créer et entraîner le modèle
            model = MaintenancePredictor()
            
            # Division train/test
            X_train, X_test = train_test_split(X, test_size=test_size, random_state=random_state)
            
            # Diviser aussi les targets
            y_train_dict = {}
            y_test_dict = {}
            for key, target in y_dict.items():
                y_train, y_test = train_test_split(target, test_size=test_size, random_state=random_state)
                y_train_dict[key] = y_train
                y_test_dict[key] = y_test
            
            # Entraînement
            train_results = model.train(X_train, y_train_dict)
            
            # Évaluation sur le test set
            test_predictions = model.predict(X_test)
            
            test_results = {}
            for key in y_test_dict.keys():
                if key in test_predictions and key in ['duration', 'operations']:
                    # Métriques pour les variables continues
                    test_mse = mean_squared_error(y_test_dict[key], test_predictions[key])
                    test_results[f'{key}_test_mse'] = test_mse
                    test_results[f'{key}_test_rmse'] = np.sqrt(test_mse)
                elif key in test_predictions and key == 'frequency':
                    # Métrique pour les variables catégorielles
                    test_acc = accuracy_score(y_test_dict[key], test_predictions[key])
                    test_results[f'{key}_test_accuracy'] = test_acc
            
            # Stocker le modèle
            self.models['maintenance'] = model
            
            results = {
                'train_metrics': train_results,
                'test_metrics': test_results,
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'targets_trained': list(y_dict.keys())
            }
            
            logger.info(f"Modèle de maintenance entraîné pour {len(y_dict)} cibles")
            return results
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèle maintenance: {e}")
            raise
    
    def _train_classifier_model(self, test_size: float, random_state: int) -> Optional[Dict]:
        """Entraîne le modèle classificateur si données disponibles"""
        logger.info("Tentative d'entraînement du classificateur...")
        
        try:
            # Créer des données synthétiques pour le classificateur
            # En l'absence de données textuelles réelles
            synthetic_data = []
            
            if 'amdec' in self.datasets:
                df = self.datasets['amdec']
                
                # Créer des descriptions textuelles synthétiques
                for _, row in df.iterrows():
                    description = f"Composant {row['Composant']} sous-composant {row['Sous-composant']} cause {row['Cause']}"
                    synthetic_data.append({
                        'text': description,
                        'component_type': row['Composant']
                    })
            
            if len(synthetic_data) < 5:  # Minimum pour l'entraînement
                logger.info("Données insuffisantes pour le classificateur")
                return None
            
            # Convertir en DataFrame
            df_classifier = pd.DataFrame(synthetic_data)
            
            X = df_classifier[['text']]
            y = df_classifier['component_type']
            
            # Vérifier qu'il y a assez de classes
            if y.nunique() < 2:
                logger.info("Pas assez de classes pour le classificateur")
                return None
            
            # Division train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            # Créer et entraîner le modèle
            model = ComponentClassifier()
            train_results = model.train(X_train, y_train)
            
            # Évaluation
            y_pred = model.predict(X_test)
            test_accuracy = accuracy_score(y_test, y_pred)
            
            # Stocker le modèle
            self.models['classifier'] = model
            
            results = {
                'train_metrics': train_results,
                'test_accuracy': test_accuracy,
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'classes': list(y.unique())
            }
            
            logger.info(f"Classificateur entraîné. Précision test: {test_accuracy:.2f}")
            return results
            
        except Exception as e:
            logger.warning(f"Impossible d'entraîner le classificateur: {e}")
            return None
    
    def _save_all_models(self):
        """Sauvegarde tous les modèles entraînés"""
        try:
            saved_count = 0
            
            for model_name, model in self.models.items():
                if hasattr(model, 'is_trained') and model.is_trained:
                    filename = f"{model_name}_model.pkl"
                    filepath = os.path.join(self.models_dir, filename)
                    
                    # Sauvegarder le modèle avec joblib
                    joblib.dump(model, filepath)
                    saved_count += 1
                    logger.info(f"Modèle {model_name} sauvegardé: {filepath}")
            
            # Sauvegarder aussi les métadonnées d'entraînement
            metadata = {
                'training_date': datetime.now().isoformat(),
                'models_saved': list(self.models.keys()),
                'dataset_info': {
                    name: len(df) for name, df in self.datasets.items()
                }
            }
            
            metadata_path = os.path.join(self.models_dir, 'training_metadata.pkl')
            joblib.dump(metadata, metadata_path)
            
            logger.info(f"{saved_count} modèles sauvegardés avec métadonnées")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des modèles: {e}")
    
    def _record_training_session(self, results: Dict):
        """Enregistre la session d'entraînement dans l'historique"""
        session_record = {
            'timestamp': results['timestamp'],
            'models_trained': results['models_trained'],
            'performance_summary': {
                model: perf.get('test_rmse', perf.get('test_accuracy', 'N/A'))
                for model, perf in results.get('performance', {}).items()
            },
            'dataset_sizes': {
                name: len(df) for name, df in self.datasets.items()
            },
            'errors': results.get('errors', [])
        }
        
        self.training_history.append(session_record)
        
        # Limiter l'historique à 50 sessions
        if len(self.training_history) > 50:
            self.training_history = self.training_history[-50:]
    
    def evaluate_models(self) -> Dict:
        """Évalue les performances des modèles entraînés"""
        if not self.models:
            return {'error': 'Aucun modèle entraîné disponible'}
        
        evaluation_results = {
            'timestamp': datetime.now().isoformat(),
            'models_evaluated': [],
            'performance_summary': {}
        }
        
        for model_name, model in self.models.items():
            if hasattr(model, 'is_trained') and model.is_trained:
                try:
                    # Évaluer sur l'ensemble de validation
                    if model_name == 'criticality' and 'amdec' in self.datasets:
                        df = self.datasets['amdec']
                        X = df[['Composant', 'Sous-composant', 'Cause', 'F', 'G', 'D']]
                        y_true = df['C']
                        y_pred = model.predict(X)
                        
                        mse = mean_squared_error(y_true, y_pred)
                        evaluation_results['performance_summary'][model_name] = {
                            'mse': mse,
                            'rmse': np.sqrt(mse),
                            'samples': len(X)
                        }
                    
                    elif model_name == 'maintenance' and 'gamme' in self.datasets:
                        df = self.datasets['gamme']
                        X = df[['Composant', 'Sous-composant', 'Criticité']]
                        predictions = model.predict(X)
                        
                        # Évaluer la prédiction de durée si disponible
                        if 'duration' in predictions and 'Durée_Totale_Min' in df.columns:
                            mse = mean_squared_error(df['Durée_Totale_Min'], predictions['duration'])
                            evaluation_results['performance_summary'][model_name] = {
                                'duration_mse': mse,
                                'duration_rmse': np.sqrt(mse),
                                'samples': len(X)
                            }
                    
                    evaluation_results['models_evaluated'].append(model_name)
                    
                except Exception as e:
                    logger.warning(f"Erreur lors de l'évaluation du modèle {model_name}: {e}")
        
        return evaluation_results
    
    def get_training_report(self) -> Dict:
        """Génère un rapport détaillé sur l'entraînement"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'datasets_info': {
                name: {
                    'size': len(df),
                    'columns': list(df.columns),
                    'missing_values': df.isnull().sum().to_dict()
                }
                for name, df in self.datasets.items()
            },
            'models_status': {
                name: {
                    'trained': hasattr(model, 'is_trained') and model.is_trained,
                    'performance': getattr(model, 'performance_metrics', {}),
                    'type': type(model).__name__
                }
                for name, model in self.models.items()
            },
            'training_history': self.training_history[-10:],  # 10 dernières sessions
            'recommendations': self._generate_training_recommendations()
        }
        
        return report
    
    def _generate_training_recommendations(self) -> List[str]:
        """Génère des recommandations pour améliorer l'entraînement"""
        recommendations = []
        
        # Vérifier la taille des datasets
        for name, df in self.datasets.items():
            if len(df) < 20:
                recommendations.append(f"Dataset {name} trop petit ({len(df)} entrées). Recommandé: >50 entrées")
        
        # Vérifier les performances des modèles
        for name, model in self.models.items():
            if hasattr(model, 'performance_metrics'):
                metrics = model.performance_metrics
                
                if name == 'criticality' and 'rmse' in metrics:
                    if metrics['rmse'] > 10:
                        recommendations.append(f"RMSE élevé pour le modèle de criticité ({metrics['rmse']:.1f}). Considérer plus de features.")
                
                elif name == 'maintenance' and any('accuracy' in k for k in metrics.keys()):
                    accuracies = [v for k, v in metrics.items() if 'accuracy' in k]
                    if accuracies and max(accuracies) < 0.7:
                        recommendations.append(f"Précision faible pour le modèle de maintenance. Enrichir les données.")
        
        # Recommandations générales
        if not recommendations:
            recommendations.append("Modèles entraînés avec succès. Continuer à enrichir les datasets avec des données terrain.")
        
        return recommendations
    
    def retrain_model(self, model_name: str, **kwargs) -> Dict:
        """Réentraîne un modèle spécifique"""
        if model_name not in ['criticality', 'maintenance', 'classifier']:
            return {'error': f'Modèle {model_name} non supporté'}
        
        logger.info(f"Réentraînement du modèle {model_name}")
        
        try:
            if model_name == 'criticality':
                return {'criticality': self._train_criticality_model(
                    kwargs.get('test_size', 0.2),
                    kwargs.get('random_state', 42)
                )}
            elif model_name == 'maintenance':
                return {'maintenance': self._train_maintenance_model(
                    kwargs.get('test_size', 0.2),
                    kwargs.get('random_state', 42)
                )}
            elif model_name == 'classifier':
                result = self._train_classifier_model(
                    kwargs.get('test_size', 0.2),
                    kwargs.get('random_state', 42)
                )
                return {'classifier': result} if result else {'error': 'Impossible d\'entraîner le classificateur'}
        
        except Exception as e:
            logger.error(f"Erreur lors du réentraînement de {model_name}: {e}")
            return {'error': str(e)}
    
    def export_models(self, export_path: str = None) -> str:
        """Exporte tous les modèles vers un répertoire"""
        if export_path is None:
            export_path = f"models_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        os.makedirs(export_path, exist_ok=True)
        
        exported_files = []
        
        # Exporter chaque modèle
        for model_name, model in self.models.items():
            if hasattr(model, 'is_trained') and model.is_trained:
                filename = f"{model_name}_model.pkl"
                filepath = os.path.join(export_path, filename)
                joblib.dump(model, filepath)
                exported_files.append(filename)
        
        # Exporter les métadonnées
        metadata = {
            'export_date': datetime.now().isoformat(),
            'models_exported': exported_files,
            'training_report': self.get_training_report()
        }
        
        metadata_path = os.path.join(export_path, 'export_metadata.json')
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Modèles exportés vers: {export_path}")
        return export_path
    
    def load_external_models(self, models_path: str) -> Dict:
        """Charge des modèles depuis un répertoire externe"""
        if not os.path.exists(models_path):
            return {'error': f'Répertoire {models_path} non trouvé'}
        
        loaded_models = []
        errors = []
        
        for filename in os.listdir(models_path):
            if filename.endswith('_model.pkl'):
                model_name = filename.replace('_model.pkl', '')
                filepath = os.path.join(models_path, filename)
                
                try:
                    model = joblib.load(filepath)
                    self.models[model_name] = model
                    loaded_models.append(model_name)
                    logger.info(f"Modèle {model_name} chargé depuis {filepath}")
                except Exception as e:
                    errors.append(f"Erreur chargement {model_name}: {str(e)}")
        
        return {
            'loaded_models': loaded_models,
            'errors': errors,
            'total_models': len(self.models)
        }