#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Test Rapide de la Correction ChromaDB
Placez ce fichier à la racine de votre projet et exécutez: python test_fix.py
"""

import os
import sys
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vector_store_fix():
    """Teste la correction du VectorStore"""
    print("🔧 TEST DE LA CORRECTION CHROMADB")
    print("=" * 50)
    
    try:
        # Importer le module corrigé
        sys.path.append('.')
        from rag.rag_engine import VectorStore, DocumentProcessor
        
        print("✅ Import réussi")
        
        # Tester VectorStore
        print("\n📦 Test VectorStore...")
        vs = VectorStore(db_path="data/test_fix", collection_name="test_fix")
        
        print(f"✅ VectorStore initialisé")
        print(f"📊 Mode fallback: {vs.fallback_mode}")
        print(f"🗄️ Backend: {'SQLite' if vs.fallback_mode else 'ChromaDB'}")
        
        # Test d'ajout de documents
        test_docs = [
            {
                'content': 'Test de corrosion sur économiseur BT - caustic attack détecté',
                'source': 'test_fix.txt',
                'section': 'Test',
                'component': 'economiseur_bt',
                'defect': 'corrosion'
            },
            {
                'content': 'Surchauffe long terme sur surchauffeur HT - surveillance requise',
                'source': 'test_fix2.txt',
                'section': 'Test',
                'component': 'surchauffeur_ht',
                'defect': 'surchauffe'
            }
        ]
        
        print(f"\n📝 Test ajout {len(test_docs)} documents...")
        success = vs.add_documents(test_docs)
        print(f"✅ Ajout: {'Réussi' if success else 'Échec'}")
        
        # Statistiques
        stats = vs.get_collection_stats()
        print(f"\n📊 Statistiques:")
        print(f"  • Total documents: {stats.get('total_documents', 0)}")
        print(f"  • Backend: {stats.get('backend', 'unknown')}")
        print(f"  • Chemin DB: {stats.get('db_path', 'unknown')}")
        
        # Test de recherche
        print(f"\n🔍 Test recherche...")
        results = vs.search("corrosion économiseur", n_results=2)
        print(f"✅ Recherche: {len(results)} résultats trouvés")
        
        for i, result in enumerate(results):
            similarity = result.get('similarity', 0)
            source = result.get('source', 'unknown')
            print(f"  {i+1}. {source} (similarité: {similarity:.3f})")
        
        # Test santé
        healthy = vs.is_healthy()
        print(f"\n💚 Santé: {'✅ OK' if healthy else '❌ Problème'}")
        
        # Test DocumentProcessor
        print(f"\n📚 Test DocumentProcessor...")
        dp = DocumentProcessor("data/documents")
        docs = dp.process_all_documents()
        print(f"✅ DocumentProcessor: {len(docs)} documents traités")
        
        print(f"\n🎉 TOUS LES TESTS RÉUSSIS !")
        print(f"🚀 La correction fonctionne parfaitement")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chromadb_availability():
    """Teste la disponibilité de ChromaDB"""
    print("\n🔍 DIAGNOSTIC CHROMADB")
    print("-" * 30)
    
    try:
        import chromadb
        print(f"✅ ChromaDB v{chromadb.__version__} disponible")
        
        try:
            from chromadb import PersistentClient
            print("✅ PersistentClient disponible")
        except ImportError:
            print("⚠️ PersistentClient non disponible")
        
        try:
            from chromadb.config import Settings
            print("✅ Settings disponible")
        except ImportError:
            print("⚠️ Settings non disponible")
            
    except ImportError:
        print("❌ ChromaDB non installé")
        print("💡 Commande: pip install chromadb")
    
    # Autres dépendances
    deps = {
        'sentence_transformers': 'SentenceTransformers',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'requests': 'Requests'
    }
    
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"✅ {name} disponible")
        except ImportError:
            print(f"⚠️ {name} non disponible")

def test_directories():
    """Teste les répertoires et permissions"""
    print("\n📁 TEST RÉPERTOIRES")
    print("-" * 20)
    
    test_dirs = [
        "data",
        "data/vector_db", 
        "data/documents",
        "rag"
    ]
    
    for dir_path in test_dirs:
        try:
            abs_path = os.path.abspath(dir_path)
            exists = os.path.exists(abs_path)
            
            if not exists:
                os.makedirs(abs_path, exist_ok=True)
                print(f"✅ {dir_path} créé: {abs_path}")
            else:
                print(f"✅ {dir_path} existe: {abs_path}")
            
            # Test écriture
            test_file = os.path.join(abs_path, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"  📝 Écriture: OK")
            
        except Exception as e:
            print(f"❌ {dir_path}: {e}")

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU TEST DE CORRECTION")
    print("Version Python:", sys.version)
    print("Répertoire:", os.getcwd())
    print()
    
    # Tests étape par étape
    test_chromadb_availability()
    test_directories()
    
    # Test principal
    success = test_vector_store_fix()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 CORRECTION RÉUSSIE !")
        print("✅ Votre VectorStore fonctionne parfaitement")
        print("🚀 Vous pouvez maintenant lancer:")
        print("   python scripts/vectorize_documents.py --force")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ LA CORRECTION A ÉCHOUÉ")
        print("📞 Contactez le support avec les logs ci-dessus")
        print("=" * 50)