#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur UNIVERSEL de fichiers Excel pour historiques d'arrêts
✅ COMPATIBLE avec n'importe quelle structure Excel
✅ DÉTECTION AUTOMATIQUE des colonnes clés
✅ NETTOYAGE et VALIDATION robustes
✅ PRÉPARATION pour regroupement par composant+sous-composant uniquement
"""

import pandas as pd
import numpy as np
import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta

from .utils import (
    normalize_component_name, 
    normalize_subcomponent_name,
    convert_duration_to_hours,
    validate_excel_structure
)

logger = logging.getLogger(__name__)

class ExcelParser:
    """
    ✅ ANALYSEUR UNIVERSEL - Compatible avec n'importe quel fichier Excel historique
    
    Fonctionnalités :
    - Détection automatique des colonnes (composant, sous-composant, cause, durée, date)
    - Nettoyage et validation robustes
    - Normalisation des formats
    - Préparation optimale pour regroupement intelligent
    """
    
    def __init__(self, file_path: str):
        """
        Initialise l'analyseur universel
        
        Args:
            file_path: Chemin vers le fichier Excel à analyser
        """
        self.file_path = file_path
        self.raw_data = None
        self.processed_data = None
        self.column_mappings = {}
        self.detection_report = {}
        self.stats = {}
        
        # Patterns de détection automatique des colonnes
        self.column_patterns = self._build_column_detection_patterns()
        
        # Vérifications initiales
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Fichier non trouvé: {file_path}")
        
        if not file_path.lower().endswith(('.xlsx', '.xls')):
            raise ValueError("❌ Le fichier doit être au format Excel (.xlsx ou .xls)")
    
    def _build_column_detection_patterns(self) -> Dict[str, List[str]]:
        """
        ✅ PATTERNS UNIVERSELS de détection automatique des colonnes
        
        Returns:
            Dictionnaire des patterns de reconnaissance
        """
        return {
            'composant': [
                'composant', 'component', 'equipment', 'equipement', 'appareil', 'asset',
                'system', 'systeme', 'machine', 'installation', 'materiel', 'element',
                'unite', 'unit', 'device', 'dispositif', 'partie', 'section', 'module',
                'assemblage', 'chaudiere', 'boiler', 'echangeur', 'eco', 'surch', 'rech'
            ],
            'sous_composant': [
                'sous_composant', 'sous-composant', 'souscomposant', 'subcomponent', 
                'sub_component', 'sub-component', 'piece', 'partie', 'element',
                'sous_element', 'sous-element', 'detail', 'organe', 'membre',
                'subdivision', 'fragment', 'segment', 'subassembly', 'epingle',
                'collecteur', 'tube', 'branche', 'branches', 'support'
            ],
            'cause': [
                'cause', 'raison', 'motif', 'origine', 'source', 'reason', 'root_cause',
                'failure_cause', 'cause_defaillance', 'cause_panne', 'probleme',
                'problem', 'defaut', 'defect', 'anomalie', 'anomaly', 'incident_type',
                'failure_type', 'defaillance', 'panne', 'dysfonctionnement'
            ],
            'date_arret': [
                'date_arret', 'date_arrêt', 'date_arret', 'date_panne', 'date_incident',
                'date_failure', 'failure_date', 'incident_date', 'arret_date',
                'shutdown_date', 'down_date', 'date_event', 'event_date', 'date',
                'timestamp', 'datetime', 'occurrence_date', 'fault_date', 'when'
            ],
            'duree': [
                'duree', 'durée', 'duration', 'temps', 'time', 'heures', 'hours',
                'minutes', 'jours', 'days', 'downtime', 'arret_duration',
                'shutdown_time', 'repair_time', 'temps_arret', 'temps_reparation',
                'indisponibilite', 'unavailability', 'outage_duration', 'hours_down'
            ],
            'description': [
                'description', 'detail', 'details', 'observation', 'observations',
                'comment', 'commentaire', 'remarque', 'notes', 'info', 'information'
            ]
        }
    
    def parse(self) -> pd.DataFrame:
        """
        ✅ PARSING UNIVERSEL du fichier Excel
        
        Returns:
            DataFrame pandas normalisé et prêt pour regroupement
        """
        try:
            logger.info(f"🔄 Analyse UNIVERSELLE du fichier: {os.path.basename(self.file_path)}")
            
            # 1. Lecture robuste du fichier Excel
            self._read_excel_file_ROBUST()
            
            # 2. Détection automatique des colonnes clés
            self._detect_columns_automatically()
            
            # 3. Validation et nettoyage des données
            self._validate_and_clean_data()
            
            # 4. Normalisation des formats
            self._normalize_data_formats()
            
            # 5. Préparation pour regroupement par composant+sous-composant
            self._prepare_for_component_grouping()
            
            # 6. Calcul des statistiques
            self._calculate_comprehensive_statistics()
            
            logger.info(f"✅ Analyse UNIVERSELLE terminée: {len(self.processed_data)} lignes validées")
            return self.processed_data
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse UNIVERSELLE: {e}")
            raise
    
    def _read_excel_file_ROBUST(self):
        """
        ✅ LECTURE ROBUSTE compatible avec tous formats Excel
        """
        logger.info("📖 Lecture robuste du fichier Excel...")
        
        # Stratégies de lecture multiples
        read_strategies = [
            # Lecture standard
            {'header': 0},
            # Au cas où première ligne = titre/métadonnées
            {'header': 1},
            # Ignorer la première ligne complètement
            {'header': 0, 'skiprows': 1},
            # Lecture sans en-tête puis auto-détection
            {'header': None},
            # Lecture de plusieurs feuilles si nécessaire
            {'header': 0, 'sheet_name': None}
        ]
        
        for i, strategy in enumerate(read_strategies):
            try:
                logger.debug(f"Tentative lecture {i+1}: {strategy}")
                
                if 'sheet_name' in strategy and strategy['sheet_name'] is None:
                    # Lire toutes les feuilles
                    excel_data = pd.read_excel(self.file_path, **strategy)
                    
                    # Prendre la feuille avec le plus de données
                    if isinstance(excel_data, dict):
                        best_sheet = max(excel_data.keys(), 
                                       key=lambda k: len(excel_data[k]) if not excel_data[k].empty else 0)
                        df = excel_data[best_sheet]
                        logger.info(f"📊 Feuille sélectionnée: '{best_sheet}'")
                    else:
                        df = excel_data
                else:
                    df = pd.read_excel(self.file_path, **strategy)
                
                # Valider que nous avons des données utilisables
                if not df.empty and len(df.columns) >= 3:
                    # Nettoyer les colonnes vides/inutiles
                    df = df.dropna(axis=1, how='all')  # Supprimer colonnes vides
                    df = df.dropna(how='all')  # Supprimer lignes vides
                    
                    if len(df) >= 2:  # Au moins 2 lignes de données
                        self.raw_data = df
                        logger.info(f"✅ Lecture réussie: {len(df)} lignes, {len(df.columns)} colonnes")
                        logger.info(f"📋 Colonnes détectées: {list(df.columns)}")
                        return
                
            except Exception as e:
                logger.debug(f"❌ Stratégie {i+1} échouée: {e}")
                continue
        
        raise ValueError("❌ Impossible de lire le fichier Excel avec toutes les stratégies testées")
    
    def _detect_columns_automatically(self):
        """
        ✅ DÉTECTION AUTOMATIQUE UNIVERSELLE des colonnes clés
        """
        logger.info("🔍 Détection automatique des colonnes...")
        
        df_columns = [str(col).lower().strip() for col in self.raw_data.columns]
        column_mapping = {}
        detection_scores = {}
        
        # Pour chaque type de colonne requis
        for target_col, patterns in self.column_patterns.items():
            best_match = None
            best_score = 0
            
            # Tester chaque colonne du DataFrame
            for i, df_col in enumerate(df_columns):
                score = 0
                
                # Calcul du score de correspondance
                for pattern in patterns:
                    pattern_clean = pattern.lower().strip()
                    
                    if pattern_clean == df_col:
                        score += 100  # Correspondance exacte
                    elif df_col.startswith(pattern_clean):
                        score += 80   # Début correspond
                    elif df_col.endswith(pattern_clean):
                        score += 70   # Fin correspond
                    elif pattern_clean in df_col:
                        score += 50   # Contient le pattern
                    elif any(part in df_col for part in pattern_clean.split('_')):
                        score += 30   # Correspondance partielle
                
                # Bonus pour les mots-clés multiples
                word_matches = sum(1 for p in patterns if p.lower() in df_col)
                score += word_matches * 10
                
                # Garder le meilleur score
                if score > best_score:
                    best_score = score
                    best_match = self.raw_data.columns[i]  # Nom original de la colonne
            
            # Seuil minimum de confiance
            if best_score >= 40:
                column_mapping[target_col] = best_match
                detection_scores[target_col] = best_score
                logger.info(f"✅ {target_col}: '{best_match}' (score: {best_score})")
            else:
                logger.warning(f"⚠️ {target_col}: non détecté (meilleur score: {best_score})")
        
        # Validation des colonnes essentielles
        required_columns = ['composant', 'sous_composant']
        missing_required = [col for col in required_columns if col not in column_mapping]
        
        if missing_required:
            logger.warning(f"⚠️ Colonnes essentielles manquantes: {missing_required}")
            # Tentative de détection alternative basée sur le contenu
            column_mapping = self._fallback_content_detection(missing_required, column_mapping)
        
        # Stocker les résultats
        self.column_mappings = column_mapping
        self.detection_report = {
            'detected': column_mapping,
            'scores': detection_scores,
            'missing': missing_required,
            'available_columns': list(self.raw_data.columns)
        }
        
        logger.info(f"📊 Détection terminée: {len(column_mapping)} colonnes mappées")
        return column_mapping
    
    def _fallback_content_detection(self, missing_columns: List[str], current_mapping: Dict[str, str]) -> Dict[str, str]:
        """
        ✅ DÉTECTION DE SECOURS basée sur l'analyse du contenu
        
        Args:
            missing_columns: Colonnes manquantes à détecter
            current_mapping: Mapping déjà trouvé
            
        Returns:
            Mapping complété
        """
        logger.info("🔍 Détection de secours basée sur le contenu...")
        
        for missing_col in missing_columns:
            best_candidate = None
            best_content_score = 0
            
            # Analyser le contenu de chaque colonne non mappée
            for col in self.raw_data.columns:
                if col in current_mapping.values():
                    continue
                
                # Analyser les valeurs uniques de cette colonne
                unique_vals = self.raw_data[col].dropna().astype(str).str.lower().unique()[:50]  # Limiter pour performance
                content_score = 0
                
                if missing_col == 'composant':
                    # Chercher des mots-clés typiques de composants
                    component_keywords = [
                        'eco', 'surch', 'rech', 'economiseur', 'surchauffeur', 'rechauffeur',
                        'chaudiere', 'echangeur', 'tube', 'collecteur', 'boiler', 'heater'
                    ]
                    for val in unique_vals:
                        for kw in component_keywords:
                            if kw in val:
                                content_score += 10
                
                elif missing_col == 'sous_composant':
                    # Chercher des mots-clés typiques de sous-composants
                    subcomp_keywords = [
                        'epingle', 'collecteur', 'tube', 'branche', 'branches', 'support',
                        'entree', 'sortie', 'suspension', 'porteur'
                    ]
                    for val in unique_vals:
                        for kw in subcomp_keywords:
                            if kw in val:
                                content_score += 10
                
                elif missing_col == 'cause':
                    # Chercher des mots-clés typiques de causes
                    cause_keywords = [
                        'corrosion', 'fissure', 'fatigue', 'erosion', 'surchauffe',
                        'fuite', 'usure', 'panne', 'defaillance'
                    ]
                    for val in unique_vals:
                        for kw in cause_keywords:
                            if kw in val:
                                content_score += 10
                
                elif missing_col == 'duree':
                    # Chercher des valeurs numériques raisonnables pour des durées
                    numeric_vals = []
                    for val in unique_vals:
                        try:
                            num_val = float(re.sub(r'[^\d.,]', '', str(val)).replace(',', '.'))
                            if 0.1 <= num_val <= 1000:  # Durées raisonnables en heures
                                numeric_vals.append(num_val)
                        except:
                            continue
                    
                    if len(numeric_vals) >= len(unique_vals) * 0.5:  # Au moins 50% de valeurs numériques
                        content_score += 50
                
                # Garder le meilleur candidat
                if content_score > best_content_score:
                    best_content_score = content_score
                    best_candidate = col
            
            # Ajouter si score suffisant
            if best_candidate and best_content_score >= 20:
                current_mapping[missing_col] = best_candidate
                logger.info(f"✅ Détection contenu: {missing_col} -> '{best_candidate}' (score: {best_content_score})")
        
        return current_mapping
    
    def _validate_and_clean_data(self):
        """
        ✅ VALIDATION et NETTOYAGE ROBUSTE des données
        """
        logger.info("🧹 Validation et nettoyage des données...")
        
        # Créer un DataFrame de travail avec les colonnes mappées
        work_data = pd.DataFrame()
        
        # Mapper les colonnes détectées vers les noms standards
        for standard_name, original_name in self.column_mappings.items():
            if original_name in self.raw_data.columns:
                work_data[standard_name] = self.raw_data[original_name].copy()
        
        initial_rows = len(work_data)
        logger.info(f"📊 Données initiales: {initial_rows} lignes")
        
        # ✅ NETTOYAGE 1: Supprimer les lignes complètement vides
        work_data = work_data.dropna(how='all')
        logger.info(f"📊 Après suppression lignes vides: {len(work_data)} lignes")
        
        # ✅ NETTOYAGE 2: Nettoyer les colonnes textuelles
        text_columns = ['composant', 'sous_composant', 'cause', 'description']
        for col in text_columns:
            if col in work_data.columns:
                # Nettoyer et normaliser
                work_data[col] = work_data[col].astype(str).str.strip()
                work_data[col] = work_data[col].str.replace(r'\s+', ' ', regex=True)  # Espaces multiples
                work_data[col] = work_data[col].replace(['nan', 'NaN', 'null', 'NULL', ''], np.nan)
                work_data[col] = work_data[col].fillna('non_specifie')
        
        # ✅ NETTOYAGE 3: Nettoyer et valider les dates
        if 'date_arret' in work_data.columns:
            work_data['date_arret'] = self._clean_and_validate_dates(work_data['date_arret'])
        
        # ✅ NETTOYAGE 4: Nettoyer et valider les durées
        if 'duree' in work_data.columns:
            work_data['duree'] = self._clean_and_validate_durations(work_data['duree'])
        else:
            # Si pas de durée, assigner une durée par défaut basée sur le type
            work_data['duree'] = 1.0  # 1 heure par défaut
        
        # ✅ NETTOYAGE 5: Supprimer les lignes avec des données essentielles manquantes
        essential_cols = ['composant', 'sous_composant']
        available_essential = [col for col in essential_cols if col in work_data.columns]
        
        if available_essential:
            mask_valid = work_data[available_essential].notna().all(axis=1)
            work_data = work_data[mask_valid]
        
        # ✅ NETTOYAGE 6: Filtrer les valeurs non significatives
        if 'composant' in work_data.columns:
            work_data = work_data[~work_data['composant'].isin(['non_specifie', 'inconnu', 'n/a', 'na'])]
        if 'sous_composant' in work_data.columns:
            work_data = work_data[~work_data['sous_composant'].isin(['non_specifie', 'inconnu', 'n/a', 'na'])]
        
        final_rows = len(work_data)
        cleaned_rows = initial_rows - final_rows
        
        logger.info(f"📊 Nettoyage terminé: {final_rows} lignes valides ({cleaned_rows} supprimées)")
        
        self.processed_data = work_data
    
    def _clean_and_validate_dates(self, date_series: pd.Series) -> pd.Series:
        """
        ✅ NETTOYAGE ROBUSTE des dates
        
        Args:
            date_series: Série de dates à nettoyer
            
        Returns:
            Série de dates validées
        """
        logger.info("📅 Nettoyage des dates...")
        
        cleaned_dates = pd.Series(index=date_series.index, dtype='datetime64[ns]')
        
        for idx, date_val in date_series.items():
            try:
                if pd.isna(date_val) or str(date_val).strip() in ['', 'nan', 'NaN']:
                    continue
                
                # Convertir en string pour traitement
                date_str = str(date_val).strip()
                
                # Formats de date supportés
                date_formats = [
                    '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y',
                    '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S',
                    '%Y/%m/%d', '%d.%m.%Y', '%Y.%m.%d',
                    '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M'
                ]
                
                parsed_date = None
                
                # Essayer pandas to_datetime en premier (plus robuste)
                try:
                    parsed_date = pd.to_datetime(date_str, errors='raise')
                except:
                    # Essayer les formats manuellement
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            break
                        except:
                            continue
                
                # Validation de la date (entre 1990 et aujourd'hui + 1 an)
                if parsed_date:
                    min_date = datetime(1990, 1, 1)
                    max_date = datetime.now() + timedelta(days=365)
                    
                    if min_date <= parsed_date <= max_date:
                        cleaned_dates.iloc[idx] = parsed_date
                
            except Exception as e:
                logger.debug(f"Erreur parsing date '{date_val}': {e}")
                continue
        
        valid_dates = cleaned_dates.notna().sum()
        total_dates = len(date_series)
        logger.info(f"📅 Dates validées: {valid_dates}/{total_dates}")
        
        return cleaned_dates
    
    def _clean_and_validate_durations(self, duration_series: pd.Series) -> pd.Series:
        """
        ✅ NETTOYAGE ROBUSTE des durées
        
        Args:
            duration_series: Série de durées à nettoyer
            
        Returns:
            Série de durées en heures
        """
        logger.info("⏱️ Nettoyage des durées...")
        
        cleaned_durations = pd.Series(index=duration_series.index, dtype='float64')
        
        for idx, duration_val in duration_series.items():
            try:
                if pd.isna(duration_val):
                    cleaned_durations.iloc[idx] = 1.0  # Durée par défaut
                    continue
                
                # Utiliser la fonction utilitaire existante
                duration_hours = convert_duration_to_hours(duration_val)
                
                # Validation de la durée (entre 1 minute et 7 jours)
                if 0.017 <= duration_hours <= 168:  # 1 min à 7 jours
                    cleaned_durations.iloc[idx] = duration_hours
                else:
                    cleaned_durations.iloc[idx] = 1.0  # Valeur par défaut
                
            except Exception as e:
                logger.debug(f"Erreur parsing durée '{duration_val}': {e}")
                cleaned_durations.iloc[idx] = 1.0  # Valeur par défaut
        
        valid_durations = (cleaned_durations > 0).sum()
        total_durations = len(duration_series)
        logger.info(f"⏱️ Durées validées: {valid_durations}/{total_durations}")
        
        return cleaned_durations
    
    def _normalize_data_formats(self):
        """
        ✅ NORMALISATION des formats de données
        """
        logger.info("🔧 Normalisation des formats...")
        
        if self.processed_data is None or self.processed_data.empty:
            return
        
        # Normaliser les noms de composants et sous-composants
        if 'composant' in self.processed_data.columns:
            self.processed_data['composant'] = self.processed_data['composant'].apply(normalize_component_name)
        
        if 'sous_composant' in self.processed_data.columns:
            self.processed_data['sous_composant'] = self.processed_data['sous_composant'].apply(normalize_subcomponent_name)
        
        # Normaliser les causes
        if 'cause' in self.processed_data.columns:
            self.processed_data['cause'] = self.processed_data['cause'].apply(self._normalize_cause)
        
        logger.info("✅ Normalisation terminée")
    
    def _normalize_cause(self, cause_value) -> str:
        """
        ✅ NORMALISATION des causes
        
        Args:
            cause_value: Valeur de cause à normaliser
            
        Returns:
            Cause normalisée
        """
        if pd.isna(cause_value) or str(cause_value).strip() == '':
            return 'non_specifie'
        
        cause = str(cause_value).lower().strip()
        
        # Mappings des causes courantes
        cause_mappings = {
            'corrosion': ['corrosion', 'rouille', 'oxydation', 'attaque_chimique', 'oxidation'],
            'fissure': ['fissure', 'fissuration', 'craquelure', 'fente', 'crack', 'cassure'],
            'erosion': ['erosion', 'érosion', 'usure', 'abrasion', 'wear', 'abrasive'],
            'fatigue': ['fatigue', 'stress', 'tension', 'contrainte', 'cyclique'],
            'percement': ['percement', 'perforation', 'trou', 'perce', 'hole'],
            'surchauffe': ['surchauffe', 'temperature_elevee', 'chaleur_excessive', 'overheat', 'thermique'],
            'encrassement': ['encrassement', 'depot', 'accumulation', 'obstruction', 'bouchage', 'fouling'],
            'vibration': ['vibration', 'oscillation', 'tremblements', 'vibratoire'],
            'fuite': ['fuite', 'ecoulement', 'perte', 'suintement', 'leak', 'leakage']
        }
        
        for standard_cause, variations in cause_mappings.items():
            if any(var in cause for var in variations):
                return standard_cause
        
        return cause
    
    def _prepare_for_component_grouping(self):
        """
        ✅ PRÉPARATION SPÉCIALE pour regroupement par composant+sous-composant
        
        Ajoute les colonnes nécessaires pour le regroupement intelligent
        """
        logger.info("🔄 Préparation pour regroupement par composant+sous-composant...")
        
        if self.processed_data is None or self.processed_data.empty:
            return
        
        # Créer des clés de regroupement normalisées
        self.processed_data['grouping_key'] = (
            self.processed_data.get('composant', 'inconnu').astype(str) + 
            '__' + 
            self.processed_data.get('sous_composant', 'inconnu').astype(str)
        )
        
        # Ajouter un ID unique pour chaque ligne (pour traçabilité)
        self.processed_data['line_id'] = range(1, len(self.processed_data) + 1)
        
        # S'assurer que toutes les colonnes nécessaires existent
        required_columns = ['composant', 'sous_composant', 'cause', 'duree']
        for col in required_columns:
            if col not in self.processed_data.columns:
                if col == 'duree':
                    self.processed_data[col] = 1.0
                else:
                    self.processed_data[col] = 'non_specifie'
        
        logger.info(f"✅ Préparation terminée: {len(self.processed_data)} lignes prêtes pour regroupement")
    
    def _calculate_comprehensive_statistics(self):
        """
        ✅ CALCUL de statistiques complètes
        """
        if self.processed_data is None or self.processed_data.empty:
            self.stats = {}
            return
        
        df = self.processed_data
        
        # Statistiques de base
        self.stats = {
            'total_rows': len(df),
            'columns_detected': len(self.column_mappings),
            'detection_report': self.detection_report,
            'unique_components': df.get('composant', pd.Series()).nunique(),
            'unique_subcomponents': df.get('sous_composant', pd.Series()).nunique(),
            'unique_causes': df.get('cause', pd.Series()).nunique(),
            'unique_grouping_keys': df.get('grouping_key', pd.Series()).nunique()
        }
        
        # Statistiques sur les durées
        if 'duree' in df.columns:
            self.stats.update({
                'avg_duration': df['duree'].mean(),
                'max_duration': df['duree'].max(),
                'min_duration': df['duree'].min(),
                'total_downtime': df['duree'].sum()
            })
        
        # Distribution des composants
        if 'composant' in df.columns:
            component_counts = df['composant'].value_counts().to_dict()
            self.stats['component_distribution'] = component_counts
        
        # Distribution des causes
        if 'cause' in df.columns:
            cause_counts = df['cause'].value_counts().to_dict()
            self.stats['cause_distribution'] = cause_counts
        
        # Prédiction du nombre de lignes AMDEC finales
        if 'grouping_key' in df.columns:
            self.stats['predicted_amdec_entries'] = df['grouping_key'].nunique()
        
        logger.info(f"📊 Statistiques calculées: {self.stats['unique_grouping_keys']} groupes uniques détectés")
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques calculées"""
        return self.stats
    
    def get_processed_data(self) -> Optional[pd.DataFrame]:
        """Retourne les données traitées"""
        return self.processed_data
    
    def get_detection_report(self) -> Dict:
        """Retourne le rapport de détection des colonnes"""
        return self.detection_report
    
    def save_processed_data(self, output_path: str = None) -> str:
        """
        Sauvegarde les données traitées
        
        Args:
            output_path: Chemin de sortie (optionnel)
            
        Returns:
            Chemin du fichier sauvegardé
        """
        if self.processed_data is None:
            raise ValueError("Aucune donnée traitée à sauvegarder")
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"historique_processed_{timestamp}.xlsx"
            output_path = os.path.join('data/historique', filename)
        
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Sauvegarder avec un formatage de base
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            self.processed_data.to_excel(writer, sheet_name='Données_Nettoyées', index=False)
            
            # Ajouter une feuille avec les statistiques
            stats_df = pd.DataFrame(list(self.stats.items()), columns=['Métrique', 'Valeur'])
            stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
            
            # Ajouter le rapport de détection
            detection_df = pd.DataFrame(list(self.detection_report.items()), columns=['Type', 'Valeur'])
            detection_df.to_excel(writer, sheet_name='Détection_Colonnes', index=False)
        
        logger.info(f"✅ Données sauvegardées: {output_path}")
        return output_path