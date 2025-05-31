#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prédicteur intelligent pour AMDEC & Gamme IA
Orchestrateur principal pour les prédictions ML
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
import os
import joblib
from datetime import datetime

from .models import CriticalityPredictor, MaintenancePredictor, ComponentClassifier, ModelFactory

logger = logging.getLogger(__name__)

class SmartPredictor:
    """
    Prédicteur intelligent qui orchestre tous les modèles ML
    """
    
    def __init__(self, models_dir: str = 'ml/saved_models'):
        """
        Initialise le prédicteur intelligent
        
        Args:
            models_dir: Répertoire des modèles sauvegardés
        """
        self.models_dir = models_dir
        self.models = {}
        self.is_loaded = False
        
        # Créer le répertoire si nécessaire
        os.makedirs(models_dir, exist_ok=True)
        
        # Tentative de chargement des modèles existants
        self.load_models()
    
    def load_models(self) -> bool:
        """
        Charge les modèles ML sauvegardés
        
        Returns:
            True si au moins un modèle a été chargé
        """
        try:
            models_loaded = 0
            
            # Liste des modèles à charger
            model_files = {
                'criticality': 'criticality_model.pkl',
                'maintenance': 'maintenance_model.pkl',
                'classifier': 'classifier_model.pkl'
            }
            
            for model_name, filename in model_files.items():
                filepath = os.path.join(self.models_dir, filename)
                
                if os.path.exists(filepath):
                    try:
                        model = joblib.load(filepath)
                        self.models[model_name] = model
                        models_loaded += 1
                        logger.info(f"Modèle {model_name} chargé avec succès")
                    except Exception as e:
                        logger.warning(f"Erreur lors du chargement du modèle {model_name}: {e}")
            
            self.is_loaded = models_loaded > 0
            
            if self.is_loaded:
                logger.info(f"{models_loaded} modèles chargés avec succès")
            else:
                logger.info("Aucun modèle pré-entraîné trouvé. Initialisation avec modèles par défaut.")
                self._initialize_default_models()
            
            return self.is_loaded
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des modèles: {e}")
            self._initialize_default_models()
            return False
    
    def _initialize_default_models(self):
        """Initialise les modèles par défaut (non entraînés)"""
        try:
            self.models = {
                'criticality': ModelFactory.create_model('criticality'),
                'maintenance': ModelFactory.create_model('maintenance'),
                'classifier': ModelFactory.create_model('classifier')
            }
            logger.info("Modèles par défaut initialisés")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des modèles par défaut: {e}")
    
    def save_models(self) -> bool:
        """
        Sauvegarde tous les modèles entraînés
        
        Returns:
            True si la sauvegarde a réussi
        """
        try:
            saved_count = 0
            
            for model_name, model in self.models.items():
                if hasattr(model, 'is_trained') and model.is_trained:
                    filename = f"{model_name}_model.pkl"
                    filepath = os.path.join(self.models_dir, filename)
                    
                    joblib.dump(model, filepath)
                    saved_count += 1
                    logger.info(f"Modèle {model_name} sauvegardé: {filepath}")
            
            logger.info(f"{saved_count} modèles sauvegardés")
            return saved_count > 0
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des modèles: {e}")
            return False
    
    def predict_criticality(self, component: str, subcomponent: str, 
                          cause: str = None, **kwargs) -> Dict:
        """
        Prédit la criticité d'un composant
        
        Args:
            component: Nom du composant
            subcomponent: Nom du sous-composant  
            cause: Cause de défaillance (optionnel)
            **kwargs: Paramètres additionnels
            
        Returns:
            Dictionnaire avec la prédiction et métadonnées
        """
        try:
            # Préparer les données d'entrée
            input_data = pd.DataFrame([{
                'Composant': component,
                'Sous-composant': subcomponent,
                'Cause': cause or 'unknown'
            }])
            
            # Utiliser le modèle de criticité
            if 'criticality' in self.models and self.models['criticality'].is_trained:
                prediction = self.models['criticality'].predict(input_data)[0]
                confidence = self._calculate_confidence('criticality', input_data)
                method = 'ML_Model'
            else:
                # Fallback vers calcul par défaut
                prediction = self._default_criticality_calculation(component, subcomponent)
                confidence = 0.7  # Confiance moyenne pour les calculs par défaut
                method = 'Default_Rules'
            
            # Interpréter la criticité
            level, description = self._interpret_criticality(prediction)
            
            result = {
                'criticality': int(prediction),
                'level': level,
                'description': description,
                'confidence': confidence,
                'method': method,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Prédiction criticité: {component}-{subcomponent} = {prediction}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction de criticité: {e}")
            # Valeur de fallback
            return {
                'criticality': 20,
                'level': 'Moyenne',
                'description': 'Estimation par défaut',
                'confidence': 0.5,
                'method': 'Fallback',
                'error': str(e)
            }
    
    def predict_maintenance_parameters(self, component: str, subcomponent: str, 
                                     criticality: int) -> Dict:
        """
        Prédit les paramètres de maintenance
        
        Args:
            component: Nom du composant
            subcomponent: Nom du sous-composant
            criticality: Criticité calculée
            
        Returns:
            Dictionnaire avec les paramètres de maintenance
        """
        try:
            # Préparer les données d'entrée
            input_data = pd.DataFrame([{
                'Composant': component,
                'Sous-composant': subcomponent,
                'Criticité': criticality
            }])
            
            result = {}
            
            # Utiliser le modèle de maintenance si disponible
            if 'maintenance' in self.models and self.models['maintenance'].is_trained:
                predictions = self.models['maintenance'].predict(input_data)
                
                result.update({
                    'duration_minutes': predictions.get('duration', [90])[0],
                    'operations_count': predictions.get('operations', [3])[0],
                    'frequency': predictions.get('frequency', ['Trimestrielle'])[0],
                    'method': 'ML_Model'
                })
            else:
                # Calculs par défaut basés sur la criticité
                result.update(self._default_maintenance_calculation(criticality))
                result['method'] = 'Default_Rules'
            
            # Ajouter des recommandations intelligentes
            result.update(self._generate_smart_recommendations(component, subcomponent, criticality))
            
            # Métadonnées
            result.update({
                'confidence': self._calculate_confidence('maintenance', input_data),
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Prédiction maintenance: {component}-{subcomponent} (C={criticality})")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction de maintenance: {e}")
            return self._default_maintenance_calculation(criticality)
    
    def predict_failure_mode(self, component: str, subcomponent: str, 
                           symptoms: List[str] = None) -> Dict:
        """
        Prédit le mode de défaillance le plus probable
        
        Args:
            component: Nom du composant
            subcomponent: Nom du sous-composant
            symptoms: Liste des symptômes observés
            
        Returns:
            Dictionnaire avec les modes de défaillance probables
        """
        try:
            # Base de connaissances des modes de défaillance
            failure_modes_db = self._get_failure_modes_database()
            
            # Rechercher les modes pour ce composant/sous-composant
            component_modes = failure_modes_db.get(component, {}).get(subcomponent, [])
            
            if not component_modes:
                component_modes = ['Défaillance générique', 'Usure normale', 'Fatigue']
            
            # Si on a des symptômes, essayer de les corréler
            if symptoms and 'classifier' in self.models and self.models['classifier'].is_trained:
                # Utiliser le classificateur pour affiner la prédiction
                symptom_text = ' '.join(symptoms)
                input_data = pd.DataFrame([{'text': symptom_text}])
                predicted_class = self.models['classifier'].predict(input_data)[0]
                
                # Ajuster les modes selon la classification
                if predicted_class in component_modes:
                    component_modes = [predicted_class] + [m for m in component_modes if m != predicted_class]
            
            # Calculer les probabilités (simulation intelligente)
            probabilities = self._calculate_failure_probabilities(component, subcomponent, symptoms)
            
            # Combiner modes et probabilités
            modes_with_prob = []
            for i, mode in enumerate(component_modes[:3]):  # Top 3
                prob = probabilities[i] if i < len(probabilities) else 0.1
                modes_with_prob.append({
                    'mode': mode,
                    'probability': prob,
                    'symptoms_match': self._calculate_symptoms_match(mode, symptoms or [])
                })
            
            result = {
                'predicted_modes': modes_with_prob,
                'primary_mode': modes_with_prob[0]['mode'] if modes_with_prob else 'Inconnu',
                'confidence': max([m['probability'] for m in modes_with_prob]) if modes_with_prob else 0.5,
                'method': 'Knowledge_Base' + ('_ML' if symptoms else ''),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction de mode de défaillance: {e}")
            return {
                'predicted_modes': [{'mode': 'Défaillance inconnue', 'probability': 0.5, 'symptoms_match': 0.0}],
                'primary_mode': 'Défaillance inconnue',
                'confidence': 0.5,
                'method': 'Fallback',
                'error': str(e)
            }
    
    def get_intelligent_recommendations(self, component: str, subcomponent: str, 
                                      criticality: int, context: Dict = None) -> Dict:
        """
        Génère des recommandations intelligentes complètes
        
        Args:
            component: Nom du composant
            subcomponent: Nom du sous-composant
            criticality: Criticité calculée
            context: Contexte additionnel (historique, conditions, etc.)
            
        Returns:
            Recommandations complètes
        """
        try:
            # Prédictions de base
            criticality_pred = self.predict_criticality(component, subcomponent)
            maintenance_pred = self.predict_maintenance_parameters(component, subcomponent, criticality)
            failure_pred = self.predict_failure_mode(component, subcomponent)
            
            # Recommandations intelligentes selon le contexte
            recommendations = {
                'immediate_actions': self._get_immediate_actions(criticality, context),
                'preventive_measures': self._get_preventive_measures(component, subcomponent, criticality),
                'monitoring_strategy': self._get_monitoring_strategy(criticality),
                'resource_planning': self._get_resource_planning(maintenance_pred),
                'risk_assessment': self._assess_risks(criticality, failure_pred),
                'cost_optimization': self._optimize_costs(maintenance_pred, criticality)
            }
            
            # Score de priorité global
            priority_score = self._calculate_priority_score(criticality, failure_pred, context)
            
            result = {
                'predictions': {
                    'criticality': criticality_pred,
                    'maintenance': maintenance_pred,
                    'failure_modes': failure_pred
                },
                'recommendations': recommendations,
                'priority_score': priority_score,
                'next_review_date': self._calculate_next_review(criticality),
                'confidence_overall': np.mean([
                    criticality_pred.get('confidence', 0.5),
                    maintenance_pred.get('confidence', 0.5),
                    failure_pred.get('confidence', 0.5)
                ]),
                'generated_at': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations: {e}")
            return {'error': str(e), 'recommendations': {}}
    
    def _default_criticality_calculation(self, component: str, subcomponent: str) -> int:
        """Calcul de criticité par défaut basé sur l'expertise"""
        # Base de connaissances des criticités par défaut
        default_criticalities = {
            'economiseur_bt': {'epingle': 24, 'collecteur_sortie': 45},
            'economiseur_ht': {'collecteur_entree': 24, 'tubes_suspension': 16},
            'surchauffeur_bt': {'epingle': 40, 'collecteur_entree': 24},
            'surchauffeur_ht': {'tube_porteur': 30, 'branches_entree': 24, 'collecteur_sortie': 30},
            'rechauffeur_bt': {'collecteur_entree': 30, 'tubes_suspension': 24, 'tube_porteur': 24},
            'rechauffeur_ht': {'branches_sortie': 36, 'collecteur_entree': 24, 'collecteur_sortie': 20}
        }
        
        component_key = component.lower().replace(' ', '_')
        subcomp_key = subcomponent.lower().replace(' ', '_')
        
        return default_criticalities.get(component_key, {}).get(subcomp_key, 25)
    
    def _default_maintenance_calculation(self, criticality: int) -> Dict:
        """Calcul des paramètres de maintenance par défaut"""
        if criticality <= 12:
            return {
                'duration_minutes': 60,
                'operations_count': 2,
                'frequency': 'Semestrielle',
                'intervention_type': 'Maintenance corrective'
            }
        elif criticality <= 16:
            return {
                'duration_minutes': 90,
                'operations_count': 3,
                'frequency': 'Trimestrielle',
                'intervention_type': 'Maintenance préventive systématique'
            }
        elif criticality <= 20:
            return {
                'duration_minutes': 120,
                'operations_count': 4,
                'frequency': 'Mensuelle',
                'intervention_type': 'Maintenance préventive conditionnelle'
            }
        else:
            return {
                'duration_minutes': 180,
                'operations_count': 5,
                'frequency': 'Hebdomadaire',
                'intervention_type': 'Remise en cause complète'
            }
    
    def _interpret_criticality(self, criticality: int) -> Tuple[str, str]:
        """Interprète la valeur de criticité"""
        if criticality <= 12:
            return 'Négligeable', 'Maintenance corrective suffisante'
        elif criticality <= 16:
            return 'Moyenne', 'Maintenance préventive systématique recommandée'
        elif criticality <= 20:
            return 'Élevée', 'Maintenance préventive conditionnelle nécessaire'
        else:
            return 'Critique', 'Remise en cause complète de la conception requise'
    
    def _calculate_confidence(self, model_type: str, input_data: pd.DataFrame) -> float:
        """Calcule la confiance de la prédiction"""
        if model_type in self.models and hasattr(self.models[model_type], 'is_trained'):
            if self.models[model_type].is_trained:
                # Confiance basée sur les métriques du modèle
                metrics = self.models[model_type].performance_metrics
                if 'cv_score_mean' in metrics:
                    return min(metrics['cv_score_mean'], 0.95)
                elif 'accuracy' in metrics:
                    return min(metrics['accuracy'], 0.95)
                else:
                    return 0.8
            else:
                return 0.6  # Modèle non entraîné
        return 0.7  # Calcul par défaut
    
    def _get_failure_modes_database(self) -> Dict:
        """Base de connaissances des modes de défaillance"""
        return {
            'economiseur_bt': {
                'epingle': ['Corrosion externe', 'Érosion par cendres', 'Encrassement interne'],
                'collecteur_sortie': ['Caustic attack', 'Fissuration contrainte', 'Fatigue thermique']
            },
            'economiseur_ht': {
                'collecteur_entree': ['Érosion par cendres', 'Corrosion externe', 'Déformation thermique'],
                'tubes_suspension': ['Fatigue mécanique', 'Vibration excessive', 'Corrosion supports']
            },
            'surchauffeur_bt': {
                'epingle': ['Short-term overheat', 'Corrosion côté feu', 'Graphitization'],
                'collecteur_entree': ['Corrosion interne', 'Érosion interne', 'Fissuration']
            },
            'surchauffeur_ht': {
                'tube_porteur': ['Long-term overheat', 'Rupture fluage', 'Corrosion haute température'],
                'branches_entree': ['Fireside corrosion', 'Fatigue thermique', 'Érosion externe'],
                'collecteur_sortie': ['SCC (Stress Corrosion Cracking)', 'Fatigue contrainte', 'Corrosion interfaces']
            },
            'rechauffeur_bt': {
                'collecteur_entree': ['Hydrogen damage', 'Microfissures', 'Dépôts internes'],
                'tubes_suspension': ['Fatigue thermique', 'Vibration supports', 'Corrosion supports'],
                'tube_porteur': ['Fatigue cyclique', 'Contraintes thermiques', 'Corrosion supports']
            },
            'rechauffeur_ht': {
                'branches_sortie': ['Acid attack', 'Érosion acide', 'Dépôts acides'],
                'collecteur_entree': ['Waterside corrosion', 'Dépôts internes', 'Fissures internes'],
                'collecteur_sortie': ['Dissimilar metal weld', 'Contraintes interfaces', 'Corrosion soudures']
            }
        }
    
    def _calculate_failure_probabilities(self, component: str, subcomponent: str, 
                                       symptoms: List[str] = None) -> List[float]:
        """Calcule les probabilités des modes de défaillance"""
        # Probabilités de base selon l'expertise
        base_probs = [0.6, 0.3, 0.1]  # Mode principal, secondaire, tertiaire
        
        # Ajustement selon les symptômes
        if symptoms:
            # Mots-clés indicateurs
            indicators = {
                'corrosion': ['rouille', 'oxydation', 'corrosion', 'attaque'],
                'fatigue': ['fissure', 'crack', 'fatigue', 'cycles'],
                'surchauffe': ['température', 'chaud', 'surchauffe', 'thermique'],
                'erosion': ['usure', 'érosion', 'particules', 'abrasion']
            }
            
            # Ajuster les probabilités selon les correspondances
            for i, prob in enumerate(base_probs):
                match_score = 0
                symptom_text = ' '.join(symptoms).lower()
                
                for category, keywords in indicators.items():
                    if any(keyword in symptom_text for keyword in keywords):
                        match_score += 0.1
                
                base_probs[i] = min(prob + match_score, 0.95)
        
        # Normaliser pour que la somme soit <= 1
        total = sum(base_probs)
        if total > 1:
            base_probs = [p/total for p in base_probs]
        
        return base_probs
    
    def _calculate_symptoms_match(self, mode: str, symptoms: List[str]) -> float:
        """Calcule la correspondance entre un mode et des symptômes"""
        if not symptoms:
            return 0.0
        
        mode_lower = mode.lower()
        symptoms_text = ' '.join(symptoms).lower()
        
        # Mots-clés par mode de défaillance
        mode_keywords = {
            'corrosion': ['corrosion', 'rouille', 'oxydation'],
            'fatigue': ['fissure', 'fatigue', 'cycles'],
            'surchauffe': ['température', 'chaud', 'thermique'],
            'erosion': ['usure', 'érosion', 'particules']
        }
        
        # Rechercher les correspondances
        matches = 0
        total_keywords = 0
        
        for category, keywords in mode_keywords.items():
            if category in mode_lower:
                total_keywords = len(keywords)
                for keyword in keywords:
                    if keyword in symptoms_text:
                        matches += 1
                break
        
        return matches / total_keywords if total_keywords > 0 else 0.0
    
    def _generate_smart_recommendations(self, component: str, subcomponent: str, 
                                      criticality: int) -> Dict:
        """Génère des recommandations intelligentes"""
        recommendations = {
            'materials_needed': self._get_recommended_materials(component, subcomponent, criticality),
            'personnel_required': self._get_required_personnel(criticality),
            'safety_measures': self._get_safety_measures(component, criticality),
            'estimated_cost': self._estimate_cost(criticality)
        }
        
        return recommendations
    
    def _get_recommended_materials(self, component: str, subcomponent: str, criticality: int) -> List[str]:
        """Recommande les matériels nécessaires"""
        base_materials = ['Lampe torche', 'Appareil photo', 'EPI']
        
        if criticality > 12:
            base_materials.extend(['Appareil ultrasons', 'Gel de contact'])
        
        if criticality > 16:
            base_materials.extend(['Kit test étanchéité', 'Brosse métallique'])
        
        if criticality > 20:
            base_materials.extend(['Caméra thermique', 'Équipement soudage'])
        
        # Matériels spécifiques selon le composant
        if 'surchauffeur' in component:
            base_materials.append('Capteurs température')
        if 'rechauffeur' in component and 'ht' in component:
            base_materials.append('Protection chimique')
        
        return base_materials
    
    def _get_required_personnel(self, criticality: int) -> List[str]:
        """Détermine le personnel requis"""
        if criticality <= 12:
            return ['Opérateur qualifié']
        elif criticality <= 16:
            return ['Technicien', 'Opérateur']
        elif criticality <= 20:
            return ['Technicien qualifié', 'Assistant', 'Superviseur']
        else:
            return ['Ingénieur expert', 'Technicien spécialisé', 'Équipe maintenance', 'Superviseur sécurité']
    
    def _get_safety_measures(self, component: str, criticality: int) -> List[str]:
        """Définit les mesures de sécurité"""
        safety = ['EPI obligatoires', 'Consignation électrique']
        
        if criticality > 16:
            safety.extend(['Consignation mécanique', 'Ventilation zone', 'Signalisation'])
        
        if 'surchauffeur' in component:
            safety.append('Protection thermique')
        
        if 'rechauffeur_ht' in component:
            safety.extend(['Protection chimique', 'Neutralisation vapeurs'])
        
        return safety
    
    def _estimate_cost(self, criticality: int) -> Dict:
        """Estime les coûts de maintenance"""
        base_cost = 500  # Coût de base en euros
        
        # Facteur multiplicateur selon la criticité
        if criticality <= 12:
            factor = 1.0
        elif criticality <= 16:
            factor = 1.5
        elif criticality <= 20:
            factor = 2.0
        else:
            factor = 3.0
        
        estimated_cost = int(base_cost * factor)
        
        return {
            'estimated_cost_eur': estimated_cost,
            'cost_breakdown': {
                'personnel': int(estimated_cost * 0.6),
                'materials': int(estimated_cost * 0.25),
                'equipment': int(estimated_cost * 0.15)
            },
            'uncertainty_range': f"±{int(estimated_cost * 0.2)}"
        }
    
    def _get_immediate_actions(self, criticality: int, context: Dict = None) -> List[str]:
        """Actions immédiates selon la criticité"""
        if criticality <= 12:
            return ['Planifier inspection routine', 'Documenter état actuel']
        elif criticality <= 16:
            return ['Programmer maintenance préventive', 'Surveillance renforcée', 'Préparation matériel']
        elif criticality <= 20:
            return ['Intervention prioritaire', 'Mobilisation équipe', 'Analyse risques', 'Plan d\'urgence']
        else:
            return ['ALERTE CRITIQUE', 'Arrêt immédiat si nécessaire', 'Mobilisation urgente', 'Expertise externe', 'Plan de contingence']
    
    def _get_preventive_measures(self, component: str, subcomponent: str, criticality: int) -> List[str]:
        """Mesures préventives recommandées"""
        measures = []
        
        # Mesures générales
        if criticality > 12:
            measures.extend(['Surveillance périodique', 'Contrôles réguliers'])
        
        # Mesures spécifiques par composant
        if 'economiseur' in component:
            measures.append('Contrôle qualité eau')
        elif 'surchauffeur' in component:
            measures.extend(['Surveillance température', 'Optimisation combustion'])
        elif 'rechauffeur' in component:
            measures.append('Analyse chimique régulière')
        
        return measures
    
    def _get_monitoring_strategy(self, criticality: int) -> Dict:
        """Stratégie de monitoring"""
        if criticality <= 12:
            return {'frequency': 'Semestrielle', 'type': 'Inspection visuelle', 'automation': 'Manuelle'}
        elif criticality <= 16:
            return {'frequency': 'Trimestrielle', 'type': 'Contrôles CND', 'automation': 'Semi-automatique'}
        elif criticality <= 20:
            return {'frequency': 'Mensuelle', 'type': 'Surveillance continue', 'automation': 'Automatique'}
        else:
            return {'frequency': 'Continue', 'type': 'Monitoring temps réel', 'automation': 'IoT + IA'}
    
    def _get_resource_planning(self, maintenance_pred: Dict) -> Dict:
        """Planification des ressources"""
        duration = maintenance_pred.get('duration_minutes', 90)
        operations = maintenance_pred.get('operations_count', 3)
        
        return {
            'planning_horizon': '2-4 semaines',
            'resource_allocation': {
                'time_slots': f"{duration} minutes",
                'team_size': min(operations, 4),
                'equipment_booking': '1 semaine avant'
            },
            'dependencies': ['Disponibilité équipe', 'Matériel en stock', 'Conditions météo']
        }
    
    def _assess_risks(self, criticality: int, failure_pred: Dict) -> Dict:
        """Évaluation des risques"""
        risk_level = 'Faible' if criticality <= 12 else 'Moyen' if criticality <= 20 else 'Élevé'
        
        return {
            'risk_level': risk_level,
            'failure_probability': failure_pred.get('confidence', 0.5),
            'impact_assessment': 'Production' if criticality > 20 else 'Performance',
            'mitigation_priority': 'Haute' if criticality > 20 else 'Moyenne'
        }
    
    def _optimize_costs(self, maintenance_pred: Dict, criticality: int) -> Dict:
        """Optimisation des coûts"""
        frequency = maintenance_pred.get('frequency', 'Trimestrielle')
        
        return {
            'cost_strategy': 'Préventif' if criticality > 16 else 'Correctif',
            'frequency_optimization': frequency,
            'bulk_planning': 'Oui' if criticality <= 16 else 'Non',
            'resource_sharing': 'Possible' if criticality <= 12 else 'Non recommandé'
        }
    
    def _calculate_priority_score(self, criticality: int, failure_pred: Dict, context: Dict = None) -> float:
        """Calcule un score de priorité global"""
        base_score = criticality / 100.0  # Normaliser 0-1
        
        # Ajustement selon la confiance de prédiction
        confidence_factor = failure_pred.get('confidence', 0.5)
        
        # Ajustement selon le contexte
        context_factor = 1.0
        if context:
            # Facteurs contextuels (âge équipement, historique, etc.)
            if context.get('age_years', 0) > 10:
                context_factor += 0.1
            if context.get('recent_failures', 0) > 2:
                context_factor += 0.2
        
        priority_score = min(base_score * confidence_factor * context_factor, 1.0)
        
        return round(priority_score, 2)
    
    def _calculate_next_review(self, criticality: int) -> str:
        """Calcule la prochaine date de révision"""
        from datetime import timedelta
        
        if criticality <= 12:
            days = 180  # 6 mois
        elif criticality <= 16:
            days = 90   # 3 mois
        elif criticality <= 20:
            days = 30   # 1 mois
        else:
            days = 7    # 1 semaine
        
        next_date = datetime.now() + timedelta(days=days)
        return next_date.strftime('%Y-%m-%d')
    
    def get_model_info(self) -> Dict:
        """Retourne les informations sur les modèles chargés"""
        info = {
            'models_loaded': list(self.models.keys()),
            'models_trained': [],
            'performance_metrics': {},
            'last_updated': datetime.now().isoformat()
        }
        
        for name, model in self.models.items():
            if hasattr(model, 'is_trained') and model.is_trained:
                info['models_trained'].append(name)
                info['performance_metrics'][name] = getattr(model, 'performance_metrics', {})
        
        return info