#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ CORRIGÉ: Magasin Vectoriel ChromaDB Fonctionnel
Résout l'erreur "unable to open database file" avec duckdb+parquet
"""

import os
import sys
import stat
import shutil
import logging
import tempfile
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# ===============================
# 🔧 IMPORTS AVEC GESTION D'ERREURS ROBUSTE
# ===============================

# ChromaDB avec gestion de version
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
    logger.error(f"ChromaDB non disponible: {e}")

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

# Sqlite3 comme fallback
import sqlite3
import json

class VectorStore:
    """
    ✅ Magasin vectoriel robuste avec ChromaDB + fallback SQLite
    Corrige l'erreur "unable to open database file"
    """
    
    def __init__(self, db_path: str = "data/vector_db", collection_name: str = "amdec_knowledge"):
        """
        Initialise le magasin vectoriel avec gestion d'erreurs robuste
        
        Args:
            db_path: Chemin vers la base vectorielle
            collection_name: Nom de la collection
        """
        self.db_path = os.path.abspath(db_path)  # Toujours chemin absolu
        self.collection_name = collection_name
        self.embedding_model = None
        self.client = None
        self.collection = None
        self.fallback_mode = False
        self.sqlite_path = None
        
        # Détection du système
        self.is_windows = os.name == 'nt'
        self.is_linux = sys.platform.startswith('linux')
        
        logger.info(f"🔄 Initialisation VectorStore")
        logger.info(f"📁 Chemin DB: {self.db_path}")
        logger.info(f"🖥️ Système: {'Windows' if self.is_windows else 'Linux/Unix'}")
        
        # Initialisation étape par étape
        self._prepare_directories()
        self._initialize_embedding_model()
        self._initialize_vector_store()
    
    def _prepare_directories(self):
        """Prépare les répertoires avec gestion des permissions"""
        try:
            # Créer le répertoire parent
            parent_dir = os.path.dirname(self.db_path)
            os.makedirs(parent_dir, exist_ok=True)
            
            # Créer le répertoire principal
            os.makedirs(self.db_path, exist_ok=True)
            
            # ✅ CORRECTION: Gestion des permissions spécifique selon l'OS
            if self.is_windows:
                # Windows: Permissions par défaut suffisantes
                logger.info("✅ Windows: Permissions par défaut")
            else:
                # Linux/Unix: Permissions explicites
                try:
                    os.chmod(self.db_path, 0o755)
                    os.chmod(parent_dir, 0o755)
                    logger.info("✅ Linux: Permissions 755 appliquées")
                except Exception as e:
                    logger.warning(f"⚠️ Permissions non modifiables: {e}")
            
            # Tester l'écriture
            test_file = os.path.join(self.db_path, 'test_write.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                logger.info("✅ Test écriture répertoire: OK")
            except Exception as e:
                logger.error(f"❌ Impossible d'écrire dans {self.db_path}: {e}")
                raise
                
        except Exception as e:
            logger.error(f"❌ Erreur préparation répertoires: {e}")
            raise
    
    def _initialize_embedding_model(self):
        """Initialise le modèle d'embeddings avec fallback"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("⚠️ SentenceTransformers non disponible")
            return
        
        try:
            logger.info("🔄 Chargement modèle embeddings...")
            
            # ✅ CORRECTION: Modèle plus léger et compatible
            models_to_try = [
                "all-MiniLM-L6-v2",  # Léger et rapide
                "paraphrase-multilingual-MiniLM-L12-v2",  # Multilingue
                "all-mpnet-base-v2"  # Plus précis mais plus lourd
            ]
            
            for model_name in models_to_try:
                try:
                    self.embedding_model = SentenceTransformer(model_name)
                    logger.info(f"✅ Modèle chargé: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Échec {model_name}: {e}")
                    continue
            
            if not self.embedding_model:
                logger.error("❌ Aucun modèle d'embedding disponible")
                
        except Exception as e:
            logger.error(f"❌ Erreur chargement embeddings: {e}")
            self.embedding_model = None
    
    def _initialize_vector_store(self):
        """Initialise ChromaDB avec fallback SQLite robuste"""
        if not CHROMADB_AVAILABLE:
            logger.warning("⚠️ ChromaDB non disponible, utilisation SQLite")
            self._initialize_sqlite_fallback()
            return
        
        # ✅ CORRECTION: Tentatives multiples avec configurations différentes
        success = False
        
        # Configuration 1: PersistentClient moderne (recommandé)
        if not success:
            success = self._try_modern_chromadb()
        
        # Configuration 2: Client avec Settings explicites
        if not success:
            success = self._try_legacy_chromadb()
        
        # Configuration 3: Répertoire temporaire
        if not success:
            success = self._try_temp_chromadb()
        
        # Fallback: SQLite
        if not success:
            logger.warning("⚠️ ChromaDB inutilisable, fallback SQLite")
            self._initialize_sqlite_fallback()
    
    def _try_modern_chromadb(self) -> bool:
        """Tentative avec PersistentClient moderne"""
        try:
            logger.info("🔄 Tentative ChromaDB moderne...")
            
            # ✅ CORRECTION: Configuration moderne sans Settings obsolètes
            self.client = PersistentClient(path=self.db_path)
            
            # Tester la connexion
            self._test_chromadb_connection()
            
            logger.info("✅ ChromaDB moderne: Succès")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ ChromaDB moderne échoué: {e}")
            self.client = None
            return False
    
    def _try_legacy_chromadb(self) -> bool:
        """Tentative avec configuration legacy"""
        try:
            logger.info("🔄 Tentative ChromaDB legacy...")
            
            # ✅ CORRECTION: Settings compatibles avec anciennes versions
            settings = Settings(
                persist_directory=self.db_path,
                anonymized_telemetry=False
            )
            
            # Essayer d'abord PersistentClient
            try:
                self.client = PersistentClient(path=self.db_path, settings=settings)
            except TypeError:
                # Version plus ancienne
                self.client = chromadb.Client(settings=settings)
            
            self._test_chromadb_connection()
            
            logger.info("✅ ChromaDB legacy: Succès")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ ChromaDB legacy échoué: {e}")
            self.client = None
            return False
    
    def _try_temp_chromadb(self) -> bool:
        """Tentative avec répertoire temporaire"""
        try:
            logger.info("🔄 Tentative ChromaDB temporaire...")
            
            # Créer un répertoire temporaire
            temp_dir = tempfile.mkdtemp(prefix='chromadb_')
            
            self.client = PersistentClient(path=temp_dir)
            self._test_chromadb_connection()
            
            # Si succès, déplacer vers répertoire final
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
            shutil.move(temp_dir, self.db_path)
            
            # Reconnecter au répertoire final
            self.client = PersistentClient(path=self.db_path)
            self._test_chromadb_connection()
            
            logger.info("✅ ChromaDB temporaire: Succès")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ ChromaDB temporaire échoué: {e}")
            self.client = None
            return False
    
    def _test_chromadb_connection(self):
        """Teste la connexion ChromaDB"""
        try:
            # Tester la création/récupération de collection
            try:
                self.collection = self.client.get_collection(self.collection_name)
                logger.info(f"📂 Collection '{self.collection_name}' récupérée")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AMDEC & Gamme IA Knowledge Base"}
                )
                logger.info(f"📂 Collection '{self.collection_name}' créée")
            
            # Test basique
            count = self.collection.count()
            logger.info(f"📊 Collection contient {count} documents")
            
        except Exception as e:
            logger.error(f"❌ Test connexion ChromaDB échoué: {e}")
            raise
    
    def _initialize_sqlite_fallback(self):
        """Initialise le fallback SQLite"""
        try:
            self.fallback_mode = True
            self.sqlite_path = os.path.join(self.db_path, 'vector_store.db')
            
            # Créer la base SQLite
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
        """
        Ajoute des documents à la base vectorielle
        
        Args:
            documents: Liste de dictionnaires avec 'content', 'source', etc.
            
        Returns:
            True si succès
        """
        if not documents:
            logger.warning("⚠️ Aucun document à ajouter")
            return False
        
        try:
            logger.info(f"📝 Ajout de {len(documents)} documents...")
            
            if self.fallback_mode:
                return self._add_documents_sqlite(documents)
            else:
                return self._add_documents_chromadb(documents)
                
        except Exception as e:
            logger.error(f"❌ Erreur ajout documents: {e}")
            return False
    
    def _add_documents_chromadb(self, documents: List[Dict]) -> bool:
        """Ajoute des documents via ChromaDB"""
        try:
            # Préparer les données
            texts = []
            metadatas = []
            ids = []
            embeddings = []
            
            for i, doc in enumerate(documents):
                content = doc.get('content', '').strip()
                if not content or len(content) < 10:
                    continue
                
                # Texte et métadonnées
                texts.append(content)
                metadatas.append({
                    'source': doc.get('source', 'unknown'),
                    'section': doc.get('section', 'unknown'),
                    'component': doc.get('component', 'general'),
                    'defect': doc.get('defect', 'general'),
                    'length': len(content)
                })
                ids.append(f"doc_{i}_{hash(content) % 100000}")
                
                # Générer embedding si possible
                if self.embedding_model:
                    try:
                        embedding = self.embedding_model.encode(content)
                        embeddings.append(embedding.tolist())
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur embedding: {e}")
                        embeddings.append(None)
                else:
                    embeddings.append(None)
            
            if not texts:
                logger.warning("⚠️ Aucun contenu valide")
                return False
            
            # Ajouter à ChromaDB
            add_kwargs = {
                'documents': texts,
                'metadatas': metadatas,
                'ids': ids
            }
            
            # Ajouter embeddings seulement si disponibles
            valid_embeddings = [e for e in embeddings if e is not None]
            if len(valid_embeddings) == len(texts):
                add_kwargs['embeddings'] = embeddings
            
            self.collection.add(**add_kwargs)
            
            logger.info(f"✅ {len(texts)} documents ajoutés à ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur ChromaDB add: {e}")
            return False
    
    def _add_documents_sqlite(self, documents: List[Dict]) -> bool:
        """Ajoute des documents via SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            added_count = 0
            for doc in documents:
                content = doc.get('content', '').strip()
                if not content or len(content) < 10:
                    continue
                
                # Métadonnées JSON
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
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur embedding SQLite: {e}")
                
                # Insérer en base
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
            logger.error(f"❌ Erreur SQLite add: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5, min_similarity: float = 0.1) -> List[Dict]:
        """
        Recherche sémantique dans la base vectorielle
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats maximum
            min_similarity: Similarité minimale
            
        Returns:
            Liste de documents pertinents
        """
        try:
            if not query.strip():
                return []
            
            if self.fallback_mode:
                return self._search_sqlite(query, n_results, min_similarity)
            else:
                return self._search_chromadb(query, n_results, min_similarity)
                
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {e}")
            return []
    
    def _search_chromadb(self, query: str, n_results: int, min_similarity: float) -> List[Dict]:
        """Recherche via ChromaDB"""
        try:
            # Recherche avec embedding si disponible
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query])
                
                results = self.collection.query(
                    query_embeddings=query_embedding.tolist(),
                    n_results=n_results,
                    include=['documents', 'metadatas', 'distances']
                )
            else:
                # Recherche textuelle
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=['documents', 'metadatas', 'distances']
                )
            
            # Formater les résultats
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
            
            logger.info(f"🔍 ChromaDB: {len(documents)} résultats pour '{query[:50]}...'")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche ChromaDB: {e}")
            return []
    
    def _search_sqlite(self, query: str, n_results: int, min_similarity: float) -> List[Dict]:
        """Recherche via SQLite avec similarité vectorielle ou textuelle"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            documents = []
            
            # Si embeddings disponibles
            if self.embedding_model:
                query_embedding = self.embedding_model.encode(query)
                
                cursor.execute("""
                    SELECT content, metadata, embedding
                    FROM documents
                    WHERE embedding IS NOT NULL
                """)
                
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
                # Recherche textuelle simple
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
                            'similarity': 0.5,  # Similarité par défaut
                            'source': metadata.get('source', 'unknown'),
                            'section': metadata.get('section', 'unknown')
                        })
            
            conn.close()
            
            # Trier par similarité
            documents.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"🔍 SQLite: {len(documents)} résultats pour '{query[:50]}...'")
            return documents[:n_results]
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche SQLite: {e}")
            return []
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcule la similarité cosinus"""
        if not NUMPY_AVAILABLE:
            return 0.5
        
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
        """Recherche par mots-clés spécifiques"""
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
        
        # Trier par similarité
        sorted_results = sorted(unique_results.values(), key=lambda x: x['similarity'], reverse=True)
        
        return sorted_results[:n_results * 2]
    
    def get_collection_stats(self) -> Dict:
        """Retourne les statistiques de la collection"""
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
                
                # Échantillon de métadonnées
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
            logger.error(f"❌ Erreur stats: {e}")
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
                logger.info("✅ Collection SQLite vidée")
            else:
                self.client.delete_collection(self.collection_name)
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AMDEC & Gamme IA Knowledge Base"}
                )
                logger.info("✅ Collection ChromaDB vidée")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur vidage collection: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """Vérifie la santé de la base vectorielle"""
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
            logger.error(f"❌ Problème santé: {e}")
            return False
    
    def get_debug_info(self) -> Dict:
        """Retourne des informations de debug"""
        return {
            'chromadb_available': CHROMADB_AVAILABLE,
            'chromadb_version': CHROMADB_VERSION,
            'sentence_transformers_available': SENTENCE_TRANSFORMERS_AVAILABLE,
            'numpy_available': NUMPY_AVAILABLE,
            'fallback_mode': self.fallback_mode,
            'db_path': self.db_path,
            'is_windows': self.is_windows,
            'embedding_model': str(self.embedding_model) if self.embedding_model else None,
            'client_type': type(self.client).__name__ if self.client else None,
            'collection_name': self.collection_name,
            'sqlite_path': self.sqlite_path if self.fallback_mode else None
        }


# ===============================
# 🧪 FONCTION DE TEST
# ===============================

def test_vector_store():
    """Teste le VectorStore avec des exemples"""
    logger.info("🧪 Test du VectorStore...")
    
    try:
        # Initialiser
        vs = VectorStore(db_path="data/test_vector_db")
        
        # Afficher les infos de debug
        debug_info = vs.get_debug_info()
        logger.info(f"🔧 Debug info: {debug_info}")
        
        # Documents d'exemple
        test_docs = [
            {
                'content': 'La corrosion caustic attack affecte les économiseurs BT',
                'source': 'test_doc1.txt',
                'section': 'Défauts économiseur',
                'component': 'economiseur_bt',
                'defect': 'corrosion'
            },
            {
                'content': 'Surchauffe long terme des tubes porteurs haute température',
                'source': 'test_doc2.txt', 
                'section': 'Défauts surchauffeur',
                'component': 'surchauffeur_ht',
                'defect': 'surchauffe'
            }
        ]
        
        # Ajouter des documents
        success = vs.add_documents(test_docs)
        logger.info(f"📝 Ajout documents: {'✅ Succès' if success else '❌ Échec'}")
        
        # Statistiques
        stats = vs.get_collection_stats()
        logger.info(f"📊 Stats: {stats}")
        
        # Test de recherche
        results = vs.search("corrosion économiseur", n_results=2)
        logger.info(f"🔍 Recherche: {len(results)} résultats")
        
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. {result['source']} (sim: {result['similarity']:.3f})")
        
        # Test santé
        healthy = vs.is_healthy()
        logger.info(f"💚 Santé: {'✅ OK' if healthy else '❌ Problème'}")
        
        return vs
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        return None


# ===============================
# 🚀 MAIN POUR TEST
# ===============================

if __name__ == "__main__":
    # Configuration du logging pour les tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Lancer le test
    vs = test_vector_store()
    
    if vs:
        print("\n" + "="*50)
        print("✅ VectorStore initialisé avec succès !")
        print(f"📊 Backend: {'SQLite' if vs.fallback_mode else 'ChromaDB'}")
        print(f"📁 Chemin: {vs.db_path}")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ Échec d'initialisation du VectorStore")
        print("="*50)