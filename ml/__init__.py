#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package ml - Modules de Machine Learning pour AMDEC & Gamme IA

Ce package contient les modèles d'intelligence artificielle,
les prédicteurs et les modules d'entraînement.
"""

__version__ = "1.0.0"
__author__ = "AMDEC & Gamme IA Team"
__description__ = "Modules de Machine Learning pour prédictions intelligentes"

# Imports principaux
try:
    from .models import (
        CriticalityPredictor,
        MaintenancePredictor,
        ComponentClassifier
    )
    from .predictor import SmartPredictor
    from .trainer import MLTrainer
    
    # Liste des exports publics
    __all__ = [
        'CriticalityPredictor',
        'MaintenancePredictor', 
        'ComponentClassifier',
        'SmartPredictor',
        'MLTrainer'
    ]
    
except ImportError as e:
    # Gérer gracieusement les imports manquants
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Certains modules ML non disponibles: {e}")
    
    __all__ = []

# Configuration
ML_CONFIG = {
    'models_directory': 'ml/saved_models',
    'default_algorithm': 'RandomForest',
    'cross_validation_folds': 5,
    'test_size': 0.2,
    'random_state': 42
}

# Vérification des dépendances ML
def check_ml_dependencies():
    """Vérifie que les dépendances ML sont disponibles"""
    try:
        import sklearn
        import numpy
        import pandas
        return True
    except ImportError:
        return False

# Initialisation
import logging
logger = logging.getLogger(__name__)

if check_ml_dependencies():
    logger.info(f"Package ml v{__version__} initialisé avec succès")
else:
    logger.warning("Dépendances ML manquantes. Certaines fonctionnalités ne seront pas disponibles.")