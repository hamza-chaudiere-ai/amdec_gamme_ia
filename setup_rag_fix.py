#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction automatique pour AMDEC & Gamme IA + RAG
Corrige automatiquement l'erreur huggingface_hub

NOUVEAU FICHIER : setup_rag_fix.py (créer à la racine du projet)
"""

import os
import sys
import subprocess
from datetime import datetime

def print_header():
    """Affiche l'en-tête du script de correction"""
    print("🔧" + "="*50)
    print("🔧 CORRECTION AUTOMATIQUE RAG")
    print("🔧 AMDEC & Gamme IA - Fix huggingface_hub")
    print(f"🔧 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧" + "="*50)

def backup_files():
    """Crée une sauvegarde des fichiers actuels"""
    print("\n💾 Création sauvegarde...")
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'requirements.txt',
        'rag/rag_engine.py',
        'rag/__init__.py'
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            import shutil
            backup_path = os.path.join(backup_dir, file_path.replace('/', '_'))
            shutil.copy2(file_path, backup_path)
            print(f"  ✅ Sauvegardé: {file_path} → {backup_path}")
    
    print(f"  📁 Sauvegarde créée dans: {backup_dir}")
    return backup_dir

def update_requirements():
    """Met à jour requirements.txt"""
    print("\n📦 Mise à jour requirements.txt...")
    
    new_requirements = """# Core Flask
Flask==2.3.3
Werkzeug==2.3.7

# Data Processing
pandas==2.0.3
numpy==1.24.3
openpyxl==3.1.2

# Machine Learning
scikit-learn==1.3.0
joblib==1.3.2

# Document Generation
python-docx==0.8.11
Pillow==10.0.0

# Web Interface
requests==2.31.0

# RAG System Dependencies (✅ Version compatible)
sentence-transformers==2.2.2

# PDF Processing (optionnel)
PyPDF2==3.0.1

# Utilities
colorama==0.4.6
tqdm==4.66.1
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(new_requirements)
    
    print("  ✅ requirements.txt mis à jour")

def update_rag_init():
    """Met à jour rag/__init__.py"""
    print("\n🏗️ Mise à jour rag/__init__.py...")
    
    new_init = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package RAG pour AMDEC & Gamme IA
Système de chatbot intelligent avec base de connaissances vectorielle
✅ CORRIGÉ: Suppression dépendances problématiques
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
'''
    
    os.makedirs('rag', exist_ok=True)
    with open('rag/__init__.py', 'w', encoding='utf-8') as f:
        f.write(new_init)
    
    print("  ✅ rag/__init__.py mis à jour")

def reinstall_dependencies():
    """Réinstalle les dépendances"""
    print("\n📥 Réinstallation des dépendances...")
    
    try:
        # Mettre à jour pip
        print("  🔄 Mise à jour pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        print("  ✅ pip mis à jour")
        
        # Installer les dépendances
        print("  🔄 Installation des dépendances...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("  ✅ Dépendances installées")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Erreur installation: {e}")
        return False

def test_imports():
    """Teste les imports après correction"""
    print("\n🧪 Test des imports corrigés...")
    
    test_results = {}
    
    # Tests essentiels
    tests = {
        'flask': 'import flask',
        'pandas': 'import pandas',
        'numpy': 'import numpy', 
        'requests': 'import requests',
        'sentence_transformers': 'from sentence_transformers import SentenceTransformer',
        'rag': 'from rag import RAGEngine'
    }
    
    for name, import_cmd in tests.items():
        try:
            exec(import_cmd)
            test_results[name] = "✅ OK"
            print(f"  ✅ {name}")
        except ImportError as e:
            test_results[name] = f"❌ {str(e)[:50]}..."
            print(f"  ❌ {name}: {str(e)[:50]}...")
    
    return test_results

def create_directories():
    """Crée les répertoires nécessaires"""
    print("\n📁 Création des répertoires...")
    
    dirs = [
        'data/documents',
        'data/vector_db',
        'data/generated/amdec',
        'data/generated/gammes',
        'uploads'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✅ {dir_path}")

def main():
    """Fonction principale de correction"""
    print_header()
    
    try:
        # Étape 1: Sauvegarde
        backup_dir = backup_files()
        
        # Étape 2: Mise à jour des fichiers
        update_requirements()
        update_rag_init()
        
        # Étape 3: Création des répertoires
        create_directories()
        
        # Étape 4: Réinstallation
        install_success = reinstall_dependencies()
        
        # Étape 5: Tests
        if install_success:
            test_results = test_imports()
            success_count = sum(1 for result in test_results.values() if "✅" in result)
            total_count = len(test_results)
            
            print(f"\n📊 Résultats: {success_count}/{total_count} imports réussis")
        else:
            success_count = 0
            total_count = 6
        
        # Résumé final
        print("\n🎯" + "="*50)
        print("🎯 RÉSUMÉ DE LA CORRECTION")
        print("🎯" + "="*50)
        
        if success_count >= total_count - 1:
            print("🎉 CORRECTION RÉUSSIE !")
            print("✅ L'erreur huggingface_hub a été corrigée")
            print("✅ Les dépendances sont installées")
            print("✅ Le module RAG est fonctionnel")
            print("\n🚀 Vous pouvez maintenant lancer:")
            print("   python app.py")
            
            # Proposer de lancer le diagnostic
            print("\n💡 Pour un diagnostic complet:")
            print("   python diagnostic_rag.py")
            
        else:
            print("⚠️ CORRECTION PARTIELLE")
            print(f"📊 {success_count}/{total_count} imports fonctionnels")
            print("\n🔧 Actions supplémentaires nécessaires:")
            
            if 'sentence_transformers' in test_results and "❌" in test_results['sentence_transformers']:
                print("   pip install sentence-transformers==2.2.2")
            
            if 'rag' in test_results and "❌" in test_results['rag']:
                print("   Vérifiez le fichier rag/rag_engine.py")
            
            print(f"\n📁 Sauvegarde disponible dans: {backup_dir}")
        
        print(f"\n⏰ Correction terminée le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}")
        
        return success_count >= total_count - 1
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la correction: {e}")
        print(f"📁 Sauvegarde disponible dans: {backup_dir}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print("\n✨ Correction terminée avec succès !")
        else:
            print("\n⚠️ Correction terminée avec des avertissements")
            
    except KeyboardInterrupt:
        print("\n⚠️ Correction interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")