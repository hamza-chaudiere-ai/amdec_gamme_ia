#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaires communs pour AMDEC & Gamme IA
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

def create_directories():
    """Crée tous les répertoires nécessaires pour l'application"""
    directories = [
        'uploads',
        'data/dataset',
        'data/historique',
        'data/models',
        'data/generated',
        'data/generated/amdec',
        'data/generated/gammes',
        'data/templates',
        'ml/saved_models',
        'static/css',
        'static/js',
        'static/images/components'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Créer un fichier .gitkeep pour les dossiers vides
        gitkeep_path = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_path) and not os.listdir(directory):
            with open(gitkeep_path, 'w') as f:
                f.write('')
    
    logger.info("Répertoires créés avec succès")

def get_file_info(filepath: str) -> Dict:
    """
    Retourne les informations d'un fichier
    
    Args:
        filepath: Chemin vers le fichier
        
    Returns:
        Dictionnaire avec les informations du fichier
    """
    if not os.path.exists(filepath):
        return {}
    
    stat = os.stat(filepath)
    return {
        'filename': os.path.basename(filepath),
        'size': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'extension': os.path.splitext(filepath)[1].lower()
    }

def normalize_component_name(name: str) -> str:
    """
    Normalise le nom d'un composant
    
    Args:
        name: Nom du composant à normaliser
        
    Returns:
        Nom normalisé
    """
    if not name:
        return ""
    
    name = str(name).strip().lower()
    
    # Mappings des composants
    mappings = {
        'eco bt': 'economiseur_bt',
        'économiseur bt': 'economiseur_bt',
        'economiseur basse température': 'economiseur_bt',
        'eco ht': 'economiseur_ht',
        'économiseur ht': 'economiseur_ht',
        'economiseur haute température': 'economiseur_ht',
        'sur bt': 'surchauffeur_bt',
        'surchauffeur bt': 'surchauffeur_bt',
        'surchauffeur basse température': 'surchauffeur_bt',
        'sur ht': 'surchauffeur_ht',
        'surchauffeur ht': 'surchauffeur_ht',
        'surchauffeur haute température': 'surchauffeur_ht',
        'rch bt': 'rechauffeur_bt',
        'réchauffeur bt': 'rechauffeur_bt',
        'rechauffeur bt': 'rechauffeur_bt',
        'rechauffeur basse température': 'rechauffeur_bt',
        'rch ht': 'rechauffeur_ht',
        'réchauffeur ht': 'rechauffeur_ht',
        'rechauffeur ht': 'rechauffeur_ht',
        'rechauffeur haute température': 'rechauffeur_ht'
    }
    
    return mappings.get(name, name.replace(' ', '_'))

def normalize_subcomponent_name(name: str) -> str:
    """
    Normalise le nom d'un sous-composant
    
    Args:
        name: Nom du sous-composant à normaliser
        
    Returns:
        Nom normalisé
    """
    if not name:
        return ""
    
    name = str(name).strip().lower()
    
    # Mappings des sous-composants
    mappings = {
        'épingle': 'epingle',
        'epingles': 'epingle',
        'épingles': 'epingle',
        'collecteur entrée': 'collecteur_entree',
        'collecteur d\'entrée': 'collecteur_entree',
        'collecteur entree': 'collecteur_entree',
        'collecteur de sortie': 'collecteur_sortie',
        'collecteur sortie': 'collecteur_sortie',
        'tubes suspension': 'tubes_suspension',
        'tubes de suspension': 'tubes_suspension',
        'tube suspension': 'tubes_suspension',
        'tube porteur': 'tube_porteur',
        'tubes porteurs': 'tube_porteur',
        'branches entrée': 'branches_entree',
        'branches entree': 'branches_entree',
        'branches d\'entrée': 'branches_entree',
        'branches sortie': 'branches_sortie',
        'branches de sortie': 'branches_sortie'
    }
    
    return mappings.get(name, name.replace(' ', '_'))

def format_component_display(name: str) -> str:
    """
    Formate le nom d'un composant pour l'affichage
    
    Args:
        name: Nom du composant à formater
        
    Returns:
        Nom formaté pour l'affichage
    """
    mappings = {
        'economiseur_bt': 'Économiseur BT',
        'economiseur_ht': 'Économiseur HT',
        'surchauffeur_bt': 'Surchauffeur BT',
        'surchauffeur_ht': 'Surchauffeur HT',
        'rechauffeur_bt': 'Réchauffeur BT',
        'rechauffeur_ht': 'Réchauffeur HT'
    }
    
    return mappings.get(name, name.replace('_', ' ').title())

