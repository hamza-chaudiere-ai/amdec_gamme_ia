#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de mise à jour pour corriger les problèmes identifiés
dans l'application AMDEC & Gamme IA
"""

import os
import shutil
import sys
from datetime import datetime

def create_backup():
    """Crée une sauvegarde de l'application actuelle"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🔄 Création de la sauvegarde dans {backup_dir}...")
    
    files_to_backup = [
        'app.py',
        'core/amdec_generator.py',
        'static/js/main.js',
        'templates/amdec.html',
        'templates/gamme.html',
        'templates/base.html',
        'static/css/style.css'
    ]
    
    os.makedirs(backup_dir, exist_ok=True)
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            # Créer la structure de répertoires si nécessaire
            backup_file_path = os.path.join(backup_dir, file_path)
            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
            shutil.copy2(file_path, backup_file_path)
            print(f"  ✅ {file_path} sauvegardé")
        else:
            print(f"  ⚠️ {file_path} non trouvé")
    
    print(f"✅ Sauvegarde terminée dans {backup_dir}")
    return backup_dir

def verify_structure():
    """Vérifie que la structure de l'application est correcte"""
    print("🔍 Vérification de la structure...")
    
    required_dirs = [
        'core',
        'ml',
        'static/css',
        'static/js',
        'static/images',
        'templates',
        'data/dataset',
        'data/generated/amdec',
        'data/generated/gammes',
        'uploads'
    ]
    
    required_files = [
        'app.py',
        'core/__init__.py',
        'core/amdec_generator.py',
        'core/gamme_generator.py',
        'core/excel_parser.py',
        'core/utils.py',
        'core/data_trainer.py',
        'ml/__init__.py',
        'ml/models.py',
        'ml/predictor.py',
        'ml/trainer.py',
        'static/css/style.css',
        'static/js/main.js',
        'templates/base.html',
        'templates/index.html',
        'templates/amdec.html',
        'templates/gamme.html'
    ]
    
    missing_dirs = []
    missing_files = []
    
    # Vérifier les répertoires
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_path}")
    
    # Vérifier les fichiers
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_dirs:
        print("📁 Répertoires manquants :")
        for dir_path in missing_dirs:
            print(f"  ❌ {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            print(f"  ✅ {dir_path} créé")
    
    if missing_files:
        print("📄 Fichiers manquants :")
        for file_path in missing_files:
            print(f"  ❌ {file_path}")
    
    return len(missing_files) == 0

def test_imports():
    """Teste que tous les imports fonctionnent"""
    print("🧪 Test des imports...")
    
    try:
        # Test des imports principaux
        import pandas as pd
        print("  ✅ pandas")
        
        import numpy as np
        print("  ✅ numpy")
        
        import flask
        print("  ✅ flask")
        
        try:
            import sklearn
            print("  ✅ scikit-learn")
        except ImportError:
            print("  ⚠️ scikit-learn manquant (optionnel pour ML)")
        
        try:
            import openpyxl
            print("  ✅ openpyxl")
        except ImportError:
            print("  ❌ openpyxl manquant (requis)")
            return False
        
        try:
            import docx
            print("  ✅ python-docx")
        except ImportError:
            print("  ❌ python-docx manquant (requis)")
            return False
        
        # Test des imports locaux
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from core.utils import ComponentConfig, normalize_component_name
            print("  ✅ core.utils")
        except ImportError as e:
            print(f"  ❌ core.utils: {e}")
            return False
        
        try:
            from core.amdec_generator import AMDECGenerator
            print("  ✅ core.amdec_generator")
        except ImportError as e:
            print(f"  ❌ core.amdec_generator: {e}")
            return False
        
        try:
            from core.gamme_generator import GammeGenerator
            print("  ✅ core.gamme_generator")
        except ImportError as e:
            print(f"  ❌ core.gamme_generator: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test des imports: {e}")
        return False

def check_missing_methods():
    """Vérifie que les méthodes requises existent"""
    print("🔧 Vérification des méthodes...")
    
    try:
        from core.amdec_generator import AMDECGenerator
        
        # Vérifier que save_dataset_amdec existe
        if hasattr(AMDECGenerator, 'save_dataset_amdec'):
            print("  ✅ AMDECGenerator.save_dataset_amdec existe")
        else:
            print("  ❌ AMDECGenerator.save_dataset_amdec manquante")
            return False
        
        # Vérifier que generate_gammes_from_amdec existe
        if hasattr(AMDECGenerator, 'generate_gammes_from_amdec'):
            print("  ✅ AMDECGenerator.generate_gammes_from_amdec existe")
        else:
            print("  ❌ AMDECGenerator.generate_gammes_from_amdec manquante")
            return False
        
        # Vérifier que generate_from_dataset existe
        if hasattr(AMDECGenerator, 'generate_from_dataset'):
            print("  ✅ AMDECGenerator.generate_from_dataset existe")
        else:
            print("  ❌ AMDECGenerator.generate_from_dataset manquante")
            return False
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Impossible d'importer AMDECGenerator: {e}")
        return False

def test_api_endpoints():
    """Teste que l'application démarre et que les endpoints existent"""
    print("🌐 Test des endpoints API...")
    
    try:
        # Import de l'application
        from app import app
        
        # Vérifier que les routes existent
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        required_routes = [
            '/api/upload_historique',
            '/api/generate_amdec_from_dataset',
            '/api/generate_gamme',
            '/api/generate_gammes_from_amdec',
            '/api/components',
            '/api/criticality',
            '/download/<path:filename>'
        ]
        
        missing_routes = []
        for route in required_routes:
            # Vérifier si la route existe (en tenant compte des paramètres)
            route_exists = any(route.replace('<path:filename>', '<filename>') in r or 
                             route.replace('<path:', '<').replace('>', '>') in r 
                             for r in routes)
            
            if route_exists:
                print(f"  ✅ {route}")
            else:
                missing_routes.append(route)
                print(f"  ❌ {route}")
        
        if missing_routes:
            print(f"  ⚠️ {len(missing_routes)} routes manquantes")
            return False
        
        print("  ✅ Tous les endpoints requis sont présents")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test de l'application: {e}")
        return False

def create_missing_files():
    """Crée les fichiers manquants avec un contenu minimal"""
    print("📝 Création des fichiers manquants...")
    
    # Créer les fichiers __init__.py s'ils manquent
    init_files = [
        'core/__init__.py',
        'ml/__init__.py'
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('# -*- coding: utf-8 -*-\n')
            print(f"  ✅ {init_file} créé")
    
    # Créer des fichiers .gitkeep pour les dossiers vides
    empty_dirs = [
        'data/generated/amdec',
        'data/generated/gammes',
        'uploads',
        'ml/saved_models'
    ]
    
    for dir_path in empty_dirs:
        gitkeep_path = os.path.join(dir_path, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            os.makedirs(dir_path, exist_ok=True)
            with open(gitkeep_path, 'w') as f:
                f.write('')
            print(f"  ✅ {gitkeep_path} créé")

def show_update_summary():
    """Affiche un résumé des corrections à appliquer"""
    print("\n" + "="*60)
    print("📋 RÉSUMÉ DES CORRECTIONS À APPLIQUER")
    print("="*60)
    
    corrections = [
        {
            "title": "1. 🔧 Correction AMDECGenerator",
            "description": "Ajouter les méthodes manquantes save_dataset_amdec() et generate_gammes_from_amdec()",
            "file": "core/amdec_generator.py",
            "status": "CRITIQUE"
        },
        {
            "title": "2. 🌐 Correction API Flask", 
            "description": "Ajouter les endpoints manquants et corriger le chaînage AMDEC→Gamme",
            "file": "app.py",
            "status": "CRITIQUE"
        },
        {
            "title": "3. 🎨 Amélioration Interface",
            "description": "Enrichir les templates HTML avec onglets et workflow amélioré",
            "file": "templates/*.html",
            "status": "IMPORTANT"
        },
        {
            "title": "4. ⚡ JavaScript Enrichi",
            "description": "Ajouter les fonctions de chaînage automatique et notifications",
            "file": "static/js/main.js", 
            "status": "IMPORTANT"
        },
        {
            "title": "5. 🎨 CSS Amélioré",
            "description": "Styles enrichis pour les nouvelles fonctionnalités",
            "file": "static/css/style.css",
            "status": "OPTIONNEL"
        }
    ]
    
    for correction in corrections:
        status_color = {
            "CRITIQUE": "🔴",
            "IMPORTANT": "🟡", 
            "OPTIONNEL": "🟢"
        }
        
        print(f"\n{status_color[correction['status']]} {correction['title']}")
        print(f"   📄 Fichier: {correction['file']}")
        print(f"   📝 Description: {correction['description']}")
    
    print("\n" + "="*60)
    print("🚀 INSTRUCTIONS DE MISE À JOUR")
    print("="*60)
    
    steps = [
        "1. Sauvegardez vos fichiers actuels (fait automatiquement)",
        "2. Remplacez le contenu de core/amdec_generator.py par la version corrigée",
        "3. Remplacez le contenu de app.py par la version corrigée",
        "4. Remplacez le contenu de static/js/main.js par la version enrichie",
        "5. Remplacez les templates HTML par les versions améliorées",
        "6. Remplacez le CSS par la version enrichie",
        "7. Redémarrez l'application avec: python app.py",
        "8. Testez les fonctionnalités corrigées"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n✅ Après ces corrections, les 3 problèmes identifiés seront résolus:")
    print("   • Fréquences correctement regroupées dans l'AMDEC")
    print("   • Chaînage automatique AMDEC → Gammes")
    print("   • Méthode save_dataset_amdec() fonctionnelle")

def run_complete_check():
    """Exécute tous les tests de vérification"""
    print("🔍 DIAGNOSTIC COMPLET DE L'APPLICATION")
    print("="*50)
    
    # 1. Créer la sauvegarde
    backup_dir = create_backup()
    
    # 2. Vérifier la structure
    structure_ok = verify_structure()
    
    # 3. Créer les fichiers manquants
    create_missing_files()
    
    # 4. Tester les imports
    imports_ok = test_imports()
    
    # 5. Vérifier les méthodes
    methods_ok = check_missing_methods()
    
    # 6. Tester les endpoints
    endpoints_ok = test_api_endpoints()
    
    # 7. Résumé
    print("\n" + "="*50)
    print("📊 RÉSULTATS DU DIAGNOSTIC")
    print("="*50)
    
    results = [
        ("Structure des fichiers", structure_ok),
        ("Imports Python", imports_ok),
        ("Méthodes requises", methods_ok),
        ("Endpoints API", endpoints_ok)
    ]
    
    all_ok = True
    for test_name, result in results:
        status = "✅ OK" if result else "❌ ERREUR"
        print(f"{test_name:<25} : {status}")
        if not result:
            all_ok = False
    
    print(f"\n📋 Sauvegarde créée dans: {backup_dir}")
    
    if all_ok:
        print("\n🎉 DIAGNOSTIC: Votre application semble fonctionnelle !")
        print("   Si vous rencontrez encore des problèmes, vérifiez les logs d'erreur.")
    else:
        print("\n⚠️ DIAGNOSTIC: Des corrections sont nécessaires.")
        show_update_summary()
    
    return all_ok

if __name__ == "__main__":
    print("🔧 SCRIPT DE DIAGNOSTIC ET MISE À JOUR")
    print("AMDEC & Gamme IA - Correcteur automatique")
    print("="*50)
    
    try:
        success = run_complete_check()
        
        if success:
            print("\n✅ Diagnostic terminé avec succès !")
        else:
            print("\n⚠️ Diagnostic terminé avec des erreurs à corriger.")
            
    except KeyboardInterrupt:
        print("\n🛑 Diagnostic interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()