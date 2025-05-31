#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire d'authentification pour AMDEC & Gamme IA
Contrôle d'accès basé sur emails professionnels TAQA Morocco
"""

import os
import json
import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from email.mime.text import MIMEText  # ✅ Correct

from email.mime.multipart import MIMEMultipart  # ✅

import logging

from .email_validator import EmailValidator
from .session_manager import SessionManager

logger = logging.getLogger(__name__)

class AuthManager:
    """Gestionnaire principal d'authentification"""
    
    def __init__(self, config_path: str = "auth_config.json"):
        """
        Initialise le gestionnaire d'authentification
        
        Args:
            config_path: Chemin vers la configuration d'authentification
        """
        self.config = self._load_config(config_path)
        self.email_validator = EmailValidator()
        self.session_manager = SessionManager()
        self.pending_verifications = {}
        
        # Créer les répertoires nécessaires
        os.makedirs("data", exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration d'authentification"""
        default_config = {
            "allowed_domains": ["taqa.ma"],
            "session_duration_hours": 8,
            "max_login_attempts": 3,
            "verification_code_length": 6,
            "verification_timeout_minutes": 15,
            "smtp_server": "smtp.office365.com",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "app_name": "AMDEC & Gamme IA",
            "company_name": "TAQA Morocco"
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            else:
                # Créer le fichier de config par défaut
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logger.warning(f"Erreur chargement config auth: {e}")
            
        return default_config
    
    def is_email_authorized(self, email: str) -> Tuple[bool, str]:
        """
        Vérifie si un email est autorisé à accéder à l'application
        
        Args:
            email: Adresse email à vérifier
            
        Returns:
            Tuple (is_authorized, reason)
        """
        if not email or not isinstance(email, str):
            return False, "Email invalide"
            
        email = email.lower().strip()
        
        # Validation format email
        if not self.email_validator.is_valid_email(email):
            return False, "Format d'email invalide"
        
        # Vérification domaine autorisé
        domain = email.split('@')[1] if '@' in email else ''
        if domain not in self.config["allowed_domains"]:
            allowed_domains_str = ", ".join(self.config["allowed_domains"])
            return False, f"Accès restreint aux domaines: {allowed_domains_str}"
        
        return True, "Email autorisé"
    
    def send_verification_code(self, email: str) -> Tuple[bool, str]:
        """
        Envoie un code de vérification par email
        
        Args:
            email: Adresse email de destination
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Vérifier que l'email est autorisé
            is_authorized, reason = self.is_email_authorized(email)
            if not is_authorized:
                return False, reason
            
            # Générer le code de vérification
            code = self._generate_verification_code()
            
            # Stocker le code avec expiration
            expiry = datetime.now() + timedelta(
                minutes=self.config["verification_timeout_minutes"]
            )
            
            self.pending_verifications[email] = {
                'code': code,
                'expiry': expiry,
                'attempts': 0
            }
            
            # Envoyer l'email (si SMTP configuré)
            if self.config.get("smtp_username"):
                email_sent = self._send_email(email, code)
                if email_sent:
                    logger.info(f"Code de vérification envoyé à {email}")
                    return True, "Code de vérification envoyé par email"
                else:
                    logger.warning(f"Échec envoi email à {email}")
                    return True, f"Code de vérification généré: {code} (email non configuré)"
            else:
                # Mode développement : afficher le code
                logger.info(f"Code de vérification pour {email}: {code}")
                return True, f"Code de vérification généré: {code}"
                
        except Exception as e:
            logger.error(f"Erreur envoi code de vérification: {e}")
            return False, "Erreur lors de l'envoi du code"
    
    def verify_code(self, email: str, code: str) -> Tuple[bool, str]:
        """
        Vérifie un code de vérification
        
        Args:
            email: Adresse email
            code: Code saisi par l'utilisateur
            
        Returns:
            Tuple (success, message)
        """
        email = email.lower().strip()
        code = code.strip()
        
        if email not in self.pending_verifications:
            return False, "Aucun code de vérification en attente pour cet email"
        
        verification = self.pending_verifications[email]
        
        # Vérifier l'expiration
        if datetime.now() > verification['expiry']:
            del self.pending_verifications[email]
            return False, "Code de vérification expiré"
        
        # Incrémenter les tentatives
        verification['attempts'] += 1
        
        # Vérifier le nombre de tentatives
        if verification['attempts'] > self.config["max_login_attempts"]:
            del self.pending_verifications[email]
            return False, "Trop de tentatives incorrectes"
        
        # Vérifier le code
        if verification['code'] != code:
            return False, f"Code incorrect ({verification['attempts']}/{self.config['max_login_attempts']})"
        
        # Code correct
        del self.pending_verifications[email]
        return True, "Code vérifié avec succès"
    
    def login_user(self, email: str, code: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Connecte un utilisateur
        
        Args:
            email: Adresse email
            code: Code de vérification (optionnel)
            
        Returns:
            Tuple (success, message, session_token)
        """
        try:
            email = email.lower().strip()
            
            # Si un code est fourni, le vérifier
            if code:
                code_valid, code_message = self.verify_code(email, code)
                if not code_valid:
                    return False, code_message, None
            else:
                # Vérifier que l'email est autorisé
                is_authorized, reason = self.is_email_authorized(email)
                if not is_authorized:
                    return False, reason, None
            
            # Créer une session
            session_token = self.session_manager.create_session(email)
            
            logger.info(f"Utilisateur connecté: {email}")
            return True, "Connexion réussie", session_token
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            return False, "Erreur lors de la connexion", None
    
    def logout_user(self, session_token: str) -> bool:
        """
        Déconnecte un utilisateur
        
        Args:
            session_token: Token de session
            
        Returns:
            Success status
        """
        try:
            user_email = self.session_manager.get_user_from_session(session_token)
            if user_email:
                self.session_manager.invalidate_session(session_token)
                logger.info(f"Utilisateur déconnecté: {user_email}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            return False
    
    def is_user_authenticated(self, session_token: str) -> Tuple[bool, Optional[str]]:
        """
        Vérifie si un utilisateur est authentifié
        
        Args:
            session_token: Token de session
            
        Returns:
            Tuple (is_authenticated, user_email)
        """
        try:
            user_email = self.session_manager.get_user_from_session(session_token)
            if user_email:
                return True, user_email
            return False, None
        except Exception as e:
            logger.error(f"Erreur vérification authentification: {e}")
            return False, None
    
    def get_user_info(self, session_token: str) -> Optional[Dict]:
        """
        Récupère les informations d'un utilisateur connecté
        
        Args:
            session_token: Token de session
            
        Returns:
            Informations utilisateur ou None
        """
        is_authenticated, user_email = self.is_user_authenticated(session_token)
        if not is_authenticated:
            return None
            
        return {
            'email': user_email,
            'domain': user_email.split('@')[1],
            'company': self.config["company_name"],
            'login_time': self.session_manager.get_session_info(session_token).get('created_at'),
            'expires_at': self.session_manager.get_session_info(session_token).get('expires_at')
        }
    
    def _generate_verification_code(self) -> str:
        """Génère un code de vérification aléatoire"""
        code_length = self.config["verification_code_length"]
        # Générer un code numérique
        code = ''.join(secrets.choice('0123456789') for _ in range(code_length))
        return code
    
    def _send_email(self, recipient_email: str, verification_code: str) -> bool:
        """
        Envoie un email avec le code de vérification
        
        Args:
            recipient_email: Email destinataire
            verification_code: Code à envoyer
            
        Returns:
            Success status
        """
        try:
            # Configuration SMTP
            smtp_server = self.config["smtp_server"]
            smtp_port = self.config["smtp_port"]
            smtp_username = self.config["smtp_username"]
            smtp_password = self.config["smtp_password"]
            
            if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
                logger.warning("Configuration SMTP incomplète")
                return False
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = recipient_email
            msg['Subject'] = f"Code d'accès {self.config['app_name']}"
            
            # Corps du message
            body = f"""
Bonjour,

Voici votre code d'accès pour {self.config['app_name']} :

    {verification_code}

Ce code est valide pendant {self.config['verification_timeout_minutes']} minutes.

Si vous n'avez pas demandé cet accès, ignorez ce message.

---
{self.config['company_name']}
Assistant IA de Maintenance Industrielle
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Envoyer l'email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    def cleanup_expired_verifications(self):
        """Nettoie les codes de vérification expirés"""
        try:
            now = datetime.now()
            expired_emails = [
                email for email, verification in self.pending_verifications.items()
                if now > verification['expiry']
            ]
            
            for email in expired_emails:
                del self.pending_verifications[email]
                
            if expired_emails:
                logger.info(f"Nettoyé {len(expired_emails)} codes expirés")
                
        except Exception as e:
            logger.error(f"Erreur nettoyage codes expirés: {e}")
    
    def get_active_sessions_count(self) -> int:
        """Retourne le nombre de sessions actives"""
        return self.session_manager.get_active_sessions_count()
    
    def get_system_stats(self) -> Dict:
        """Retourne les statistiques du système d'authentification"""
        return {
            'active_sessions': self.get_active_sessions_count(),
            'pending_verifications': len(self.pending_verifications),
            'allowed_domains': self.config["allowed_domains"],
            'session_duration_hours': self.config["session_duration_hours"],
            'max_login_attempts': self.config["max_login_attempts"]
        }