def format_subcomponent_display(name: str) -> str:
    """
    Formate le nom d'un sous-composant pour l'affichage
    
    Args:
        name: Nom du sous-composant à formater
        
    Returns:
        Nom formaté pour l'affichage
    """
    mappings = {
        'epingle': 'Épingle',
        'collecteur_entree': 'Collecteur entrée',
        'collecteur_sortie': 'Collecteur sortie',
        'tubes_suspension': 'Tubes suspension',
        'tube_porteur': 'Tube porteur',
        'branches_entree': 'Branches entrée',
        'branches_sortie': 'Branches sortie'
    }
    
    return mappings.get(name, name.replace('_', ' ').title())

def calculate_criticality(frequency: int, gravity: int, detection: int) -> int:
    """
    Calcule la criticité (F × G × D)
    
    Args:
        frequency: Fréquence (1-4)
        gravity: Gravité (1-5)
        detection: Détection (1-4)
        
    Returns:
        Criticité calculée
    """
    return frequency * gravity * detection

def get_criticality_color(criticality: int) -> str:
    """
    Retourne la couleur associée à une criticité
    
    Args:
        criticality: Valeur de criticité
        
    Returns:
        Code couleur hexadécimal
    """
    if criticality <= 12:
        return '#00FF00'  # Vert
    elif criticality <= 16:
        return '#FFFF00'  # Jaune
    elif criticality < 30:
        return '#FFA500'  # Orange
    else:
        return '#FF0000'  # Rouge

def validate_excel_structure(df) -> Tuple[bool, List[str]]:
    """
    Valide la structure d'un DataFrame Excel
    
    Args:
        df: DataFrame pandas à valider
        
    Returns:
        Tuple (is_valid, errors)
    """
    required_columns = ['composant', 'sous_composant', 'cause', 'duree']
    errors = []
    
    # Vérifier les colonnes requises
    df_columns = [col.lower().replace(' ', '_') for col in df.columns]
    missing_columns = []
    
    for req_col in required_columns:
        if req_col not in df_columns:
            # Chercher des variations
            variations = {
                'composant': ['component', 'equipement', 'équipement'],
                'sous_composant': ['sous-composant', 'subcomponent', 'sous_comp'],
                'cause': ['raison', 'motif', 'origine'],
                'duree': ['durée', 'temps', 'time', 'heures']
            }
            
            found = False
            for variation in variations.get(req_col, []):
                if variation in df_columns:
                    found = True
                    break
            
            if not found:
                missing_columns.append(req_col)
    
    if missing_columns:
        errors.append(f"Colonnes manquantes: {', '.join(missing_columns)}")
    
    # Vérifier que le DataFrame n'est pas vide
    if df.empty:
        errors.append("Le fichier Excel est vide")
    
    # Vérifier qu'il y a des données utiles
    if len(df) < 1:
        errors.append("Aucune ligne de données trouvée")
    
    return len(errors) == 0, errors

def convert_duration_to_hours(duration) -> float:
    """
    Convertit une durée en heures
    
    Args:
        duration: Durée à convertir (peut être str, int, float)
        
    Returns:
        Durée en heures
    """
    if duration is None or str(duration).strip() == '':
        return 0.0
    
    try:
        # Si c'est déjà un nombre, le retourner
        return float(duration)
    except (ValueError, TypeError):
        pass
    
    duration_str = str(duration).lower().strip()
    
    # Format "HH:MM:SS" ou "HH:MM"
    if ':' in duration_str:
        parts = duration_str.split(':')
        try:
            if len(parts) == 3:  # HH:MM:SS
                return float(parts[0]) + float(parts[1])/60 + float(parts[2])/3600
            elif len(parts) == 2:  # HH:MM
                return float(parts[0]) + float(parts[1])/60
        except ValueError:
            pass
    
    # Format "Xh Ymin"
    import re
    match = re.search(r'(\d+)h\s*(?:(\d+)m(?:in)?)?', duration_str)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2)) if match.group(2) else 0
        return hours + minutes/60
    
    # Format "X heures Y minutes"
    match = re.search(r'(\d+)\s*heure[s]?\s*(?:(\d+)\s*minute[s]?)?', duration_str)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2)) if match.group(2) else 0
        return hours + minutes/60
    
    # Si rien ne fonctionne, retourner 0
    return 0.0

