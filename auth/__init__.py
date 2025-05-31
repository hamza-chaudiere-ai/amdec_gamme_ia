#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'authentification pour AMDEC & Gamme IA
Système de sécurité basé sur emails professionnels @taqa.ma
"""

__version__ = "1.0.0"
__author__ = "AMDEC & Gamme IA Security Team"

from .auth_manager import AuthManager
from .email_validator import EmailValidator
from .session_manager import SessionManager

__all__ = [
    'AuthManager',
    'EmailValidator', 
    'SessionManager'
]