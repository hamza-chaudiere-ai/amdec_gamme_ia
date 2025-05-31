#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation du système d'authentification TAQA
pour AMDEC & Gamme IA
"""

import os
import json
import sys
import subprocess
from pathlib import Path

def create_directory_structure():
    """Crée la structure de répertoires nécessaire"""
    directories = [
        "auth",
        "templates/auth", 
        "static/css",
        "static/js",
        "data",
        "logs"
    ]
    
    print("📁 Création de la structure de répertoires...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print("✅ Structure de répertoires créée")

def create_init_files():
    """Crée les fichiers __init__.py nécessaires"""
    init_files = [
        "auth/__init__.py"
    ]
    
    print("📄 Création des fichiers __init__.py...")
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('# -*- coding: utf-8 -*-\n')
            print(f"  ✅ {init_file}")
    
    print("✅ Fichiers __init__.py créés")

def create_config_files():
    """Crée les fichiers de configuration"""
    
    # Configuration d'authentification
    auth_config = {
        "allowed_domains": ["taqa.ma"],
        "session_duration_hours": 8,
        "max_login_attempts": 3,
        "verification_code_length": 6,
        "verification_timeout_minutes": 15,
        "max_sessions_per_user": 3,
        "app_name": "AMDEC & Gamme IA",
        "company_name": "TAQA Morocco",
        "smtp_server": "",
        "smtp_port": 587,
        "smtp_username": "",
        "smtp_password": "",
        "development_mode": {
            "enabled": True,
            "bypass_email_verification": False,
            "test_verification_code": "123456"
        }
    }
    
    print("⚙️ Création des fichiers de configuration...")
    
    # Sauvegarder auth_config.json
    with open('auth_config.json', 'w', encoding='utf-8') as f:
        json.dump(auth_config, f, indent=2, ensure_ascii=False)
    print("  ✅ auth_config.json")
    
    # Créer un fichier .env d'exemple
    env_content = """# Configuration AMDEC & Gamme IA avec Authentification TAQA
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=amdec-gamme-ia-taqa-secure-2024

# Configuration SMTP (optionnel pour développement)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# Configuration RAG/Chatbot
GROQ_API_KEY=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

# Sécurité
ALLOWED_DOMAINS=taqa.ma
SESSION_DURATION_HOURS=8
MAX_LOGIN_ATTEMPTS=3
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("  ✅ .env.example")
    
    print("✅ Fichiers de configuration créés")

def install_dependencies():
    """Installe les dépendances Python"""
    print("📦 Installation des dépendances...")
    
    try:
        # Vérifier si on est dans un environnement virtuel
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("  ✅ Environnement virtuel détecté")
        else:
            print("  ⚠️ Aucun environnement virtuel détecté")
            response = input("    Continuer sans environnement virtuel ? (y/N): ")
            if response.lower() != 'y':
                print("  ❌ Installation annulée")
                return False
        
        # Installer les dépendances de base
        basic_deps = [
            "Flask==2.3.3",
            "email-validator==2.1.0",
            "cryptography==41.0.7",
            "python-dotenv==1.0.0"
        ]
        
        for dep in basic_deps:
            print(f"  📦 Installation de {dep}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print(f"    ✅ {dep} installé")
            else:
                print(f"    ❌ Erreur installation {dep}: {result.stderr}")
        
        print("✅ Dépendances de base installées")
        print("💡 Pour installer toutes les dépendances: pip install -r requirements.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def create_sample_users():
    """Crée un fichier d'exemples d'utilisateurs autorisés"""
    sample_users = {
        "authorized_users_examples": [
            "admin@taqa.ma",
            "maintenance.chef@taqa.ma", 
            "technicien.senior@taqa.ma",
            "ingenieur.maintenance@taqa.ma"
        ],
        "blocked_domains": [
            "gmail.com",
            "yahoo.com", 
            "hotmail.com",
            "outlook.com"
        ],
        "note": "Ce fichier est fourni à titre d'exemple. L'authentification se base sur le domaine @taqa.ma uniquement."
    }
    
    with open('data/sample_users.json', 'w', encoding='utf-8') as f:
        json.dump(sample_users, f, indent=2, ensure_ascii=False)
    
    print("  ✅ data/sample_users.json (exemples)")

def test_installation():
    """Teste l'installation de base"""
    print("🧪 Test de l'installation...")
    
    try:
        # Test import des modules Flask
        import flask
        print("  ✅ Flask importé")
        
        # Test import email-validator
        import email_validator
        print("  ✅ email-validator importé")
        
        # Test création des répertoires
        required_dirs = ["auth", "templates/auth", "data"]
        for directory in required_dirs:
            if os.path.exists(directory):
                print(f"  ✅ {directory} existe")
            else:
                print(f"  ❌ {directory} manquant")
                return False
        
        # Test fichiers de configuration
        if os.path.exists('auth_config.json'):
            print("  ✅ auth_config.json existe")
        else:
            print("  ❌ auth_config.json manquant")
            return False
        
        print("✅ Tests de base réussis")
        return True
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erreur de test: {e}")
        return False

def main():
    """Fonction principale d'installation"""
    print("🚀" + "="*60)
    print("🚀 INSTALLATION SYSTÈME D'AUTHENTIFICATION TAQA MOROCCO")
    print("🚀 AMDEC & Gamme IA - Sécurisation de l'application")
    print("🚀" + "="*60)
    
    try:
        # Étape 1: Structure de répertoires
        create_directory_structure()
        
        # Étape 2: Fichiers __init__.py
        create_init_files()
        
        # Étape 3: Fichiers de configuration
        create_config_files()
        
        # Étape 4: Utilisateurs d'exemple
        create_sample_users()
        
        # Étape 5: Installation des dépendances
        if input("\n📦 Installer les dépendances Python de base ? (Y/n): ").lower() != 'n':
            install_dependencies()
        
        # Étape 6: Test de l'installation
        if test_installation():
            print("\n🎉" + "="*60)
            print("🎉 INSTALLATION TERMINÉE AVEC SUCCÈS !")
            print("🎉" + "="*60)
            
            print("\n📋 PROCHAINES ÉTAPES :")
            print("1. 📝 Copiez les codes des modules d'authentification dans auth/")
            print("2. 📝 Copiez les templates dans templates/auth/")
            print("3. 📝 Copiez les styles CSS dans static/css/")
            print("4. 📝 Copiez le JavaScript dans static/js/")
            print("5. ⚙️ Configurez SMTP dans auth_config.json (optionnel)")
            print("6. 🚀 Lancez l'application: python app.py")
            
            print("\n💡 CONFIGURATION SMTP (Optionnelle) :")
            print("   • smtp_server: smtp.office365.com")
            print("   • smtp_port: 587") 
            print("   • smtp_username: votre-email@taqa.ma")
            print("   • smtp_password: votre-mot-de-passe")
            
            print("\n🔐 SÉCURITÉ :")
            print("   • Seuls les emails @taqa.ma sont autorisés")
            print("   • Sessions de 8 heures par défaut")
            print("   • 3 tentatives de connexion maximum")
            print("   • Codes de vérification à 6 chiffres")
            
        else:
            print("\n❌ INSTALLATION ÉCHOUÉE")
            print("Vérifiez les erreurs ci-dessus et réessayez")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Installation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()