def generate_timestamp() -> str:
    """
    Génère un timestamp pour les noms de fichiers
    
    Returns:
        Timestamp formaté
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_maintenance_frequency(criticality: int) -> str:
    """
    Détermine la fréquence de maintenance basée sur la criticité
    
    Args:
        criticality: Valeur de criticité
        
    Returns:
        Fréquence de maintenance recommandée
    """
    if criticality <= 12:
        return "Annuelle"
    elif criticality <= 16:
        return "Semestrielle"
    elif criticality <= 20:
        return "Trimestrielle"
    else:
        return "Mensuelle"

def safe_filename(filename: str) -> str:
    """
    Sécurise un nom de fichier en supprimant les caractères problématiques
    
    Args:
        filename: Nom de fichier à sécuriser
        
    Returns:
        Nom de fichier sécurisé
    """
    import re
    # Supprimer ou remplacer les caractères non autorisés
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'[^\w\s-.]', '', filename)
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename.strip('_')

class ComponentConfig:
    """Configuration des composants et sous-composants supportés"""
    
    COMPONENTS = {
        'economiseur_bt': {
            'name': 'Économiseur BT',
            'subcomponents': {
                'collecteur_sortie': 'Collecteur sortie',
                'epingle': 'Épingle'
            },
            'default_criticities': {
                'collecteur_sortie': 45,
                'epingle': 24
            }
        },
        'economiseur_ht': {
            'name': 'Économiseur HT',
            'subcomponents': {
                'collecteur_entree': 'Collecteur entrée',
                'tubes_suspension': 'Tubes suspension'
            },
            'default_criticities': {
                'collecteur_entree': 24,
                'tubes_suspension': 16
            }
        },
        'surchauffeur_bt': {
            'name': 'Surchauffeur BT',
            'subcomponents': {
                'epingle': 'Épingle',
                'collecteur_entree': 'Collecteur entrée'
            },
            'default_criticities': {
                'epingle': 40,
                'collecteur_entree': 24
            }
        },
        'surchauffeur_ht': {
            'name': 'Surchauffeur HT',
            'subcomponents': {
                'tube_porteur': 'Tube porteur',
                'branches_entree': 'Branches entrée',
                'collecteur_sortie': 'Collecteur sortie'
            },
            'default_criticities': {
                'tube_porteur': 30,
                'branches_entree': 24,
                'collecteur_sortie': 30
            }
        },
        'rechauffeur_bt': {
            'name': 'Réchauffeur BT',
            'subcomponents': {
                'collecteur_entree': 'Collecteur entrée',
                'tubes_suspension': 'Tubes suspension',
                'tube_porteur': 'Tube porteur'
            },
            'default_criticities': {
                'collecteur_entree': 30,
                'tubes_suspension': 24,
                'tube_porteur': 24
            }
        },
        'rechauffeur_ht': {
            'name': 'Réchauffeur HT',
            'subcomponents': {
                'branches_sortie': 'Branches sortie',
                'collecteur_entree': 'Collecteur entrée',
                'collecteur_sortie': 'Collecteur sortie'
            },
            'default_criticities': {
                'branches_sortie': 36,
                'collecteur_entree': 24,
                'collecteur_sortie': 20
            }
        }
    }
    
    @classmethod
    def get_component_list(cls) -> List[Dict]:
        """Retourne la liste des composants formatée pour l'interface"""
        return [
            {
                'id': comp_id,
                'name': comp_data['name'],
                'subcomponents': [
                    {'id': sub_id, 'name': sub_name}
                    for sub_id, sub_name in comp_data['subcomponents'].items()
                ]
            }
            for comp_id, comp_data in cls.COMPONENTS.items()
        ]
    
    @classmethod
    def get_default_criticality(cls, component: str, subcomponent: str) -> int:
        """Retourne la criticité par défaut pour un composant/sous-composant"""
        comp_data = cls.COMPONENTS.get(component, {})
        return comp_data.get('default_criticities', {}).get(subcomponent, 25)
    
    @classmethod
    def is_valid_component(cls, component: str, subcomponent: str = None) -> bool:
        """Vérifie si un composant/sous-composant est valide"""
        if component not in cls.COMPONENTS:
            return False
        
        if subcomponent is None:
            return True
        
        return subcomponent in cls.COMPONENTS[component]['subcomponents']