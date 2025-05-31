#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package RAG pour AMDEC & Gamme IA
Système de chatbot intelligent avec base de connaissances vectorielle
✅ CORRIGÉ: Suppression dépendances problématiques

REMPLACE COMPLÈTEMENT : rag/__init__.py
"""

__version__ = "1.0.0"
__author__ = "AMDEC & Gamme IA Team"

# Import depuis rag_engine qui contient tout
try:
    from .rag_engine import RAGEngine, DocumentProcessor, VectorStore, LLMClient
    RAG_COMPONENTS_AVAILABLE = True
except ImportError as e:
    # Fallback si les composants ne sont pas disponibles
    RAG_COMPONENTS_AVAILABLE = False
    
    # Classes de fallback
    class RAGEngine:
        def __init__(self, *args, **kwargs):
            pass
        def initialize(self):
            return False
        def query(self, question):
            return {'response': 'RAG non disponible', 'sources': []}
    
    class DocumentProcessor:
        def __init__(self, *args, **kwargs):
            pass
    
    class VectorStore:
        def __init__(self, *args, **kwargs):
            pass
    
    class LLMClient:
        def __init__(self, *args, **kwargs):
            pass

__all__ = [
    'RAGEngine',
    'VectorStore', 
    'DocumentProcessor',
    'LLMClient',
    'RAG_COMPONENTS_AVAILABLE'
]