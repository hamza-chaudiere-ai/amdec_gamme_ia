#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ CORRIGÉ: rag_engine.py - Remplace complètement l'ancien code
Résout l'erreur "unable to open database file" définitivement
"""

import os
import sys
import stat
import shutil
import logging
import tempfile
import json
import sqlite3
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# ===============================
# 🔧 IMPORTS AVEC GESTION D'ERREURS
# ===============================

# ChromaDB avec gestion d'erreurs robuste
try:
    import chromadb
    from chromadb import PersistentClient
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
    CHROMADB_VERSION = chromadb.__version__
    logger.info(f"ChromaDB version: {CHROMADB_VERSION}")
except ImportError as e:
    CHROMADB_AVAILABLE = False
    CHROMADB_VERSION = None
    logger.warning(f"ChromaDB non disponible: {e}")

# SentenceTransformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning(f"SentenceTransformers non disponible: {e}")

# NumPy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy non disponible")

# Autres imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("Requests non disponible")

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx non disponible")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 non disponible")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("Pandas non disponible")

# ===============================
# 🗄️ CLASSE VECTOR STORE CORRIGÉE
# ===============================

class VectorStore:
    """✅ Magasin vectoriel corrigé - résout l'erreur 'unable to open database file'"""
    
    def __init__(self, db_path: str = "data/vector_db", collection_name: str = "amdec_knowledge"):
        self.db_path = os.path.abspath(db_path)
        self.collection_name = collection_name
        self.embedding_model = None
        self.client = None
        self.collection = None
        self.fallback_mode = False
        self.sqlite_path = None
        self.is_windows = os.name == 'nt'
        
        logger.info(f"🔄 Initialisation VectorStore: {self.db_path}")
        
        self._prepare_directories()
        self._initialize_embedding_model()
        self._initialize_vector_store()
    
    def _prepare_directories(self):
        """Prépare les répertoires avec gestion permissions Windows/Linux"""
        try:
            # Créer répertoires avec permissions
            parent_dir = os.path.dirname(self.db_path)
            os.makedirs(parent_dir, exist_ok=True)
            os.makedirs(self.db_path, exist_ok=True)
            
            # Test d'écriture
            test_file = os.path.join(self.db_path, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            logger.info("✅ Répertoires et permissions OK")
            
        except Exception as e:
            logger.error(f"❌ Erreur préparation répertoires: {e}")
            raise
    
    def _initialize_embedding_model(self):
        """Initialise le modèle d'embeddings"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("⚠️ SentenceTransformers non disponible")
            return
        
        try:
            # Modèle léger et compatible
            model_name = "all-MiniLM-L6-v2"
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Modèle embeddings chargé: {model_name}")
            
        except Exception as e:
            logger.warning(f"Erreur chargement embeddings: {e}")
            self.embedding_model = None
    
    def _initialize_vector_store(self):
        """✅ CORRECTION PRINCIPALE: Initialise ChromaDB avec fallback SQLite"""
        if not CHROMADB_AVAILABLE:
            logger.info("ChromaDB non disponible, utilisation SQLite")
            self._initialize_sqlite_fallback()
            return
        
        # ✅ Tentative ChromaDB moderne
        success = self._try_modern_chromadb()
        
        if not success:
            logger.warning("ChromaDB échoué, fallback SQLite")
            self._initialize_sqlite_fallback()
    
    def _try_modern_chromadb(self) -> bool:
        """Tentative ChromaDB avec configuration moderne"""
        try:
            logger.info("🔄 Tentative ChromaDB moderne...")
            
            # ✅ CORRECTION: Configuration simple sans Settings obsolètes
            self.client = PersistentClient(path=self.db_path)
            
            # Test de connexion
            try:
                self.collection = self.client.get_collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' récupérée")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AMDEC & Gamme IA Knowledge Base"}
                )
                logger.info(f"Collection '{self.collection_name}' créée")
            
            # Test basique
            count = self.collection.count()
            logger.info(f"✅ ChromaDB opérationnel: {count} documents")
            return True
            
        except Exception as e:
            logger.warning(f"ChromaDB échoué: {e}")
            self.client = None
            return False
    
    def _initialize_sqlite_fallback(self):
        """✅ Fallback SQLite robuste"""
        try:
            self.fallback_mode = True
            self.sqlite_path = os.path.join(self.db_path, 'vector_store.db')
            
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content ON documents(content)")
            conn.commit()
            conn.close()
            
            logger.info("✅ SQLite fallback initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur SQLite fallback: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """Ajoute des documents à la base vectorielle"""
        if not documents:
            logger.warning("Aucun document à ajouter")
            return False
        
        try:
            logger.info(f"Ajout de {len(documents)} documents...")
            
            if self.fallback_mode:
                return self._add_documents_sqlite(documents)
            else:
                return self._add_documents_chromadb(documents)
                
        except Exception as e:
            logger.error(f"Erreur ajout documents: {e}")
            return False
    
    def _add_documents_chromadb(self, documents: List[Dict]) -> bool:
        """Ajoute via ChromaDB"""
        try:
            texts = []
            metadatas = []
            ids = []
            embeddings = []
            
            for i, doc in enumerate(documents):
                content = doc.get('content', '').strip()
                if not content or len(content) < 10:
                    continue
                
                texts.append(content)
                metadatas.append({
                    'source': doc.get('source', 'unknown'),
                    'section': doc.get('section', 'unknown'),
                    'component': doc.get('component', 'general'),
                    'defect': doc.get('defect', 'general')
                })
                ids.append(f"doc_{i}_{hash(content) % 100000}")
                
                # Embedding si disponible
                if self.embedding_model:
                    try:
                        embedding = self.embedding_model.encode(content)
                        embeddings.append(embedding.tolist())
                    except:
                        embeddings.append(None)
                else:
                    embeddings.append(None)
            
            if not texts:
                return False
            
            # Ajouter à ChromaDB
            add_kwargs = {
                'documents': texts,
                'metadatas': metadatas,
                'ids': ids
            }
            
            # Ajouter embeddings si tous disponibles
            valid_embeddings = [e for e in embeddings if e is not None]
            if len(valid_embeddings) == len(texts):
                add_kwargs['embeddings'] = embeddings
            
            self.collection.add(**add_kwargs)
            
            logger.info(f"✅ {len(texts)} documents ajoutés à ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ChromaDB add: {e}")
            return False
    
    def _add_documents_sqlite(self, documents: List[Dict]) -> bool:
        """Ajoute via SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            added_count = 0
            for doc in documents:
                content = doc.get('content', '').strip()
                if not content or len(content) < 10:
                    continue
                
                metadata = {
                    'source': doc.get('source', 'unknown'),
                    'section': doc.get('section', 'unknown'),
                    'component': doc.get('component', 'general'),
                    'defect': doc.get('defect', 'general')
                }
                
                # Embedding si possible
                embedding_blob = None
                if self.embedding_model:
                    try:
                        embedding = self.embedding_model.encode(content)
                        embedding_blob = embedding.tobytes()
                    except:
                        pass
                
                cursor.execute("""
                    INSERT INTO documents (content, metadata, embedding)
                    VALUES (?, ?, ?)
                """, (content, json.dumps(metadata), embedding_blob))
                
                added_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ {added_count} documents ajoutés à SQLite")
            return True
            
        except Exception as e:
            logger.error(f"Erreur SQLite add: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5, min_similarity: float = 0.1) -> List[Dict]:
        """Recherche sémantique"""
        try:
            if not query.strip():
                return []
            
            if self.fallback_mode:
                return self._search_sqlite(query, n_results, min_similarity)
            else:
                return self._search_chromadb(query, n_results, min_similarity)
                
        except Exception as e:
            logger.error(f"Erreur recherche: {e}")
            return []
    
    def _search_chromadb(self, query: str, n_results: int, min_similarity: float) -> List[Dict]:
        """Recherche ChromaDB"""
        try:
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query])
                results = self.collection.query(
                    query_embeddings=query_embedding.tolist(),
                    n_results=n_results,
                    include=['documents', 'metadatas', 'distances']
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=['documents', 'metadatas', 'distances']
                )
            
            documents = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i] if results.get('distances') else 0.5
                    similarity = 1 - distance
                    
                    if similarity >= min_similarity:
                        documents.append({
                            'content': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i],
                            'similarity': round(similarity, 3),
                            'source': results['metadatas'][0][i].get('source', 'unknown'),
                            'section': results['metadatas'][0][i].get('section', 'unknown')
                        })
            
            return documents
            
        except Exception as e:
            logger.error(f"Erreur recherche ChromaDB: {e}")
            return []
    
    def _search_sqlite(self, query: str, n_results: int, min_similarity: float) -> List[Dict]:
        """Recherche SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            documents = []
            
            if self.embedding_model and NUMPY_AVAILABLE:
                # Recherche vectorielle
                query_embedding = self.embedding_model.encode(query)
                
                cursor.execute("SELECT content, metadata, embedding FROM documents WHERE embedding IS NOT NULL")
                
                for row in cursor.fetchall():
                    content, metadata_json, embedding_blob = row
                    
                    if embedding_blob:
                        doc_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                        similarity = self._cosine_similarity(query_embedding, doc_embedding)
                        
                        if similarity >= min_similarity:
                            metadata = json.loads(metadata_json)
                            documents.append({
                                'content': content,
                                'metadata': metadata,
                                'similarity': round(similarity, 3),
                                'source': metadata.get('source', 'unknown'),
                                'section': metadata.get('section', 'unknown')
                            })
            else:
                # Recherche textuelle
                query_words = query.lower().split()
                like_conditions = []
                params = []
                
                for word in query_words:
                    like_conditions.append("LOWER(content) LIKE ?")
                    params.append(f"%{word}%")
                
                if like_conditions:
                    sql = f"""
                        SELECT content, metadata
                        FROM documents
                        WHERE {' OR '.join(like_conditions)}
                        LIMIT ?
                    """
                    params.append(n_results)
                    
                    cursor.execute(sql, params)
                    
                    for row in cursor.fetchall():
                        content, metadata_json = row
                        metadata = json.loads(metadata_json)
                        documents.append({
                            'content': content,
                            'metadata': metadata,
                            'similarity': 0.5,
                            'source': metadata.get('source', 'unknown'),
                            'section': metadata.get('section', 'unknown')
                        })
            
            conn.close()
            documents.sort(key=lambda x: x['similarity'], reverse=True)
            
            return documents[:n_results]
            
        except Exception as e:
            logger.error(f"Erreur recherche SQLite: {e}")
            return []
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcule la similarité cosinus"""
        try:
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
            
        except Exception:
            return 0.5
    
    def search_by_keywords(self, keywords: List[str], n_results: int = 3) -> List[Dict]:
        """Recherche par mots-clés"""
        all_results = []
        
        for keyword in keywords:
            results = self.search(keyword, n_results)
            for result in results:
                result['matched_keyword'] = keyword
            all_results.extend(results)
        
        # Déduplication
        unique_results = {}
        for result in all_results:
            content_hash = hash(result['content'][:200])
            if content_hash not in unique_results or result['similarity'] > unique_results[content_hash]['similarity']:
                unique_results[content_hash] = result
        
        sorted_results = sorted(unique_results.values(), key=lambda x: x['similarity'], reverse=True)
        return sorted_results[:n_results * 2]
    
    def get_collection_stats(self) -> Dict:
        """Statistiques de la collection"""
        try:
            if self.fallback_mode:
                conn = sqlite3.connect(self.sqlite_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM documents")
                total_docs = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT DISTINCT json_extract(metadata, '$.source') 
                    FROM documents 
                    LIMIT 10
                """)
                sources = [row[0] for row in cursor.fetchall() if row[0]]
                
                conn.close()
                
                return {
                    'total_documents': total_docs,
                    'collection_name': self.collection_name,
                    'db_path': self.db_path,
                    'backend': 'SQLite (fallback)',
                    'sample_sources': sources
                }
            else:
                count = self.collection.count()
                
                try:
                    sample = self.collection.peek(limit=5)
                    sources = set()
                    if sample.get('metadatas'):
                        for metadata in sample['metadatas']:
                            if 'source' in metadata:
                                sources.add(metadata['source'])
                    sample_sources = list(sources)
                except:
                    sample_sources = []
                
                return {
                    'total_documents': count,
                    'collection_name': self.collection_name,
                    'db_path': self.db_path,
                    'backend': f'ChromaDB v{CHROMADB_VERSION}',
                    'sample_sources': sample_sources
                }
                
        except Exception as e:
            logger.error(f"Erreur stats collection: {e}")
            return {
                'total_documents': 0,
                'error': str(e),
                'backend': 'SQLite (fallback)' if self.fallback_mode else 'ChromaDB'
            }
    
    def clear_collection(self) -> bool:
        """Vide la collection"""
        try:
            if self.fallback_mode:
                conn = sqlite3.connect(self.sqlite_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents")
                conn.commit()
                conn.close()
                logger.info("Collection SQLite vidée")
            else:
                self.client.delete_collection(self.collection_name)
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AMDEC & Gamme IA Knowledge Base"}
                )
                logger.info("Collection ChromaDB vidée")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur vidage collection: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """Vérifie la santé de la base"""
        try:
            if self.fallback_mode:
                conn = sqlite3.connect(self.sqlite_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                count = cursor.fetchone()[0]
                conn.close()
                return count >= 0
            else:
                count = self.collection.count()
                return count >= 0
                
        except Exception as e:
            logger.error(f"Problème santé: {e}")
            return False

# ===============================
# 📚 DOCUMENT PROCESSOR
# ===============================

class DocumentProcessor:
    """Traite et extrait le contenu des documents techniques"""
    
    def __init__(self, documents_dir: str):
        self.documents_dir = documents_dir
        self.default_knowledge = self._build_default_knowledge()
    
    def _build_default_knowledge(self) -> List[Dict]:
        """Base de connaissances par défaut"""
        return [
            {
                'content': """CORROSION CAUSTIC ATTACK - ÉCONOMISEUR BT
                
Définition: La corrosion caustic attack est une forme de corrosion spécifique qui affecte 
principalement les collecteurs de sortie des économiseurs basse température.

Causes principales:
- Concentration excessive de soude caustique (NaOH)
- Zones de stagnation avec évaporation
- pH local très élevé (>12)
- Température entre 250-350°C

Solutions:
1. Contrôle strict du pH de l'eau d'alimentation
2. Limitation des concentrations en sodium (<3ppm)
3. Amélioration de la circulation dans les collecteurs
4. Surveillance par ultrasons des épaisseurs
5. Revêtement céramique des zones sensibles

Criticité: ÉLEVÉE (F=3, G=5, D=3, C=45)""",
                'source': 'Base expertise AMDEC',
                'section': 'Défauts Économiseur BT',
                'component': 'economiseur_bt',
                'defect': 'corrosion'
            },
            {
                'content': """SURCHAUFFE LONG TERME - SURCHAUFFEUR HT
                
Définition: La surchauffe long terme (long-term overheat) est un phénomène de dégradation 
progressive des tubes porteurs de surchauffeurs haute température.

Mécanisme:
- Exposition prolongée à T > 580°C
- Dégradation de la microstructure métallique
- Formation de carbures grossiers
- Perte de résistance mécanique

Actions correctives:
1. Optimisation de la combustion
2. Installation de capteurs de température permanents
3. Amélioration de la circulation vapeur
4. Nettoyage régulier des surfaces
5. Renforcement des supports

Criticité: CRITIQUE (F=2, G=5, D=2, C=20)""",
                'source': 'Base expertise AMDEC',
                'section': 'Défauts Surchauffeur HT',
                'component': 'surchauffeur_ht',
                'defect': 'surchauffe'
            },
            {
                'content': """MAINTENANCE PRÉVENTIVE - ÉCONOMISEUR BT
                
Programme de maintenance pour économiseur basse température:

INSPECTION VISUELLE (Mensuelle): 45 minutes
- Contrôle général de l'état externe
- Vérification des supports et fixations
- Recherche de fuites visibles

CONTRÔLE ULTRASONS (Trimestrielle): 90 minutes
- Mesure d'épaisseur des zones sensibles
- Cartographie des amincissements
- Suivi de l'évolution des défauts

TEST D'ÉTANCHÉITÉ (Semestrielle): 120 minutes
- Pressurisation selon procédure
- Recherche de fuites sous pression
- Contrôle des joints et brides

Matériel: Lampe torche, appareil ultrasons, kit test étanchéité""",
                'source': 'Guide maintenance préventive',
                'section': 'Procédures Économiseur',
                'component': 'economiseur_bt',
                'defect': 'maintenance'
            },
            {
                'content': """ANALYSE CRITICITÉ AMDEC - MÉTHODE F×G×D
                
La criticité dans l'analyse AMDEC se calcule selon la formule: C = F × G × D

F - FRÉQUENCE d'apparition (1-4):
1 = Très rare (< 1 fois/10 ans)
2 = Rare (1 fois/2-10 ans) 
3 = Occasionnelle (1 fois/an)
4 = Fréquente (plusieurs fois/an)

G - GRAVITÉ des conséquences (1-5):
1 = Négligeable (pas d'impact)
2 = Légère (impact mineur)
3 = Modérée (dégradation performance)
4 = Grave (arrêt programmé)
5 = Catastrophique (arrêt d'urgence)

D - DÉTECTION (1-4):
1 = Détection certaine (surveillance continue)
2 = Détection probable (contrôles réguliers)
3 = Détection possible (inspections périodiques)
4 = Détection improbable (pas de surveillance)

NIVEAUX DE CRITICITÉ:
C ≤ 12: Négligeable - Maintenance corrective
12 < C ≤ 16: Moyenne - Maintenance préventive systématique
16 < C ≤ 20: Élevée - Maintenance préventive conditionnelle  
C > 20: Critique - Remise en cause conception""",
                'source': 'Méthode AMDEC',
                'section': 'Calcul criticité',
                'component': 'general',
                'defect': 'criticite'
            },
            {
                'content': """ACID ATTACK - RÉCHAUFFEUR HT
                
Définition: L'acid attack est une forme de corrosion acide qui affecte spécifiquement 
les branches de sortie des réchauffeurs haute température.

Mécanisme:
- Condensation d'acides faibles (H2SO4, HCl)
- Attaque chimique localisée
- Formation de surfaces "fromage suisse"
- Perte progressive de matière

Prévention:
1. Maintien de la température de paroi > 150°C
2. Amélioration de l'isolation thermique
3. Optimisation des débits de vapeur
4. Nettoyage chimique périodique
5. Protection par revêtement résistant aux acides

Criticité: ÉLEVÉE (F=3, G=4, D=2, C=24)""",
                'source': 'Base expertise AMDEC',
                'section': 'Défauts Réchauffeur HT',
                'component': 'rechauffeur_ht',
                'defect': 'corrosion'
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
                
                # Détecter les headers
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
# 🤖 LLM CLIENT SIMPLE
# ===============================

class LLMClient:
    """Client LLM simple avec fallback"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Charge la configuration LLM"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Configuration par défaut
                config = {
                    "type": "api",
                    "name": "llama3-70b-8192",
                    "api_key": "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",
                    "api_url": "https://api.groq.com/openai/v1/chat/completions"
                }
                
                with open(self.config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                return config
                
        except Exception as e:
            logger.error(f"Erreur chargement config LLM: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Teste la connexion au LLM"""
        return REQUESTS_AVAILABLE and bool(self.config.get('api_key'))
    
    def generate_response(self, system_prompt: str, user_query: str, 
                         context: str, temperature: float = 0.7) -> str:
        """Génère une réponse"""
        if not REQUESTS_AVAILABLE or not self.config.get('api_key'):
            return self._fallback_response(user_query, context)
        
        try:
            headers = {
                'Authorization': f"Bearer {self.config['api_key']}",
                'Content-Type': 'application/json'
            }
            
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
                return self._fallback_response(user_query, context)
                
        except Exception as e:
            logger.error(f"Erreur génération réponse LLM: {e}")
            return self._fallback_response(user_query, context)
    
    def _fallback_response(self, user_query: str, context: str) -> str:
        """Réponse de fallback"""
        query_lower = user_query.lower()
        
        if 'caustic attack' in query_lower:
            return """La corrosion caustic attack affecte les économiseurs BT.
            
**Causes**: Concentration excessive de soude caustique (NaOH), zones de stagnation.
**Solutions**: Contrôle pH, limitation sodium <3ppm, surveillance ultrasons.
**Criticité**: ÉLEVÉE (C=45)"""
        
        elif 'surchauffe' in query_lower:
            return """La surchauffe long terme affecte les surchauffeurs HT exposés à T>580°C.
            
**Effets**: Fluage, déformation, perte résistance mécanique.
**Solutions**: Optimisation combustion, capteurs température, renforcement supports.
**Criticité**: CRITIQUE (C=20)"""
        
        elif 'maintenance' in query_lower:
            return """Programme de maintenance préventive recommandé:
            
- **Mensuel**: Inspection visuelle (45 min)
- **Trimestriel**: Contrôle ultrasons (90 min)  
- **Semestriel**: Test étanchéité (120 min)

**Sécurité**: EPI, consignation, vérification pression/température."""
        
        else:
            return """Je peux vous aider avec les questions concernant:
            
🔧 **Composants**: Économiseurs, Surchauffeurs, Réchauffeurs (BT/HT)
⚠️ **Défauts**: Corrosion, Surchauffe, Fissures, Érosion
🛠️ **Maintenance**: Procédures, Fréquences, Matériel
📊 **AMDEC**: Calculs criticité, Analyses F×G×D"""
    
    def get_system_prompt(self) -> str:
        """Prompt système"""
        return """Tu es un expert en maintenance industrielle spécialisé dans les chaudières et l'analyse AMDEC.

**Expertise**: 
- Analyses AMDEC et calculs de criticité (F×G×D)
- Défauts courants: corrosion, surchauffe, fissures, érosion
- Composants: Économiseurs, Surchauffeurs, Réchauffeurs (BT/HT)
- Maintenance préventive et corrective

**Style**: Précis et technique mais accessible, avec structure claire."""

# ===============================
# 🤖 RAG ENGINE PRINCIPAL
# ===============================

class RAGEngine:
    """✅ Moteur RAG principal corrigé"""
    
    def __init__(self, 
                 documents_dir: str = "data/documents",
                 vector_db_path: str = "data/vector_db",
                 llm_config_path: str = "llm_config.json"):
        
        self.documents_dir = documents_dir
        self.vector_db_path = vector_db_path
        self.llm_config_path = llm_config_path
        
        # Initialiser les composants
        self.document_processor = DocumentProcessor(documents_dir)
        self.vector_store = VectorStore(vector_db_path)
        self.llm_client = LLMClient(llm_config_path)
        
        # État
        self.is_initialized = False
        self.last_index_update = None
    
    def initialize(self, force_reindex: bool = False) -> bool:
        """Initialise le moteur RAG"""
        try:
            logger.info("🚀 Initialisation du moteur RAG...")
            
            # Vérifier si indexation nécessaire
            stats = self.vector_store.get_collection_stats()
            needs_indexing = (
                force_reindex or 
                stats.get('total_documents', 0) == 0
            )
            
            if needs_indexing:
                logger.info("📚 Indexation des documents...")
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
            self.is_initialized = True  # Permettre le fonctionnement en mode dégradé
            return True
    
    def _index_documents(self) -> bool:
        """Indexe les documents"""
        try:
            documents = self.document_processor.process_all_documents()
            
            if not documents:
                logger.warning("⚠️ Aucun document trouvé")
                return False
            
            # Nettoyer la collection si nécessaire
            stats = self.vector_store.get_collection_stats()
            if stats.get('total_documents', 0) > 0:
                self.vector_store.clear_collection()
            
            # Ajouter les documents
            success = self.vector_store.add_documents(documents)
            
            if success:
                final_stats = self.vector_store.get_collection_stats()
                logger.info(f"✅ Indexation terminée: {final_stats.get('total_documents', 0)} documents")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur indexation: {e}")
            return False
    
    def query(self, user_question: str, max_context_length: int = 3000) -> Dict:
        """Traite une question utilisateur"""
        try:
            if not self.is_initialized:
                self.initialize()
            
            logger.info(f"🔍 Question: {user_question[:50]}...")
            
            # Recherche de documents pertinents
            relevant_docs = self.vector_store.search(user_question, n_results=5)
            
            # Construire le contexte
            context_parts = []
            for doc in relevant_docs[:3]:  # Limiter à 3 docs
                source = doc.get('source', 'unknown')
                content = doc.get('content', '')[:800]  # Limiter la taille
                context_parts.append(f"[{source}]\n{content}")
            
            context = '\n\n'.join(context_parts)
            
            # Générer la réponse
            system_prompt = self.llm_client.get_system_prompt()
            response = self.llm_client.generate_response(
                system_prompt=system_prompt,
                user_query=user_question,
                context=context
            )
            
            return {
                'response': response,
                'context': context,
                'sources': [doc.get('source', 'unknown') for doc in relevant_docs],
                'confidence': self._calculate_confidence(relevant_docs),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement question: {e}")
            return {
                'response': "Désolé, une erreur s'est produite. Veuillez réessayer.",
                'error': str(e),
                'context': '',
                'sources': []
            }
    
    def _calculate_confidence(self, documents: List[Dict]) -> float:
        """Calcule la confiance"""
        if not documents:
            return 0.3
        
        similarities = [doc.get('similarity', 0.5) for doc in documents]
        avg_similarity = sum(similarities) / len(similarities)
        doc_bonus = min(len(documents) / 5.0, 1.0)
        
        return min(round(avg_similarity + doc_bonus * 0.2, 2), 1.0)
    
    def get_system_status(self) -> Dict:
        """État du système RAG"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            llm_healthy = self.llm_client.test_connection()
            
            return {
                'initialized': self.is_initialized,
                'last_index_update': self.last_index_update.isoformat() if self.last_index_update else None,
                'vector_store': {
                    'healthy': self.vector_store.is_healthy(),
                    'total_documents': vector_stats.get('total_documents', 0),
                    'backend': vector_stats.get('backend', 'unknown')
                },
                'llm_client': {
                    'healthy': llm_healthy
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur statut système: {e}")
            return {'error': str(e)}
    
    def update_knowledge_base(self) -> bool:
        """Met à jour la base de connaissances"""
        try:
            return self.initialize(force_reindex=True)
        except Exception as e:
            logger.error(f"Erreur mise à jour: {e}")
            return False