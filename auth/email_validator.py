#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validateur d'emails pour AMDEC & Gamme IA
Validation spécialisée pour les domaines TAQA Morocco
"""

import re
import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

class EmailValidator:
    """Validateur d'adresses email avec règles spécifiques TAQA"""
    
    def __init__(self):
        """Initialise le validateur"""
        self.email_regex = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Domaines autorisés TAQA Morocco
        self.authorized_domains = [
            'taqa.ma',
            'taqa-morocco.ma',  # Si d'autres domaines existent
        ]
        
        # Préfixes/suffixes interdits
        self.forbidden_patterns = [
            'test@',
            'demo@', 
            'admin@',
            'root@',
            'noreply@',
            'no-reply@'
        ]
        
        # Domaines personnels courants à bloquer explicitement
        self.personal_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'live.com', 'msn.com', 'aol.com', 'icloud.com',
            'protonmail.com', 'yandex.com', 'mail.com'
        ]
    
    def is_valid_email(self, email: str) -> bool:
        """
        Vérifie si l'email a un format valide
        
        Args:
            email: Adresse email à valider
            
        Returns:
            True si le format est valide
        """
        if not email or not isinstance(email, str):
            return False
            
        email = email.strip().lower()
        
        # Vérification regex basique
        if not self.email_regex.match(email):
            return False
        
        # Vérifications supplémentaires
        if len(email) > 254:  # RFC 5321
            return False
            
        local_part, domain_part = email.split('@')
        
        # Vérifier la partie locale
        if len(local_part) > 64:  # RFC 5321
            return False
            
        if local_part.startswith('.') or local_part.endswith('.'):
            return False
            
        if '..' in local_part:
            return False
        
        # Vérifier le domaine
        if len(domain_part) > 253:
            return False
            
        return True
    
    def is_authorized_domain(self, email: str) -> Tuple[bool, str]:
        """
        Vérifie si le domaine de l'email est autorisé
        
        Args:
            email: Adresse email à vérifier
            
        Returns:
            Tuple (is_authorized, reason)
        """
        if not self.is_valid_email(email):
            return False, "Format d'email invalide"
        
        email = email.strip().lower()
        domain = email.split('@')[1]
        
        # Vérifier si c'est un domaine autorisé
        if domain in self.authorized_domains:
            return True, "Domaine autorisé"
        
        # Vérifier si c'est un domaine personnel (explicitement interdit)
        if domain in self.personal_domains:
            return False, f"Domaines personnels non autorisés. Utilisez votre email @taqa.ma"
        
        # Domaine non reconnu
        authorized_list = ", ".join(self.authorized_domains)
        return False, f"Seuls les domaines suivants sont autorisés: {authorized_list}"
    
    def is_forbidden_pattern(self, email: str) -> Tuple[bool, str]:
        """
        Vérifie si l'email contient des motifs interdits
        
        Args:
            email: Adresse email à vérifier
            
        Returns:
            Tuple (is_forbidden, reason)
        """
        email = email.strip().lower()
        
        for pattern in self.forbidden_patterns:
            if email.startswith(pattern):
                return True, f"Adresses commençant par '{pattern}' non autorisées"
        
        return False, "Aucun motif interdit détecté"
    
    def validate_full(self, email: str) -> Tuple[bool, str]:
        """
        Validation complète d'un email
        
        Args:
            email: Adresse email à valider
            
        Returns:
            Tuple (is_valid, reason)
        """
        # Vérification format
        if not self.is_valid_email(email):
            return False, "Format d'email invalide"
        
        # Vérification motifs interdits
        is_forbidden, forbidden_reason = self.is_forbidden_pattern(email)
        if is_forbidden:
            return False, forbidden_reason
        
        # Vérification domaine autorisé
        is_authorized, auth_reason = self.is_authorized_domain(email)
        if not is_authorized:
            return False, auth_reason
        
        return True, "Email valide et autorisé"
    
    def get_domain_from_email(self, email: str) -> str:
        """
        Extrait le domaine d'une adresse email
        
        Args:
            email: Adresse email
            
        Returns:
            Nom de domaine ou chaîne vide si invalide
        """
        if not self.is_valid_email(email):
            return ""
        
        return email.strip().lower().split('@')[1]
    
    def suggest_correct_email(self, email: str) -> List[str]:
        """
        Suggère des corrections pour un email invalide
        
        Args:
            email: Adresse email potentiellement incorrecte
            
        Returns:
            Liste de suggestions
        """
        suggestions = []
        
        if not email or '@' not in email:
            return suggestions
        
        email = email.strip().lower()
        local_part = email.split('@')[0]
        
        # Si le domaine n'est pas autorisé, suggérer les domaines TAQA
        for domain in self.authorized_domains:
            suggestion = f"{local_part}@{domain}"
            if self.validate_full(suggestion)[0]:
                suggestions.append(suggestion)
        
        return suggestions
    
    def get_validation_rules(self) -> Dict:
        """
        Retourne les règles de validation pour l'interface utilisateur
        
        Returns:
            Dictionnaire des règles
        """
        return {
            'authorized_domains': self.authorized_domains,
            'max_email_length': 254,
            'max_local_length': 64,
            'forbidden_patterns': self.forbidden_patterns,
            'blocked_personal_domains': self.personal_domains[:10],  # Première partie pour l'affichage
            'format_requirements': [
                'Format standard nom@domaine.extension',
                'Pas d\'espaces ou caractères spéciaux interdits',
                'Maximum 254 caractères au total'
            ],
            'domain_requirements': [
                'Seuls les emails @taqa.ma sont autorisés',
                'Pas d\'emails personnels (Gmail, Yahoo, etc.)',
                'Pas d\'emails de test ou administrateur'
            ]
        }