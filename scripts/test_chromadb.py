#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Script de Test et Diagnostic ChromaDB
Résout l'erreur "unable to open database file"
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_chromadb_configurations():
    """Teste différentes configurations ChromaDB"""
    print("🔧 DIAGNOSTIC CHROMADB COMPLET")
    print("=" * 60)
    
    # Test 1: Vérification des dépendances
    print("\n📋 1. VÉRIFICATION DES DÉPENDANCES")
    test_dependencies()
    
    # Test 2: Permissions et chemins
    print("\n📁 2. TEST DES PERMISSIONS")
    test_paths_and_permissions()
    
    # Test 3: Configurations ChromaDB
    print("\n🔬 3. TEST CONFIGURATIONS CHROMADB") 
    test_chromadb_variants()
    
    # Test 4: Test complet avec VectorStore
    print("\n🧪 4. TEST VECTORSTORE COMPLET")
    test_complete_vectorstore()

def test_dependencies():
    """Teste la disponibilité des dépendances"""
    dependencies = {
        'chromadb': False,
        'sentence_transformers': False,
        'numpy': False,
        'sqlite3': True  # Toujours disponible
    }
    
    # ChromaDB
    try:
        import chromadb
        dependencies['chromadb'] = True
        print(f"✅ ChromaDB v{chromadb.__version__}")
        
        # Tester les classes importantes
        try:
            from chromadb import PersistentClient
            print("✅ PersistentClient disponible")
        except ImportError:
            print("⚠️ PersistentClient non disponible (version ancienne)")
            
    except ImportError as e:
        print(f"❌ ChromaDB: {e}")
    
    # SentenceTransformers
    try:
        from sentence_transformers import SentenceTransformer
        dependencies['sentence_transformers'] = True
        print("✅ SentenceTransformers disponible")
    except ImportError as e:
        print(f"❌ SentenceTransformers: {e}")
    
    # NumPy
    try:
        import numpy as np
        dependencies['numpy'] = True
        print(f"✅ NumPy v{np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
    
    return dependencies

def test_paths_and_permissions():
    """Teste les chemins et permissions"""
    test_paths = [
        "data/vector_db",
        "data/test_chromadb",
        "./chromadb_test",
        tempfile.gettempdir() + "/chromadb_test"
    ]
    
    for path in test_paths:
        print(f"\n🔍 Test chemin: {path}")
        
        try:
            # Créer le répertoire
            abs_path = os.path.abspath(path)
            os.makedirs(abs_path, exist_ok=True)
            print(f"  📁 Répertoire créé: {abs_path}")
            
            # Test d'écriture
            test_file = os.path.join(abs_path, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test content')
            
            # Test de lecture
            with open(test_file, 'r') as f:
                content = f.read()
            
            os.remove(test_file)
            print("  ✅ Lecture/écriture: OK")
            
            # Test permissions
            try:
                if os.name != 'nt':  # Unix/Linux
                    os.chmod(abs_path, 0o755)
                print("  ✅ Permissions: OK")
            except Exception as e:
                print(f"  ⚠️ Permissions: {e}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {e}")

def test_chromadb_variants():
    """Teste différentes variantes de configuration ChromaDB"""
    
    try:
        import chromadb
        from chromadb import PersistentClient
    except ImportError:
        print("❌ ChromaDB non disponible")
        return
    
    test_dir = "data/chromadb_variants_test"
    
    # Variante 1: PersistentClient simple
    print("\n🔬 Variante 1: PersistentClient simple")
    test_variant_1(test_dir + "/variant1")
    
    # Variante 2: PersistentClient avec settings
    print("\n🔬 Variante 2: PersistentClient avec settings")
    test_variant_2(test_dir + "/variant2")
    
    # Variante 3: Répertoire temporaire
    print("\n🔬 Variante 3: Répertoire temporaire")
    test_variant_3()
    
    # Variante 4: Client en mémoire (si supporté)
    print("\n🔬 Variante 4: Client en mémoire")
    test_variant_4()

def test_variant_1(db_path):
    """Test PersistentClient simple"""
    try:
        from chromadb import PersistentClient
        
        # Nettoyer si existe
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        
        os.makedirs(db_path, exist_ok=True)
        
        # Créer client
        client = PersistentClient(path=db_path)
        
        # Test basique
        collection = client.create_collection("test_collection")
        collection.add(
            documents=["Test document"],
            ids=["test_1"]
        )
        
        count = collection.count()
        print(f"  ✅ Succès - {count} document(s)")
        
        # Nettoyer
        client.delete_collection("test_collection")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Échec: {e}")
        return False

def test_variant_2(db_path):
    """Test PersistentClient avec settings"""
    try:
        from chromadb import PersistentClient
        from chromadb.config import Settings
        
        # Nettoyer si existe
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        
        os.makedirs(db_path, exist_ok=True)
        
        # Settings explicites
        settings = Settings(
            persist_directory=db_path,
            anonymized_telemetry=False
        )
        
        # Créer client
        client = PersistentClient(path=db_path, settings=settings)
        
        # Test basique
        collection = client.create_collection("test_collection_2")
        collection.add(
            documents=["Test document with settings"],
            ids=["test_2"]
        )
        
        count = collection.count()
        print(f"  ✅ Succès avec settings - {count} document(s)")
        
        # Nettoyer
        client.delete_collection("test_collection_2")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Échec avec settings: {e}")
        return False

def test_variant_3():
    """Test avec répertoire temporaire"""
    try:
        from chromadb import PersistentClient
        
        # Créer répertoire temporaire
        temp_dir = tempfile.mkdtemp(prefix='chromadb_temp_')
        print(f"  📁 Répertoire temporaire: {temp_dir}")
        
        # Créer client
        client = PersistentClient(path=temp_dir)
        
        # Test basique
        collection = client.create_collection("temp_collection")
        collection.add(
            documents=["Temporary test document"],
            ids=["temp_1"]
        )
        
        count = collection.count()
        print(f"  ✅ Succès temporaire - {count} document(s)")
        
        # Nettoyer
        client.delete_collection("temp_collection")
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Échec temporaire: {e}")
        return False

def test_variant_4():
    """Test client en mémoire"""
    try:
        import chromadb
        
        # Essayer client en mémoire
        client = chromadb.Client()
        
        # Test basique
        collection = client.create_collection("memory_collection")
        collection.add(
            documents=["In-memory test document"],
            ids=["mem_1"]
        )
        
        count = collection.count()
        print(f"  ✅ Succès en mémoire - {count} document(s)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Échec mémoire: {e}")
        return False

def test_complete_vectorstore():
    """Teste le VectorStore complet"""
    try:
        # Importer le VectorStore corrigé
        sys.path.append('.')
        from rag.vector_store import VectorStore

        
        print("📦 Import VectorStore: ✅")
        
        # Initialiser avec un chemin de test
        test_path = "data/test_final_vectorstore"
        vs = VectorStore(db_path=test_path, collection_name="test_final")
        
        print(f"🔧 Initialisation: ✅")
        print(f"📊 Mode fallback: {vs.fallback_mode}")
        
        # Debug info
        debug_info = vs.get_debug_info()
        print(f"🔍 Debug info:")
        for key, value in debug_info.items():
            print(f"  {key}: {value}")
        
        # Test d'ajout de documents
        test_docs = [
            {
                'content': 'Test de corrosion sur économiseur BT avec caustic attack',
                'source': 'test_final.txt',
                'section': 'Test section',
                'component': 'economiseur_bt',
                'defect': 'corrosion'
            },
            {
                'content': 'Surchauffe long terme des tubes porteurs surchauffeur HT',
                'source': 'test_final2.txt',
                'section': 'Test section 2',
                'component': 'surchauffeur_ht', 
                'defect': 'surchauffe'
            },
            {
                'content': 'Maintenance préventive des réchauffeurs avec inspection ultrasons',
                'source': 'test_final3.txt',
                'section': 'Test section 3',
                'component': 'rechauffeur_ht',
                'defect': 'maintenance'
            }
        ]
        
        success = vs.add_documents(test_docs)
        print(f"📝 Ajout documents: {'✅' if success else '❌'}")
        
        # Statistiques
        stats = vs.get_collection_stats()
        print(f"📊 Stats: {stats}")
        
        # Tests de recherche
        queries = [
            "corrosion économiseur",
            "surchauffe tube",
            "maintenance inspection",
            "caustic attack",
            "ultrasons"
        ]
        
        print(f"\n🔍 Tests de recherche:")
        for query in queries:
            results = vs.search(query, n_results=2)
            print(f"  '{query}': {len(results)} résultats")
            for i, result in enumerate(results[:1]):
                similarity = result.get('similarity', 0)
                source = result.get('source', 'unknown')
                print(f"    {i+1}. {source} (sim: {similarity:.3f})")
        
        # Test par mots-clés
        keywords_results = vs.search_by_keywords(['corrosion', 'maintenance'], n_results=2)
        print(f"🔑 Recherche mots-clés: {len(keywords_results)} résultats")
        
        # Test de santé
        healthy = vs.is_healthy()
        print(f"💚 Santé finale: {'✅ OK' if healthy else '❌ Problème'}")
        
        # Nettoyage final
        vs.clear_collection()
        print(f"🧹 Nettoyage: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur VectorStore complet: {e}")
        import traceback
        traceback.print_exc()
        return False

def install_recommendations():
    """Affiche les recommandations d'installation"""
    print("\n" + "="*60)
    print("📋 RECOMMANDATIONS D'INSTALLATION")
    print("="*60)
    
    print("\n1. 📦 INSTALLATION DES DÉPENDANCES:")
    print("pip install chromadb sentence-transformers numpy")
    print("# ou")
    print("pip install 'chromadb>=0.4.0' 'sentence-transformers>=2.0.0' 'numpy>=1.21.0'")
    
    print("\n2. 🔧 SI PROBLÈMES PERSISTENT:")
    print("# Version spécifique ChromaDB qui fonctionne bien:")
    print("pip install 'chromadb==0.4.24'")
    
    print("\n3. 🐛 DÉPANNAGE AVANCÉ:")
    print("# Nettoyer complètement ChromaDB:")
    print("pip uninstall chromadb -y")
    print("pip install chromadb --no-cache-dir")
    
    print("\n4. 🗂️ PERMISSIONS LINUX/MAC:")
    print("sudo chown -R $USER:$USER data/")
    print("chmod -R 755 data/")
    
    print("\n5. 🔄 FALLBACK SQLite:")
    print("Si ChromaDB ne fonctionne pas, le code utilise automatiquement SQLite")
    print("Aucune configuration supplémentaire nécessaire !")

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU DIAGNOSTIC CHROMADB")
    print("Version Python:", sys.version)
    print("Système:", os.name, sys.platform)
    print()
    
    # Lancer tous les tests
    test_chromadb_configurations()
    
    # Afficher les recommandations
    install_recommendations()
    
    print("\n" + "="*60)
    print("✅ DIAGNOSTIC TERMINÉ")
    print("="*60)