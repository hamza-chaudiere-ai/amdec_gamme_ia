#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package core - Logique métier principale pour AMDEC & Gamme IA

Ce package contient tous les modules de traitement des données,
génération AMDEC, gammes de maintenance et utilitaires.
"""

__version__ = "1.0.0"
__author__ = "AMDEC & Gamme IA Team"
__description__ = "Modules de logique métier pour l'assistant intelligent de maintenance"

# Imports principaux pour faciliter l'utilisation
from .excel_parser import ExcelParser
from .amdec_generator import AMDECGenerator
from .gamme_generator import GammeGenerator
from .data_trainer import DataTrainer
from .utils import (
    normalize_component_name,
    normalize_subcomponent_name,
    format_component_display,
    format_subcomponent_display,
    calculate_criticality,
    ComponentConfig
)

# Liste des exports publics
__all__ = [
    'ExcelParser',
    'AMDECGenerator', 
    'GammeGenerator',
    'DataTrainer',
    'normalize_component_name',
    'normalize_subcomponent_name',
    'format_component_display',
    'format_subcomponent_display',
    'calculate_criticality',
    'ComponentConfig'
]

# Configuration du logging pour le package
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Message d'initialisation
logger.info(f"Package core v{__version__} initialisé avec succès")