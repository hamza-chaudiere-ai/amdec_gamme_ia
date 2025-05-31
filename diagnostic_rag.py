#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour AMDEC & Gamme IA + RAG
Vérifie l'installation et les dépendances

NOUVEAU FICHIER : diagnostic_rag.py (créer à la racine du projet)
"""

import sys
import os
import logging
from datetime import datetime

def print_header():
    """Affiche l'en-tête du diagnostic"""
    print("🚀" + "="*50)
    print("🚀 DIAGNOSTIC AMDEC & GAMME IA + RAG")
    print("🚀 Version: 1.0.0")
    print(f"🚀 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀" + "="*50)

def test_python_version():
    """Teste la version de Python"""
    print("\n🐍 Test version Python...")
    
    version = sys.version_info
    print(f"  Version détectée: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("  ✅ Version Python compatible")
        return True
    else:
        print("  ❌ Version Python trop ancienne (minimum 3.8 requis)")
        return False

def test_imports():
    """Teste tous les imports nécessaires"""
    print("\n🔍 Test des imports...")
    
    imports_results = {}
    
    # Imports essentiels
    essential_imports = {
        'pandas': 'import pandas as pd',
        'numpy': 'import numpy as np',
        'requests': 'import requests',
        'flask': 'import flask',
        'openpyxl': 'import openpyxl'
    }
    
    # Imports documents
    document_imports = {
        'python-docx': 'import docx',
        'PyPDF2': 'import PyPDF2',
        'Pillow': 'from PIL import Image'
    }
    
    # Imports ML
    ml_imports = {
        'scikit-learn': 'import sklearn',
        'joblib': 'import joblib'
    }
    
    # Import RAG (optionnel)
    rag_imports = {
        'sentence-transformers': 'from sentence_transformers import SentenceTransformer'
    }
    
    all_imports = {
        **essential_imports,
        **document_imports, 
        **ml_imports,
        **rag_imports
    }
    
    for name, import_cmd in all_imports.items():
        try:
            exec(import_cmd)
            if name in essential_imports:
                imports_results[name] = "✅ ESSENTIEL OK"
            elif name in rag_imports:
                imports_results[name] = "✅ RAG OK"
            else:
                imports_results[name] = "✅ OK"
        except ImportError as e:
            if name in essential_imports:
                imports_results[name] = f"❌ CRITIQUE: {str(e)[:50]}..."
            elif name in rag_imports:
                imports_results[name] = f"⚠️ OPTIONNEL: {str(e)[:50]}..."
            else:
                imports_results[name] = f"⚠️ MANQUANT: {str(e)[:50]}..."
    
    # Afficher les résultats
    print("\n📊 Résultats des imports:")
    for module, status in imports_results.items():
        print(f"  {module:20}: {status}")
    
    return imports_results

def test_core_modules():
    """Teste les modules core du projet"""
    print("\n🏗️ Test des modules core...")
    
    core_modules = [
        'core.utils',
        'core.excel_parser', 
        'core.amdec_generator',
        'core.gamme_generator',
        'core.data_trainer'
    ]
    
    core_results = {}
    
    for module in core_modules:
        try:
            __import__(module)
            core_results[module] = "✅ OK"
        except ImportError as e:
            core_results[module] = f"❌ Erreur: {str(e)[:50]}..."
    
    # Test import rag
    try:
        from rag import RAGEngine
        core_results['rag'] = "✅ OK"
    except ImportError as e:
        core_results['rag'] = f"❌ Erreur: {str(e)[:50]}..."
    
    # Afficher les résultats
    for module, status in core_results.items():
        print(f"  {module:20}: {status}")
    
    return core_results

def test_directories():
    """Teste la présence des répertoires nécessaires"""
    print("\n📁 Test des répertoires...")
    
    required_dirs = [
        'data',
        'data/dataset',
        'data/generated',
        'data/generated/amdec',
        'data/generated/gammes',
        'data/documents',
        'data/vector_db',
        'core',
        'ml', 
        'rag',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'templates',
        'uploads'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - Manquant")
            missing_dirs.append(dir_path)
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"    🔧 Créé automatiquement")
            except Exception as e:
                print(f"    ❌ Erreur création: {e}")
    
    return len(missing_dirs) == 0

def test_required_files():
    """Teste la présence des fichiers requis"""
    print("\n📄 Test des fichiers requis...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'core/__init__.py',
        'rag/__init__.py',
        'rag/rag_engine.py',
        'templates/base.html',
        'templates/index.html',
        'templates/amdec.html',
        'templates/gamme.html',
        'templates/chatbot.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Manquant")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_rag_engine():
    """Teste l'initialisation du moteur RAG"""
    print("\n🧠 Test du moteur RAG...")
    
    try:
        from rag import RAGEngine
        print("  ✅ Import RAGEngine réussi")
        
        # Initialiser le moteur
        rag_engine = RAGEngine()
        print("  ✅ RAGEngine créé")
        
        # Tester l'initialisation
        success = rag_engine.initialize()
        if success:
            print("  ✅ Initialisation réussie")
        else:
            print("  ⚠️ Initialisation partiellement réussie")
        
        # Tester le statut
        status = rag_engine.get_system_status()
        docs_count = status.get('vector_store', {}).get('total_documents', 0)
        llm_healthy = status.get('llm_client', {}).get('healthy', False)
        
        print(f"  📊 Documents en base: {docs_count}")
        print(f"  🤖 LLM disponible: {llm_healthy}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur RAG: {e}")
        return False

def test_basic_query():
    """Teste une requête basique au chatbot"""
    print("\n💬 Test requête chatbot...")
    
    try:
        from rag import RAGEngine
        
        rag_engine = RAGEngine()
        rag_engine.initialize()
        
        # Tester une question simple
        test_questions = [
            "Qu'est-ce que la corrosion caustic attack ?",
            "Comment maintenir un économiseur BT ?",
            "Quelle est la criticité d'une fissure ?"
        ]
        
        for i, question in enumerate(test_questions[:1]):  # Tester seulement la première
            print(f"  🔍 Test question {i+1}: {question[:50]}...")
            
            result = rag_engine.query(question)
            
            if result.get('response'):
                response_preview = result['response'][:100].replace('\n', ' ')
                print(f"    ✅ Réponse: {response_preview}...")
                print(f"    📊 Confiance: {result.get('confidence', 0):.2f}")
                print(f"    📚 Sources: {len(result.get('sources', []))}")
                return True
            else:
                print(f"    ❌ Aucune réponse générée")
                return False
                
    except Exception as e:
        print(f"  ❌ Erreur test requête: {e}")
        return False

def test_flask_app():
    """Teste le démarrage de l'application Flask"""
    print("\n🌐 Test application Flask...")
    
    try:
        # Import sans lancer le serveur
        import app
        print("  ✅ Import app.py réussi")
        
        # Vérifier les routes principales
        from flask import Flask
        if hasattr(app, 'app') and isinstance(app.app, Flask):
            print("  ✅ Application Flask créée")
            
            # Lister quelques routes
            routes = [rule.rule for rule in app.app.url_map.iter_rules()]
            main_routes = ['/', '/amdec', '/gamme', '/chatbot']
            
            for route in main_routes:
                if route in routes:
                    print(f"    ✅ Route {route} disponible")
                else:
                    print(f"    ❌ Route {route} manquante")
            
            return True
        else:
            print("  ❌ Application Flask non trouvée")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur Flask: {e}")
        return False

def generate_report(results):
    """Génère un rapport de diagnostic"""
    print("\n📋 GÉNÉRATION DU RAPPORT...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'python_compatible': results.get('python', False),
        'imports_ok': results.get('imports_critical', 0),
        'core_modules_ok': results.get('core_modules', 0), 
        'directories_ok': results.get('directories', False),
        'files_ok': results.get('files', False),
        'rag_ok': results.get('rag', False),
        'chatbot_ok': results.get('chatbot', False),
        'flask_ok': results.get('flask', False)
    }
    
    # Calculer le score global
    total_checks = len([k for k in report.keys() if k != 'timestamp'])
    passed_checks = sum(1 for v in report.values() if v is True or (isinstance(v, int) and v > 0))
    score = (passed_checks / total_checks) * 100
    
    report['global_score'] = score
    
    return report

def main():
    """Fonction principale du diagnostic"""
    print_header()
    
    results = {}
    
    # Test 1: Version Python
    results['python'] = test_python_version()
    
    # Test 2: Imports
    imports_results = test_imports()
    critical_imports = sum(1 for status in imports_results.values() if "✅" in status and "ESSENTIEL" in status)
    results['imports_critical'] = critical_imports
    results['imports_total'] = len(imports_results)
    
    # Test 3: Modules core
    core_results = test_core_modules()
    core_ok = sum(1 for status in core_results.values() if "✅" in status)
    results['core_modules'] = core_ok
    
    # Test 4: Répertoires
    results['directories'] = test_directories()
    
    # Test 5: Fichiers requis
    results['files'] = test_required_files()
    
    # Test 6: Moteur RAG
    results['rag'] = test_rag_engine()
    
    # Test 7: Requête chatbot
    results['chatbot'] = test_basic_query()
    
    # Test 8: Application Flask
    results['flask'] = test_flask_app()
    
    # Générer le rapport final
    report = generate_report(results)
    
    # Afficher le résumé
    print("\n🎯" + "="*50)
    print("🎯 RÉSUMÉ DU DIAGNOSTIC")
    print("🎯" + "="*50)
    
    print(f"📊 Score global: {report['global_score']:.1f}%")
    print(f"🐍 Python: {'✅ OK' if report['python_compatible'] else '❌ Problème'}")
    print(f"📦 Imports critiques: {report['imports_ok']}/5")
    print(f"🏗️ Modules core: {report['core_modules_ok']}/6")
    print(f"📁 Répertoires: {'✅ OK' if report['directories_ok'] else '❌ Problème'}")
    print(f"📄 Fichiers: {'✅ OK' if report['files_ok'] else '❌ Problème'}")
    print(f"🧠 Moteur RAG: {'✅ OK' if report['rag_ok'] else '❌ Problème'}")
    print(f"💬 Chatbot: {'✅ OK' if report['chatbot_ok'] else '❌ Problème'}")
    print(f"🌐 Flask: {'✅ OK' if report['flask_ok'] else '❌ Problème'}")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS:")
    
    if report['global_score'] >= 90:
        print("🎉 EXCELLENT ! Votre système est parfaitement configuré.")
        print("   ➡️ Vous pouvez lancer: python app.py")
        
    elif report['global_score'] >= 70:
        print("✅ BON ! Quelques améliorations mineures possibles.")
        print("   ➡️ L'application devrait fonctionner: python app.py")
        
        if not report['rag_ok']:
            print("   🔧 Pour activer le RAG: pip install sentence-transformers")
            
    else:
        print("⚠️ CORRECTIONS NÉCESSAIRES !")
        
        if not report['python_compatible']:
            print("   🐍 Mettez à jour Python vers la version 3.8+")
            
        if report['imports_ok'] < 4:
            print("   📦 Installez les dépendances: pip install -r requirements.txt")
            
        if report['core_modules_ok'] < 4:
            print("   🏗️ Vérifiez la structure du projet et les fichiers manquants")
            
        if not report['files_ok']:
            print("   📄 Vérifiez que tous les fichiers du projet sont présents")
    
    print(f"\n🔍 Diagnostic terminé le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}")
    print("📧 En cas de problème persistant, vérifiez la documentation du projet.")
    
    return report['global_score'] >= 70

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)