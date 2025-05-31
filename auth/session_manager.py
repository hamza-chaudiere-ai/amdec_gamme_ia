#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de sessions pour AMDEC & Gamme IA
Gestion sécurisée des sessions utilisateur avec persistance
"""

import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Gestionnaire de sessions utilisateur"""
    
    def __init__(self, session_file: str = "data/auth_sessions.json"):
        """
        Initialise le gestionnaire de sessions
        
        Args:
            session_file: Fichier de stockage des sessions
        """
        self.session_file = session_file
        self.sessions = {}
        
        # Configuration par défaut
        self.session_duration_hours = 8
        self.max_sessions_per_user = 3
        self.cleanup_interval_hours = 1
        
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(session_file), exist_ok=True)
        
        # Charger les sessions existantes
        self._load_sessions()
        
        # Nettoyer les sessions expirées
        self._cleanup_expired_sessions()
    
    def _load_sessions(self):
        """Charge les sessions depuis le fichier"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Convertir les chaînes de dates en objets datetime
                    for session_id, session_data in data.items():
                        if 'created_at' in session_data:
                            session_data['created_at'] = datetime.fromisoformat(
                                session_data['created_at']
                            )
                        if 'expires_at' in session_data:
                            session_data['expires_at'] = datetime.fromisoformat(
                                session_data['expires_at']
                            )
                        if 'last_activity' in session_data:
                            session_data['last_activity'] = datetime.fromisoformat(
                                session_data['last_activity']
                            )
                    
                    self.sessions = data
                    logger.info(f"Chargé {len(self.sessions)} sessions depuis {self.session_file}")
                    
        except Exception as e:
            logger.error(f"Erreur chargement sessions: {e}")
            self.sessions = {}
    
    def _save_sessions(self):
        """Sauvegarde les sessions dans le fichier"""
        try:
            # Convertir les objets datetime en chaînes pour JSON
            data_to_save = {}
            for session_id, session_data in self.sessions.items():
                data_copy = session_data.copy()
                
                if 'created_at' in data_copy and isinstance(data_copy['created_at'], datetime):
                    data_copy['created_at'] = data_copy['created_at'].isoformat()
                if 'expires_at' in data_copy and isinstance(data_copy['expires_at'], datetime):
                    data_copy['expires_at'] = data_copy['expires_at'].isoformat()
                if 'last_activity' in data_copy and isinstance(data_copy['last_activity'], datetime):
                    data_copy['last_activity'] = data_copy['last_activity'].isoformat()
                
                data_to_save[session_id] = data_copy
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde sessions: {e}")
    
    def create_session(self, user_email: str) -> str:
        """
        Crée une nouvelle session pour un utilisateur
        
        Args:
            user_email: Email de l'utilisateur
            
        Returns:
            Token de session
        """
        try:
            user_email = user_email.lower().strip()
            
            # Nettoyer les anciennes sessions de l'utilisateur si nécessaire
            self._cleanup_user_sessions(user_email)
            
            # Générer un token sécurisé
            session_token = self._generate_session_token()
            
            # Créer les données de session
            now = datetime.now()
            session_data = {
                'user_email': user_email,
                'created_at': now,
                'expires_at': now + timedelta(hours=self.session_duration_hours),
                'last_activity': now,
                'ip_address': None,  # À implémenter si nécessaire
                'user_agent': None,  # À implémenter si nécessaire
                'is_active': True
            }
            
            # Stocker la session
            self.sessions[session_token] = session_data
            
            # Sauvegarder
            self._save_sessions()
            
            logger.info(f"Session créée pour {user_email}: {session_token[:8]}...")
            return session_token
            
        except Exception as e:
            logger.error(f"Erreur création session: {e}")
            raise
    
    def get_user_from_session(self, session_token: str) -> Optional[str]:
        """
        Récupère l'utilisateur associé à un token de session
        
        Args:
            session_token: Token de session
            
        Returns:
            Email utilisateur ou None si session invalide
        """
        try:
            if not session_token or session_token not in self.sessions:
                return None
            
            session_data = self.sessions[session_token]
            
            # Vérifier si la session est active
            if not session_data.get('is_active', False):
                return None
            
            # Vérifier l'expiration
            if datetime.now() > session_data['expires_at']:
                self.invalidate_session(session_token)
                return None
            
            # Mettre à jour la dernière activité
            session_data['last_activity'] = datetime.now()
            self._save_sessions()
            
            return session_data['user_email']
            
        except Exception as e:
            logger.error(f"Erreur récupération utilisateur: {e}")
            return None
    
    def invalidate_session(self, session_token: str) -> bool:
        """
        Invalide une session
        
        Args:
            session_token: Token de session à invalider
            
        Returns:
            True si la session a été invalidée
        """
        try:
            if session_token in self.sessions:
                user_email = self.sessions[session_token].get('user_email', 'unknown')
                del self.sessions[session_token]
                self._save_sessions()
                
                logger.info(f"Session invalidée pour {user_email}: {session_token[:8]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur invalidation session: {e}")
            return False
    
    def extend_session(self, session_token: str, hours: int = None) -> bool:
        """
        Prolonge une session
        
        Args:
            session_token: Token de session
            hours: Nombre d'heures à ajouter (par défaut: session_duration_hours)
            
        Returns:
            True si la session a été prolongée
        """
        try:
            if session_token not in self.sessions:
                return False
            
            hours = hours or self.session_duration_hours
            session_data = self.sessions[session_token]
            
            # Prolonger l'expiration
            session_data['expires_at'] = datetime.now() + timedelta(hours=hours)
            session_data['last_activity'] = datetime.now()
            
            self._save_sessions()
            
            user_email = session_data.get('user_email', 'unknown')
            logger.info(f"Session prolongée pour {user_email}: +{hours}h")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur prolongation session: {e}")
            return False
    
    def get_session_info(self, session_token: str) -> Optional[Dict]:
        """
        Récupère les informations d'une session
        
        Args:
            session_token: Token de session
            
        Returns:
            Informations de session ou None
        """
        if session_token not in self.sessions:
            return None
        
        session_data = self.sessions[session_token].copy()
        
        # Ajouter des informations calculées
        now = datetime.now()
        session_data['is_expired'] = now > session_data['expires_at']
        session_data['remaining_time_minutes'] = max(
            0, 
            int((session_data['expires_at'] - now).total_seconds() / 60)
        )
        
        return session_data
    
    def get_user_sessions(self, user_email: str) -> List[Dict]:
        """
        Récupère toutes les sessions actives d'un utilisateur
        
        Args:
            user_email: Email de l'utilisateur
            
        Returns:
            Liste des sessions de l'utilisateur
        """
        user_email = user_email.lower().strip()
        user_sessions = []
        
        for session_token, session_data in self.sessions.items():
            if (session_data.get('user_email') == user_email and 
                session_data.get('is_active', False) and
                datetime.now() <= session_data['expires_at']):
                
                session_info = session_data.copy()
                session_info['session_token'] = session_token[:8] + '...'  # Token tronqué
                user_sessions.append(session_info)
        
        return user_sessions
    
    def invalidate_all_user_sessions(self, user_email: str) -> int:
        """
        Invalide toutes les sessions d'un utilisateur
        
        Args:
            user_email: Email de l'utilisateur
            
        Returns:
            Nombre de sessions invalidées
        """
        user_email = user_email.lower().strip()
        sessions_to_remove = []
        
        for session_token, session_data in self.sessions.items():
            if session_data.get('user_email') == user_email:
                sessions_to_remove.append(session_token)
        
        for session_token in sessions_to_remove:
            del self.sessions[session_token]
        
        if sessions_to_remove:
            self._save_sessions()
            logger.info(f"Invalidé {len(sessions_to_remove)} sessions pour {user_email}")
        
        return len(sessions_to_remove)
    
    def get_active_sessions_count(self) -> int:
        """Retourne le nombre de sessions actives"""
        now = datetime.now()
        active_count = 0
        
        for session_data in self.sessions.values():
            if (session_data.get('is_active', False) and 
                now <= session_data['expires_at']):
                active_count += 1
        
        return active_count
    
    def _generate_session_token(self) -> str:
        """Génère un token de session sécurisé"""
        # Générer 32 bytes aléatoires et les encoder en hexadécimal
        random_bytes = secrets.token_bytes(32)
        token = random_bytes.hex()
        
        # Ajouter un hash basé sur le timestamp pour l'unicité
        timestamp = str(datetime.now().timestamp())
        hash_suffix = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
        
        return f"{token}{hash_suffix}"
    
    def _cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        try:
            now = datetime.now()
            expired_sessions = []
            
            for session_token, session_data in self.sessions.items():
                if now > session_data['expires_at']:
                    expired_sessions.append(session_token)
            
            for session_token in expired_sessions:
                user_email = self.sessions[session_token].get('user_email', 'unknown')
                del self.sessions[session_token]
                logger.debug(f"Session expirée supprimée: {user_email}")
            
            if expired_sessions:
                self._save_sessions()
                logger.info(f"Nettoyé {len(expired_sessions)} sessions expirées")
                
        except Exception as e:
            logger.error(f"Erreur nettoyage sessions expirées: {e}")
    
    def _cleanup_user_sessions(self, user_email: str):
        """Nettoie les anciennes sessions d'un utilisateur si nécessaire"""
        user_sessions = self.get_user_sessions(user_email)
        
        if len(user_sessions) >= self.max_sessions_per_user:
            # Trier par dernière activité (plus anciennes en premier)
            user_sessions.sort(key=lambda x: x['last_activity'])
            
            # Supprimer les plus anciennes
            sessions_to_remove = len(user_sessions) - self.max_sessions_per_user + 1
            
            for i in range(sessions_to_remove):
                # Retrouver le token complet
                partial_token = user_sessions[i]['session_token'].replace('...', '')
                for session_token in self.sessions:
                    if session_token.startswith(partial_token):
                        del self.sessions[session_token]
                        break
            
            logger.info(f"Supprimé {sessions_to_remove} anciennes sessions pour {user_email}")
    
    def get_system_stats(self) -> Dict:
        """Retourne les statistiques du système de sessions"""
        now = datetime.now()
        total_sessions = len(self.sessions)
        active_sessions = 0
        expired_sessions = 0
        
        users = set()
        
        for session_data in self.sessions.values():
            if now <= session_data['expires_at']:
                active_sessions += 1
            else:
                expired_sessions += 1
            
            users.add(session_data.get('user_email', ''))
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'expired_sessions': expired_sessions,
            'unique_users': len(users) - (1 if '' in users else 0),
            'session_duration_hours': self.session_duration_hours,
            'max_sessions_per_user': self.max_sessions_per_user
        }