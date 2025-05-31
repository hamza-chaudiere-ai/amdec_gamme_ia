#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moteur RAG Complet pour AMDEC & Gamme IA
✅ CORRIGÉ: Import huggingface_hub 
🤖 Système de chatbot intelligent avec récupération augmentée
"""

import logging
import re
import os
import json
import sqlite3
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import logging
logger = logging.getLogger(__name__)


# ===============================
# 🔧 IMPORTS AVEC GESTION D'ERREURS
# ===============================

# Imports requis avec fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy non disponible")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ✅ CORRECTION: Import HuggingFace Hub avec fallback
try:
    from huggingface_hub import hf_hub_download
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    try:
        # Fallback pour anciennes versions
        from huggingface_hub import cached_download as hf_hub_download
        HUGGINGFACE_AVAILABLE = True
    except ImportError:
        HUGGINGFACE_AVAILABLE = False

# Imports pour traitement des documents
try:
    import docx
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)

# ===============================
# 📚 CLASSE DOCUMENT PROCESSOR
# ===============================

class DocumentProcessor:
    """Traite et extrait le contenu des documents techniques"""
    
    def __init__(self, documents_dir: str):
        self.documents_dir = documents_dir
        self.processed_docs = []
        
        # Base de connaissances par défaut si pas de documents
        self.default_knowledge = self._build_default_knowledge()
    
    def _build_default_knowledge(self) -> List[Dict]:
        """Construit une base de connaissances par défaut"""
        return [
            {
                'content': """
                CORROSION CAUSTIC ATTACK - ÉCONOMISEUR BT
                
                Définition: La corrosion caustic attack est une forme de corrosion spécifique qui affecte 
                principalement les collecteurs de sortie des économiseurs basse température. Elle se caractérise 
                par une attaque chimique due à la concentration d'agents alcalins (sodium, potassium) dans l'eau.
                
                Causes principales:
                - Concentration excessive de soude caustique (NaOH)
                - Zones de stagnation avec évaporation
                - pH local très élevé (>12)
                - Température entre 250-350°C
                
                Effets observés:
                - Amincissement localisé des parois
                - Formation de cavités profondes
                - Perte de matière interne importante
                - Risque de percement
                
                Solutions:
                1. Contrôle strict du pH de l'eau d'alimentation
                2. Limitation des concentrations en sodium (<3ppm)
                3. Amélioration de la circulation dans les collecteurs
                4. Surveillance par ultrasons des épaisseurs
                5. Revêtement céramique des zones sensibles
                
                Criticité: ÉLEVÉE (F=3, G=5, D=3, C=45)
                Fréquence de contrôle: Mensuelle
                """,
                'source': 'Base expertise AMDEC',
                'section': 'Défauts Économiseur BT',
                'component': 'economiseur_bt',
                'defect': 'corrosion'
            },
            {
                'content': """
                SURCHAUFFE LONG TERME - SURCHAUFFEUR HT
                
                Définition: La surchauffe long terme (long-term overheat) est un phénomène de dégradation 
                progressive des tubes porteurs de surchauffeurs haute température exposés à des températures 
                dépassant leurs limites de conception sur des périodes prolongées.
                
                Mécanisme:
                - Exposition prolongée à T > 580°C
                - Dégradation de la microstructure métallique
                - Formation de carbures grossiers
                - Perte de résistance mécanique
                
                Signes d'alerte:
                - Déformation progressive des tubes (fluage)
                - Changement de couleur (oxydation)
                - Microfissures de fluage
                - Durcissement local du métal
                
                Causes:
                - Mauvaise répartition des débits de vapeur
                - Encrassement des surfaces d'échange
                - Combustion déséquilibrée
                - Défaillance du système de régulation
                
                Actions correctives:
                1. Optimisation de la combustion
                2. Installation de capteurs de température permanents
                3. Amélioration de la circulation vapeur
                4. Nettoyage régulier des surfaces
                5. Renforcement des supports
                6. Remplacement préventif des sections critiques
                
                Criticité: CRITIQUE (F=2, G=5, D=2, C=20)
                """,
                'source': 'Base expertise AMDEC',
                'section': 'Défauts Surchauffeur HT',
                'component': 'surchauffeur_ht',
                'defect': 'surchauffe'
            },
            {
                'content': """
                ACID ATTACK - RÉCHAUFFEUR HT
                
                Définition: L'acid attack est une forme de corrosion acide qui affecte spécifiquement 
                les branches de sortie des réchauffeurs haute température. Elle résulte de la condensation 
                d'acides (sulfurique, chlorhydrique) sur les surfaces métalliques.
                
                Mécanisme:
                - Condensation d'acides faibles (H2SO4, HCl)
                - Attaque chimique localisée
                - Formation de surfaces "fromage suisse"
                - Perte progressive de matière
                
                Facteurs favorisants:
                - Présence de soufre dans le combustible
                - Température de paroi < point de rosée acide
                - Zones de circulation réduite
                - Accumulation de dépôts
                
                Prévention:
                1. Maintien de la température de paroi > 150°C
                2. Amélioration de l'isolation thermique
                3. Optimisation des débits de vapeur
                4. Nettoyage chimique périodique
                5. Protection par revêtement résistant aux acides
                6. Contrôle qualité du combustible
                
                Détection:
                - Inspection visuelle des surfaces
                - Mesure d'épaisseur par ultrasons
                - Analyse chimique des dépôts
                - Contrôle pH des condensats
                
                Criticité: ÉLEVÉE (F=3, G=4, D=2, C=24)
                """,
                'source': 'Base expertise AMDEC',
                'section': 'Défauts Réchauffeur HT',
                'component': 'rechauffeur_ht',
                'defect': 'corrosion'
            },
            {
                'content': """
                MAINTENANCE PRÉVENTIVE - ÉCONOMISEUR BT
                
                Programme de maintenance pour économiseur basse température:
                
                INSPECTION VISUELLE (Mensuelle):
                - Contrôle général de l'état externe
                - Vérification des supports et fixations
                - Recherche de fuites visibles
                - Documentation photographique
                Matériel: Lampe torche, appareil photo, échelle
                Durée: 45 minutes
                
                CONTRÔLE ULTRASONS (Trimestrielle):
                - Mesure d'épaisseur des zones sensibles
                - Cartographie des amincissements
                - Suivi de l'évolution des défauts
                Matériel: Appareil ultrasons, gel de contact, calibres
                Durée: 90 minutes
                
                TEST D'ÉTANCHÉITÉ (Semestrielle):
                - Pressurisation selon procédure
                - Recherche de fuites sous pression
                - Contrôle des joints et brides
                Matériel: Kit test étanchéité, manomètres, produit traceur
                Durée: 120 minutes
                
                NETTOYAGE PRÉVENTIF (Annuelle):
                - Élimination des dépôts internes
                - Nettoyage chimique si nécessaire
                - Rinçage et neutralisation
                Matériel: Pompe circulation, produits chimiques, analyseur pH
                Durée: 4-6 heures
                
                Consignes de sécurité:
                - EPI obligatoires (casque, gants, lunettes)
                - Consignation électrique et mécanique
                - Vérification absence pression/température
                - Balisage zone intervention
                """,
                'source': 'Guide maintenance préventive',
                'section': 'Procédures Économiseur',
                'component': 'economiseur_bt',
                'defect': 'maintenance'
            },
            {
                'content': """
                ANALYSE CRITICITÉ AMDEC - MÉTHODE F×G×D
                
                La criticité dans l'analyse AMDEC se calcule selon la formule: C = F × G × D
                
                F - FRÉQUENCE d'apparition:
                1 = Très rare (< 1 fois/10 ans)
                2 = Rare (1 fois/2-10 ans) 
                3 = Occasionnelle (1 fois/an)
                4 = Fréquente (plusieurs fois/an)
                5 = Très fréquente (> 1 fois/mois)
                
                G - GRAVITÉ des conséquences:
                1 = Négligeable (pas d'impact)
                2 = Légère (impact mineur)
                3 = Modérée (dégradation performance)
                4 = Grave (arrêt programmé)
                5 = Catastrophique (arrêt d'urgence, sécurité)
                
                D - DÉTECTION:
                1 = Détection certaine (surveillance continue)
                2 = Détection probable (contrôles réguliers)
                3 = Détection possible (inspections périodiques)
                4 = Détection improbable (pas de surveillance)
                
                NIVEAUX DE CRITICITÉ:
                C ≤ 12: Négligeable - Maintenance corrective
                12 < C ≤ 16: Moyenne - Maintenance préventive systématique
                16 < C ≤ 20: Élevée - Maintenance préventive conditionnelle  
                C > 20: Critique - Remise en cause conception
                
                Exemples:
                - Corrosion épingle économiseur: F=3, G=4, D=2 → C=24 (Critique)
                - Fissure collecteur: F=2, G=5, D=3 → C=30 (Critique)
                - Encrassement modéré: F=4, G=2, D=1 → C=8 (Négligeable)
                """,
                'source': 'Méthode AMDEC',
                'section': 'Calcul criticité',
                'component': 'general',
                'defect': 'criticite'
            }
        ]
    
    def process_all_documents(self) -> List[Dict]:
        """Traite tous les documents disponibles"""
        documents = []
        
        try:
            if not os.path.exists(self.documents_dir):
                logger.warning(f"Répertoire documents {self.documents_dir} non trouvé")
                return self.default_knowledge
            
            # Parcourir tous les fichiers
            for root, dirs, files in os.walk(self.documents_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if file.endswith('.docx') and DOCX_AVAILABLE:
                        docs = self._process_docx(file_path)
                        documents.extend(docs)
                    elif file.endswith('.pdf') and PDF_AVAILABLE:
                        docs = self._process_pdf(file_path)
                        documents.extend(docs)
                    elif file.endswith('.xlsx') and PANDAS_AVAILABLE:
                        docs = self._process_excel(file_path)
                        documents.extend(docs)
                    elif file.endswith(('.txt', '.md')):
                        docs = self._process_text(file_path)
                        documents.extend(docs)
            
            # Si aucun document traité, utiliser la base par défaut
            if not documents:
                logger.info("Aucun document externe trouvé, utilisation base par défaut")
                return self.default_knowledge
            
            # Combiner avec la base par défaut
            all_documents = self.default_knowledge + documents
            
            logger.info(f"Documents traités: {len(documents)} externes + {len(self.default_knowledge)} par défaut")
            return all_documents
            
        except Exception as e:
            logger.error(f"Erreur traitement documents: {e}")
            return self.default_knowledge
    
    def _process_docx(self, file_path: str) -> List[Dict]:
        """Traite un fichier Word"""
        try:
            doc = DocxDocument(file_path)
            filename = os.path.basename(file_path)
            
            documents = []
            current_section = "Introduction"
            content_buffer = []
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                
                if not text:
                    continue
                
                # Détecter les nouveaux sections (headers)
                if (paragraph.style.name.startswith('Heading') or 
                    len(text) < 100 and text.isupper()):
                    
                    # Sauvegarder la section précédente
                    if content_buffer:
                        documents.append({
                            'content': '\n'.join(content_buffer),
                            'source': filename,
                            'section': current_section,
                            'component': self._detect_component(current_section),
                            'defect': self._detect_defect('\n'.join(content_buffer))
                        })
                        content_buffer = []
                    
                    current_section = text
                else:
                    content_buffer.append(text)
            
            # Dernière section
            if content_buffer:
                documents.append({
                    'content': '\n'.join(content_buffer),
                    'source': filename,
                    'section': current_section,
                    'component': self._detect_component(current_section),
                    'defect': self._detect_defect('\n'.join(content_buffer))
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Erreur traitement DOCX {file_path}: {e}")
            return []
    
    def _process_pdf(self, file_path: str) -> List[Dict]:
        """Traite un fichier PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                content = ""
                
                for page in reader.pages:
                    content += page.extract_text() + "\n"
            
            if content.strip():
                return [{
                    'content': content,
                    'source': os.path.basename(file_path),
                    'section': 'Document PDF',
                    'component': self._detect_component(content),
                    'defect': self._detect_defect(content)
                }]
            
            return []
            
        except Exception as e:
            logger.error(f"Erreur traitement PDF {file_path}: {e}")
            return []
    
    def _process_excel(self, file_path: str) -> List[Dict]:
        """Traite un fichier Excel"""
        try:
            df = pd.read_excel(file_path)
            filename = os.path.basename(file_path)
            documents = []
            
            # Traiter chaque ligne comme un document
            for index, row in df.iterrows():
                content_parts = []
                for col, value in row.items():
                    if pd.notna(value) and str(value).strip():
                        content_parts.append(f"{col}: {value}")
                
                if content_parts:
                    content = '\n'.join(content_parts)
                    documents.append({
                        'content': content,
                        'source': filename,
                        'section': f'Ligne {index + 1}',
                        'component': self._detect_component(content),
                        'defect': self._detect_defect(content)
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Erreur traitement Excel {file_path}: {e}")
            return []
    
    def _process_text(self, file_path: str) -> List[Dict]:
        """Traite un fichier texte"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if content.strip():
                return [{
                    'content': content,
                    'source': os.path.basename(file_path),
                    'section': 'Document texte',
                    'component': self._detect_component(content),
                    'defect': self._detect_defect(content)
                }]
            
            return []
            
        except Exception as e:
            logger.error(f"Erreur traitement texte {file_path}: {e}")
            return []
    
    def _detect_component(self, text: str) -> str:
        """Détecte le composant dans le texte"""
        text_lower = text.lower()
        
        components = {
            'economiseur_bt': ['économiseur bt', 'economiseur basse', 'eco bt'],
            'economiseur_ht': ['économiseur ht', 'economiseur haute', 'eco ht'],
            'surchauffeur_bt': ['surchauffeur bt', 'surchauffeur basse'],
            'surchauffeur_ht': ['surchauffeur ht', 'surchauffeur haute'],
            'rechauffeur_bt': ['réchauffeur bt', 'rechauffeur basse'],
            'rechauffeur_ht': ['réchauffeur ht', 'rechauffeur haute']
        }
        
        for component, patterns in components.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return component
        
        return 'general'
    
    def _detect_defect(self, text: str) -> str:
        """Détecte le type de défaut dans le texte"""
        text_lower = text.lower()
        
        defects = {
            'corrosion': ['corrosion', 'caustic attack', 'acid attack', 'rouille'],
            'surchauffe': ['surchauffe', 'overheat', 'température', 'fluage'],
            'fissure': ['fissure', 'crack', 'fente', 'rupture'],
            'erosion': ['érosion', 'usure', 'abrasion'],
            'maintenance': ['maintenance', 'inspection', 'contrôle'],
            'criticite': ['criticité', 'amdec', 'f×g×d']
        }
        
        for defect, patterns in defects.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return defect
        
        return 'general'

# ===============================
# 🗄️ CLASSE VECTOR STORE
# ===============================

class VectorStore:
    """Stockage et recherche vectorielle avec SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.embeddings_model = None
        self._init_database()
        self._init_embeddings()
    
    def _init_database(self):
        """Initialise la base de données SQLite"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table pour les documents
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    section TEXT NOT NULL,
                    component TEXT,
                    defect TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index pour recherche rapide
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON documents(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_component ON documents(component)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_defect ON documents(defect)")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur initialisation base: {e}")
    
    def _init_embeddings(self):
        """Initialise le modèle d'embeddings"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("SentenceTransformers non disponible, utilisation fallback")
            return
        
        try:
            # Utiliser un modèle multilingue optimisé
            model_name = "all-MiniLM-L6-v2"  # Modèle léger et performant
            self.embeddings_model = SentenceTransformer(model_name)
            logger.info(f"Modèle embeddings chargé: {model_name}")
            
        except Exception as e:
            logger.error(f"Erreur chargement modèle embeddings: {e}")
            self.embeddings_model = None
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """Ajoute des documents à la base vectorielle"""
        try:
            if not self.embeddings_model:
                logger.warning("Modèle embeddings non disponible")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for doc in documents:
                content = doc['content']
                
                # Générer l'embedding
                try:
                    embedding = self.embeddings_model.encode(content)
                    embedding_blob = embedding.tobytes()
                except Exception as e:
                    logger.warning(f"Erreur embedding document: {e}")
                    continue
                
                # Insérer en base
                cursor.execute("""
                    INSERT INTO documents (content, source, section, component, defect, embedding)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    content,
                    doc.get('source', 'Unknown'),
                    doc.get('section', 'Unknown'),
                    doc.get('component', 'general'),
                    doc.get('defect', 'general'),
                    embedding_blob
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Ajouté {len(documents)} documents à la base vectorielle")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout documents: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5, min_similarity: float = 0.1) -> List[Dict]:
        """Recherche sémantique dans la base"""
        try:
            if not self.embeddings_model:
                return self._fallback_search(query, n_results)
            
            # Encoder la requête
            query_embedding = self.embeddings_model.encode(query)
            
            # Récupérer tous les documents
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, content, source, section, component, defect, embedding
                FROM documents
            """)
            
            results = []
            for row in cursor.fetchall():
                doc_id, content, source, section, component, defect, embedding_blob = row
                
                if embedding_blob:
                    # Reconstituer l'embedding
                    doc_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    
                    # Calculer la similarité cosinus
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    
                    if similarity >= min_similarity:
                        results.append({
                            'id': doc_id,
                            'content': content,
                            'source': source,
                            'section': section,
                            'component': component,
                            'defect': defect,
                            'similarity': float(similarity)
                        })
            
            conn.close()
            
            # Trier par similarité
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return results[:n_results]
            
        except Exception as e:
            logger.error(f"Erreur recherche: {e}")
            return self._fallback_search(query, n_results)
    
    def search_by_keywords(self, keywords: List[str], n_results: int = 3) -> List[Dict]:
        """Recherche par mots-clés (fallback)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construire la requête LIKE
            like_conditions = []
            params = []
            
            for keyword in keywords:
                like_conditions.append("content LIKE ?")
                params.append(f"%{keyword}%")
            
            query = f"""
                SELECT content, source, section, component, defect
                FROM documents
                WHERE {' OR '.join(like_conditions)}
                LIMIT ?
            """
            params.append(n_results)
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                content, source, section, component, defect = row
                results.append({
                    'content': content,
                    'source': source,
                    'section': section,
                    'component': component,
                    'defect': defect,
                    'similarity': 0.5  # Similarité par défaut pour mots-clés
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche mots-clés: {e}")
            return []
    
    def _fallback_search(self, query: str, n_results: int) -> List[Dict]:
        """Recherche de fallback basée sur mots-clés"""
        query_words = query.lower().split()
        return self.search_by_keywords(query_words, n_results)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcule la similarité cosinus entre deux vecteurs"""
        if not NUMPY_AVAILABLE:
            return 0.5
        
        try:
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception:
            return 0.5
    
    def clear_collection(self):
        """Vide la collection de documents"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents")
            conn.commit()
            conn.close()
            logger.info("Collection vidée")
        except Exception as e:
            logger.error(f"Erreur vidage collection: {e}")
    
    def get_collection_stats(self) -> Dict:
        """Retourne les statistiques de la collection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_docs = cursor.fetchone()[0]
            
            cursor.execute("SELECT DISTINCT source FROM documents LIMIT 10")
            sample_sources = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'total_documents': total_docs,
                'sample_sources': sample_sources
            }
            
        except Exception as e:
            logger.error(f"Erreur stats collection: {e}")
            return {'total_documents': 0, 'sample_sources': []}
    
    def is_healthy(self) -> bool:
        """Vérifie la santé de la base vectorielle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception:
            return False

# ===============================
# 🤖 CLASSE LLM CLIENT  
# ===============================

class LLMClient:
    """Client pour interaction avec LLM (Groq/OpenAI compatible)"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration LLM"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                # Configuration par défaut
                self.config = {
                    "type": "api",
                    "name": "llama3-70b-8192",
                    "api_key": "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",
                    "api_url": "https://api.groq.com/openai/v1/chat/completions"
                }
                
                # Sauvegarder la config par défaut
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                
                logger.info("Configuration LLM par défaut créée")
            
        except Exception as e:
            logger.error(f"Erreur chargement config LLM: {e}")
            self.config = {}
    
    def test_connection(self) -> bool:
        """Teste la connexion au LLM"""
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests non disponible pour test LLM")
            return False
        
        try:
            if not self.config.get('api_key') or not self.config.get('api_url'):
                return False
            
            headers = {
                'Authorization': f"Bearer {self.config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.config.get('name', 'llama3-70b-8192'),
                'messages': [{'role': 'user', 'content': 'Test'}],
                'max_tokens': 10,
                'temperature': 0.1
            }
            
            response = requests.post(
                self.config['api_url'],
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Test connexion LLM échoué: {e}")
            return False
    
    def generate_response(self, system_prompt: str, user_query: str, 
                         context: str, temperature: float = 0.7) -> str:
        """Génère une réponse via le LLM"""
        if not REQUESTS_AVAILABLE:
            return self._fallback_response(user_query, context)
        
        try:
            headers = {
                'Authorization': f"Bearer {self.config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            # Construire le prompt complet
            full_prompt = f"""Contexte technique:
{context}

Question: {user_query}

Réponds de manière précise et technique en te basant sur le contexte fourni."""
            
            data = {
                'model': self.config.get('name', 'llama3-70b-8192'),
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': full_prompt}
                ],
                'max_tokens': 1000,
                'temperature': temperature
            }
            
            response = requests.post(
                self.config['api_url'],
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Erreur API LLM: {response.status_code}")
                return self._fallback_response(user_query, context)
                
        except Exception as e:
            logger.error(f"Erreur génération réponse LLM: {e}")
            return self._fallback_response(user_query, context)
    
    def _fallback_response(self, user_query: str, context: str) -> str:
        """Réponse de fallback basée sur le contexte"""
        query_lower = user_query.lower()
        
        # Réponses prédéfinies selon le type de question
        if 'caustic attack' in query_lower:
            return """La corrosion caustic attack est une forme de corrosion spécifique aux économiseurs BT.
            
**Causes**: Concentration excessive de soude caustique (NaOH), zones de stagnation.
**Solutions**: Contrôle pH, limitation sodium <3ppm, surveillance ultrasons.
**Criticité**: ÉLEVÉE (C=45)"""
        
        elif 'surchauffe' in query_lower and 'long terme' in query_lower:
            return """La surchauffe long terme affecte les surchauffeurs HT exposés à T>580°C.
            
**Effets**: Fluage, déformation, perte résistance mécanique.
**Solutions**: Optimisation combustion, capteurs température, renforcement supports.
**Criticité**: CRITIQUE (C=20)"""
        
        elif 'acid attack' in query_lower:
            return """L'acid attack touche les réchauffeurs HT par condensation d'acides.
            
**Prévention**: Maintien T>150°C, amélioration isolation, nettoyage chimique.
**Détection**: Inspection visuelle, mesure ultrasons.
**Criticité**: ÉLEVÉE (C=24)"""
        
        elif any(word in query_lower for word in ['maintenance', 'contrôle', 'inspection']):
            return """Programme de maintenance préventive recommandé:
            
- **Mensuel**: Inspection visuelle (45 min)
- **Trimestriel**: Contrôle ultrasons (90 min)  
- **Semestriel**: Test étanchéité (120 min)
- **Annuel**: Nettoyage complet (4-6h)

**Sécurité**: EPI, consignation, vérification pression/température."""
        
        elif 'criticité' in query_lower or 'amdec' in query_lower:
            return """Calcul criticité AMDEC: C = F × G × D
            
**Niveaux**:
- C ≤ 12: Négligeable (maintenance corrective)
- 12 < C ≤ 16: Moyenne (préventive systématique)
- 16 < C ≤ 20: Élevée (préventive conditionnelle)
- C > 20: Critique (remise en cause conception)

**F**: Fréquence (1-5), **G**: Gravité (1-5), **D**: Détection (1-4)"""
        
        else:
            # Extraire des informations du contexte si disponible
            if context and len(context) > 100:
                # Prendre les premiers 300 caractères du contexte
                summary = context[:300] + "..."
                return f"""Basé sur la documentation technique disponible:

{summary}

Pour une réponse plus précise, veuillez reformuler votre question ou préciser le composant concerné."""
            
            return """Je peux vous aider avec les questions concernant:
            
🔧 **Composants**: Économiseurs, Surchauffeurs, Réchauffeurs (BT/HT)
⚠️ **Défauts**: Corrosion, Surchauffe, Fissures, Érosion
🛠️ **Maintenance**: Procédures, Fréquences, Matériel
📊 **AMDEC**: Calculs criticité, Analyses F×G×D

Exemple: "J'ai un percement sur l'économiseur BT, que faire ?" """
    
    def get_system_prompt(self) -> str:
        """Retourne le prompt système pour le chatbot"""
        return """Tu es un expert en maintenance industrielle spécialisé dans les chaudières et l'analyse AMDEC.

**Ton rôle**: Fournir des conseils techniques précis sur la maintenance des équipements de chaudière.

**Expertise**: 
- Analyses AMDEC et calculs de criticité (F×G×D)
- Défauts courants: corrosion, surchauffe, fissures, érosion
- Composants: Économiseurs, Surchauffeurs, Réchauffeurs (BT/HT)
- Maintenance préventive et corrective

**Style de réponse**:
- Précis et technique mais accessible
- Structure claire avec sections (Diagnostic, Solutions, Prévention)
- Indications de criticité et urgence
- Consignes de sécurité importantes

**Utilise le contexte fourni** pour donner des réponses précises basées sur la documentation technique."""
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles"""
        return [
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]

# ===============================
# 🤖 CLASSE RAG ENGINE PRINCIPALE
# ===============================

class RAGEngine:
    """Moteur RAG principal orchestrant la recherche et génération de réponses"""
    
    def __init__(self, 
                 documents_dir: str = "data/documents",
                 vector_db_path: str = "data/vector_db/chroma.db",
                 llm_config_path: str = "llm_config.json"):
        """
        Initialise le moteur RAG
        
        Args:
            documents_dir: Répertoire des documents techniques
            vector_db_path: Chemin de la base vectorielle
            llm_config_path: Configuration du LLM
        """
        self.documents_dir = documents_dir
        self.vector_db_path = vector_db_path
        self.llm_config_path = llm_config_path
        
        # Initialiser les composants
        self.document_processor = DocumentProcessor(documents_dir)
        self.vector_store = VectorStore(vector_db_path)
        self.llm_client = LLMClient(llm_config_path)
        
        # État d'initialisation
        self.is_initialized = False
        self.last_index_update = None
        
        # Patterns de détection pour améliorer la recherche
        self.component_patterns = {
            'economiseur_bt': ['économiseur bt', 'economiseur basse température', 'eco bt'],
            'economiseur_ht': ['économiseur ht', 'economiseur haute température', 'eco ht'],
            'surchauffeur_bt': ['surchauffeur bt', 'surchauffeur basse température', 'sur bt'],
            'surchauffeur_ht': ['surchauffeur ht', 'surchauffeur haute température', 'sur ht'],
            'rechauffeur_bt': ['réchauffeur bt', 'rechauffeur basse température', 'rch bt'],
            'rechauffeur_ht': ['réchauffeur ht', 'rechauffeur haute température', 'rch ht']
        }
        
        self.defect_patterns = {
            'corrosion': ['corrosion', 'rouille', 'oxydation', 'attaque', 'caustic', 'acid'],
            'fissure': ['fissure', 'crack', 'fente', 'cassure', 'rupture'],
            'percement': ['percement', 'trou', 'perforation', 'perce'],
            'surchauffe': ['surchauffe', 'température', 'overheat', 'thermique', 'fluage'],
            'erosion': ['érosion', 'usure', 'abrasion', 'dégradation'],
            'fatigue': ['fatigue', 'cycles', 'contrainte', 'stress']
        }
    
    def initialize(self, force_reindex: bool = False) -> bool:
        """
        Initialise le moteur RAG et indexe les documents
        
        Args:
            force_reindex: Force la réindexation des documents
            
        Returns:
            True si l'initialisation réussit
        """
        try:
            logger.info("🚀 Initialisation du moteur RAG...")
            
            # Vérifier la santé des composants
            llm_healthy = self.llm_client.test_connection()
            if not llm_healthy:
                logger.warning("⚠️ Connexion LLM non optimale, mais RAG fonctionnel")
            
            if not self.vector_store.is_healthy():
                logger.info("🔄 Initialisation de la base vectorielle...")
                self.vector_store.clear_collection()
            
            # Vérifier si indexation nécessaire
            stats = self.vector_store.get_collection_stats()
            needs_indexing = (
                force_reindex or 
                stats.get('total_documents', 0) == 0 or
                self._should_reindex()
            )
            
            if needs_indexing:
                logger.info("📚 Indexation des documents nécessaire...")
                if not self._index_documents():
                    logger.warning("⚠️ Échec de l'indexation, utilisation base par défaut")
            else:
                logger.info(f"✅ Base vectorielle OK ({stats.get('total_documents', 0)} documents)")
            
            self.is_initialized = True
            self.last_index_update = datetime.now()
            
            logger.info("✅ Moteur RAG initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation RAG: {e}")
            # Même en cas d'erreur, marquer comme initialisé pour fallback
            self.is_initialized = True
            return True  # Retourner True pour permettre le fonctionnement en mode dégradé
    
    def _should_reindex(self) -> bool:
        """Détermine si une réindexation est nécessaire"""
        try:
            # Vérifier la présence de nouveaux documents
            if not os.path.exists(self.documents_dir):
                return True
            
            doc_files = []
            for root, dirs, files in os.walk(self.documents_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in ['.docx', '.pdf', '.xlsx', '.md', '.txt']):
                        doc_files.append(os.path.join(root, file))
            
            # Si plus de 0 fichiers documents et moins de 5 entrées vectorielles
            stats = self.vector_store.get_collection_stats()
            return len(doc_files) > 0 and stats.get('total_documents', 0) < 5
            
        except Exception as e:
            logger.warning(f"Erreur vérification réindexation: {e}")
            return True
    
    def _index_documents(self) -> bool:
        """Indexe tous les documents dans la base vectorielle"""
        try:
            logger.info("🔄 Traitement et indexation des documents...")
            
            # Traiter les documents
            documents = self.document_processor.process_all_documents()
            
            if not documents:
                logger.warning("⚠️ Aucun document trouvé")
                return False
            
            # Nettoyer la collection existante si nécessaire
            if self.vector_store.get_collection_stats().get('total_documents', 0) > 0:
                logger.info("🧹 Nettoyage de la base vectorielle existante...")
                self.vector_store.clear_collection()
            
            # Ajouter les documents
            success = self.vector_store.add_documents(documents)
            
            if success:
                stats = self.vector_store.get_collection_stats()
                logger.info(f"✅ Indexation terminée: {stats.get('total_documents', 0)} documents")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur indexation documents: {e}")
            return False
    
    def query(self, user_question: str, max_context_length: int = 3000) -> Dict:
        """
        Traite une question utilisateur et génère une réponse
        
        Args:
            user_question: Question de l'utilisateur
            max_context_length: Longueur maximale du contexte RAG
            
        Returns:
            Dictionnaire avec réponse, contexte, métadonnées
        """
        try:
            if not self.is_initialized:
                logger.warning("Moteur RAG non initialisé, tentative d'initialisation...")
                if not self.initialize():
                    return {
                        'response': "Désolé, le système n'est pas encore prêt. Veuillez réessayer dans quelques instants.",
                        'error': 'RAG not initialized',
                        'context': '',
                        'sources': []
                    }
            
            logger.info(f"🔍 Traitement de la question: {user_question[:100]}...")
            
            # Étape 1: Analyser la question
            analysis = self._analyze_question(user_question)
            
            # Étape 2: Recherche vectorielle
            relevant_docs = self._search_relevant_documents(user_question, analysis)
            
            # Étape 3: Construire le contexte
            context = self._build_context(relevant_docs, max_context_length)
            
            # Étape 4: Générer la réponse
            response = self._generate_response(user_question, context, analysis)
            
            # Étape 5: Post-traitement
            final_response = self._post_process_response(response, analysis)
            
            return {
                'response': final_response,
                'context': context,
                'sources': [doc.get('source', 'Unknown') for doc in relevant_docs],
                'detected_components': analysis.get('components', []),
                'detected_defects': analysis.get('defects', []),
                'confidence': self._calculate_confidence(relevant_docs),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement question: {e}")
            return {
                'response': f"Désolé, une erreur s'est produite lors du traitement de votre question. Veuillez réessayer ou reformuler votre demande.",
                'error': str(e),
                'context': '',
                'sources': []
            }
    
    def _analyze_question(self, question: str) -> Dict:
        """Analyse la question pour détecter composants et défauts"""
        analysis = {
            'components': [],
            'defects': [],
            'question_type': 'general',
            'keywords': []
        }
        
        question_lower = question.lower()
        
        # Détecter les composants
        for component, patterns in self.component_patterns.items():
            for pattern in patterns:
                if pattern in question_lower:
                    if component not in analysis['components']:
                        analysis['components'].append(component)
                    analysis['keywords'].append(pattern)
                    break
        
        # Détecter les défauts
        for defect, patterns in self.defect_patterns.items():
            for pattern in patterns:
                if pattern in question_lower:
                    if defect not in analysis['defects']:
                        analysis['defects'].append(defect)
                    analysis['keywords'].append(pattern)
                    break
        
        # Déterminer le type de question
        if any(word in question_lower for word in ['que faire', 'solution', 'réparer', 'corriger']):
            analysis['question_type'] = 'solution'
        elif any(word in question_lower for word in ['qu\'est-ce', 'définition', 'expliquer']):
            analysis['question_type'] = 'explanation'
        elif any(word in question_lower for word in ['criticité', 'urgent', 'priorité']):
            analysis['question_type'] = 'criticality'
        elif any(word in question_lower for word in ['maintenance', 'contrôle', 'inspection']):
            analysis['question_type'] = 'maintenance'
        
        return analysis
    
    def _search_relevant_documents(self, question: str, analysis: Dict) -> List[Dict]:
        """Recherche les documents pertinents"""
        # Recherche sémantique principale
        semantic_results = self.vector_store.search(question, n_results=5, min_similarity=0.1)
        
        # Recherche par mots-clés spécifiques
        keywords = analysis.get('keywords', [])
        if keywords:
            keyword_results = self.vector_store.search_by_keywords(keywords, n_results=3)
        else:
            keyword_results = []
        
        # Combiner et déduplicater
        all_results = semantic_results + keyword_results
        
        # Déduplication par contenu
        seen_content = set()
        unique_results = []
        
        for doc in all_results:
            content_preview = doc.get('content', '')[:200]  # Premiers 200 caractères
            content_hash = hash(content_preview)
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(doc)
        
        # Trier par pertinence (similarité + bonus pour mots-clés)
        for doc in unique_results:
            bonus = 0
            if keywords:
                content_lower = doc.get('content', '').lower()
                for keyword in keywords:
                    if keyword.lower() in content_lower:
                        bonus += 0.1
            doc['final_score'] = doc.get('similarity', 0.5) + bonus
        
        # Trier et limiter
        sorted_results = sorted(unique_results, key=lambda x: x.get('final_score', 0), reverse=True)
        
        return sorted_results[:6]  # Limiter à 6 documents maximum
    
    def _build_context(self, documents: List[Dict], max_length: int) -> str:
        """Construit le contexte RAG à partir des documents pertinents"""
        if not documents:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(documents):
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            section = doc.get('section', 'Unknown')
            
            # Formater l'extrait
            formatted_doc = f"[Source: {source} - {section}]\n{content}\n"
            
            # Vérifier la longueur
            if current_length + len(formatted_doc) > max_length:
                if current_length == 0:  # Au moins inclure le premier document
                    # Tronquer le document
                    available_space = max_length - len(f"[Source: {source} - {section}]\n") - 50
                    if available_space > 100:
                        truncated_content = content[:available_space] + "..."
                        formatted_doc = f"[Source: {source} - {section}]\n{truncated_content}\n"
                        context_parts.append(formatted_doc)
                break
            
            context_parts.append(formatted_doc)
            current_length += len(formatted_doc)
        
        return "\n".join(context_parts)
    
    def _generate_response(self, question: str, context: str, analysis: Dict) -> str:
        """Génère la réponse via le LLM"""
        # Construire un prompt système adapté au type de question
        system_prompt = self.llm_client.get_system_prompt()
        
        # Ajouter des instructions spécifiques selon le type de question
        question_type = analysis.get('question_type', 'general')
        
        if question_type == 'solution':
            system_prompt += "\n\nPour cette question de résolution de problème, structure ta réponse ainsi:\n" \
                           "1. **Diagnostic** du problème\n" \
                           "2. **Solutions immédiates** à mettre en œuvre\n" \
                           "3. **Actions préventives** pour éviter la récurrence\n" \
                           "4. **Niveau de criticité** et urgence\n" \
                           "5. **Consignes de sécurité** importantes"
        
        elif question_type == 'explanation':
            system_prompt += "\n\nPour cette question d'explication, fournis:\n" \
                           "1. **Définition claire** du phénomène\n" \
                           "2. **Causes principales** identifiées\n" \
                           "3. **Conséquences** possibles\n" \
                           "4. **Prévention** recommandée"
        
        elif question_type == 'maintenance':
            system_prompt += "\n\nPour cette question de maintenance, indique:\n" \
                           "1. **Opérations** recommandées\n" \
                           "2. **Fréquence** d'intervention\n" \
                           "3. **Matériel** nécessaire\n" \
                           "4. **Procédure** détaillée\n" \
                           "5. **Points de contrôle** critiques"
        
        # Générer la réponse
        response = self.llm_client.generate_response(
            system_prompt=system_prompt,
            user_query=question,
            context=context,
            temperature=0.7
        )
        
        return response
    
    def _post_process_response(self, response: str, analysis: Dict) -> str:
        """Post-traite la réponse pour améliorer la qualité"""
        # Ajouter des informations de contexte si pertinent
        components = analysis.get('components', [])
        defects = analysis.get('defects', [])
        
        # Ajouter une note sur les composants détectés
        if components or defects:
            context_note = "\n\n---\n"
            
            if components:
                comp_names = {
                    'economiseur_bt': 'Économiseur BT',
                    'economiseur_ht': 'Économiseur HT',
                    'surchauffeur_bt': 'Surchauffeur BT',
                    'surchauffeur_ht': 'Surchauffeur HT',
                    'rechauffeur_bt': 'Réchauffeur BT',
                    'rechauffeur_ht': 'Réchauffeur HT'
                }
                detected_comps = [comp_names.get(comp, comp) for comp in components]
                context_note += f"🔧 **Composant(s) identifié(s)**: {', '.join(detected_comps)}\n"
            
            if defects:
                defect_names = {
                    'corrosion': 'Corrosion',
                    'fissure': 'Fissuration',
                    'percement': 'Percement',
                    'surchauffe': 'Surchauffe',
                    'erosion': 'Érosion',
                    'fatigue': 'Fatigue'
                }
                detected_defects = [defect_names.get(defect, defect) for defect in defects]
                context_note += f"⚠️ **Défaut(s) identifié(s)**: {', '.join(detected_defects)}\n"
            
            context_note += "\n💡 *Cette analyse est basée sur la base de connaissances AMDEC & Gamme IA*"
            
            response += context_note
        
        return response
    
    def _calculate_confidence(self, documents: List[Dict]) -> float:
        """Calcule le niveau de confiance de la réponse"""
        if not documents:
            return 0.3  # Confiance minimale
        
        # Confiance basée sur:
        # - Nombre de documents pertinents
        # - Similarité moyenne
        # - Diversité des sources
        
        similarities = [doc.get('similarity', 0.5) for doc in documents]
        avg_similarity = sum(similarities) / len(similarities)
        
        # Bonus pour multiple documents
        doc_bonus = min(len(documents) / 5.0, 1.0)
        
        # Bonus pour diversité des sources
        sources = set(doc.get('source', 'unknown') for doc in documents)
        source_bonus = min(len(sources) / 3.0, 1.0)
        
        confidence = (avg_similarity + doc_bonus * 0.2 + source_bonus * 0.1)
        
        return min(round(confidence, 2), 1.0)
    
    def get_system_status(self) -> Dict:
        """Retourne l'état du système RAG"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            llm_healthy = self.llm_client.test_connection()
            
            return {
                'initialized': self.is_initialized,
                'last_index_update': self.last_index_update.isoformat() if self.last_index_update else None,
                'vector_store': {
                    'healthy': self.vector_store.is_healthy(),
                    'total_documents': vector_stats.get('total_documents', 0),
                    'sample_sources': vector_stats.get('sample_sources', [])
                },
                'llm_client': {
                    'healthy': llm_healthy,
                    'model': self.llm_client.config.get('name', 'unknown'),
                    'available_models': self.llm_client.get_available_models()
                },
                'components_supported': list(self.component_patterns.keys()),
                'defects_detected': list(self.defect_patterns.keys()),
                'dependencies': {
                    'sentence_transformers': SENTENCE_TRANSFORMERS_AVAILABLE,
                    'numpy': NUMPY_AVAILABLE,
                    'requests': REQUESTS_AVAILABLE,
                    'pandas': PANDAS_AVAILABLE,
                    'docx': DOCX_AVAILABLE,
                    'pdf': PDF_AVAILABLE
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur statut système: {e}")
            return {'error': str(e)}
    
    def update_knowledge_base(self) -> bool:
        """Met à jour la base de connaissances"""
        try:
            logger.info("🔄 Mise à jour de la base de connaissances...")
            return self.initialize(force_reindex=True)
        except Exception as e:
            logger.error(f"Erreur mise à jour base: {e}")
            return False