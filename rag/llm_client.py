#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client LLM pour AMDEC & Gamme IA - Groq API
Gestion des requêtes vers le modèle Llama3 via Groq
"""

import os
import json
import logging
from typing import Dict, List, Optional
from groq import Groq

logger = logging.getLogger(__name__)

class LLMClient:
    """Client pour interagir avec Groq API (Llama3)"""
    
    def __init__(self, config_path: str = "llm_config.json"):
        """
        Initialise le client LLM
        
        Args:
            config_path: Chemin vers la configuration LLM
        """
        self.config = self._load_config(config_path)
        self.client = self._initialize_client()
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration LLM"""
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(config_path):
                logger.warning(f"Fichier config {config_path} non trouvé, utilisation de la config par défaut")
                return self._get_default_config()
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Vérifier la clé API dans les variables d'environnement
            groq_api_key = os.getenv('GROQ_API_KEY', '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')
            config['api_key'] = groq_api_key
            
            logger.info(f"Configuration LLM chargée: {config.get('name', 'unknown')}")
            return config
            
        except Exception as e:
            logger.error(f"Erreur chargement config LLM: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Configuration par défaut"""
        return {
            "type": "api",
            "name": "llama3-70b-8192",
            "api_key": os.getenv('GROQ_API_KEY', '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'),
            "api_url": "https://api.groq.com/openai/v1/chat/completions",
            "temperature": 0.7,
            "max_tokens": 2048
        }
    
    def _initialize_client(self) -> Groq:
        """Initialise le client Groq"""
        try:
            client = Groq(api_key=self.config['api_key'])
            logger.info("Client Groq initialisé avec succès")
            return client
        except Exception as e:
            logger.error(f"Erreur initialisation client Groq: {e}")
            raise
    
    def generate_response(self, system_prompt: str, user_query: str, 
                         context: str = "", temperature: float = None) -> str:
        """
        Génère une réponse via Groq Llama3
        
        Args:
            system_prompt: Prompt système pour définir le comportement
            user_query: Question de l'utilisateur
            context: Contexte RAG (documents pertinents)
            temperature: Température de génération
            
        Returns:
            Réponse générée par le LLM
        """
        try:
            # Construire le prompt complet
            if context:
                full_prompt = f"""Contexte technique disponible:
{context}

Question de l'utilisateur: {user_query}

Réponds en te basant sur le contexte technique fourni et ta connaissance des chaudières industrielles."""
            else:
                full_prompt = user_query
            
            # Paramètres de génération
            temperature = temperature or self.config.get('temperature', 0.7)
            max_tokens = self.config.get('max_tokens', 2048)
            
            # Appel à l'API Groq
            response = self.client.chat.completions.create(
                model=self.config['name'],
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": full_prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                stream=False
            )
            
            # Extraire la réponse
            generated_text = response.choices[0].message.content.strip()
            
            logger.info(f"Réponse LLM générée ({len(generated_text)} caractères)")
            return generated_text
            
        except Exception as e:
            logger.error(f"Erreur génération réponse LLM: {e}")
            return f"Désolé, je ne peux pas répondre pour le moment. Erreur: {str(e)}"
    
    def get_system_prompt(self) -> str:
        """Retourne le prompt système optimisé pour AMDEC & Gamme IA"""
        return """Tu es un expert en maintenance industrielle spécialisé dans les chaudières et les analyses AMDEC.

Tes compétences incluent :
- Diagnostic des défaillances de chaudières (économiseurs, surchauffeurs, réchauffeurs)
- Analyses AMDEC (Analyse des Modes de Défaillance, de leurs Effets et de leur Criticité)
- Recommandations de maintenance préventive et corrective
- Identification des causes de pannes et solutions techniques

Instructions de réponse :
1. **Diagnostic précis** : Identifie le composant concerné et le type de défaillance
2. **Solutions pratiques** : Propose des actions concrètes et réalisables
3. **Niveau de criticité** : Évalue l'urgence (F×G×D) si pertinent
4. **Recommandations préventives** : Suggère des mesures pour éviter la récurrence
5. **Sécurité** : Mentionne toujours les consignes de sécurité importantes

Format de réponse souhaité :
- **Diagnostic** : Description claire du problème
- **Cause probable** : Explication technique
- **Solution immédiate** : Actions à prendre rapidement
- **Solution long terme** : Prévention et amélioration
- **Criticité** : Niveau d'urgence et justification
- **Sécurité** : Consignes de sécurité essentielles

Utilise un langage technique mais accessible, et base-toi sur les meilleures pratiques industrielles."""
    
    def test_connection(self) -> bool:
        """Teste la connexion à l'API Groq"""
        try:
            test_response = self.generate_response(
                system_prompt="Tu es un assistant test.",
                user_query="Réponds simplement 'Test OK' pour vérifier la connexion.",
                temperature=0.1
            )
            
            is_working = "test ok" in test_response.lower()
            if is_working:
                logger.info("Test connexion Groq: ✅ OK")
            else:
                logger.warning(f"Test connexion Groq: ⚠️ Réponse inattendue: {test_response}")
                
            return is_working
            
        except Exception as e:
            logger.error(f"Test connexion Groq: ❌ Échec - {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles"""
        try:
            # Les modèles Groq disponibles
            return [
                "llama3-70b-8192",
                "llama3-8b-8192", 
                "mixtral-8x7b-32768",
                "gemma-7b-it"
            ]
        except Exception as e:
            logger.error(f"Erreur récupération modèles: {e}")
            return [self.config.get('name', 'llama3-70b-8192')]