#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Flask pour AMDEC & Gamme IA - AVEC AUTHENTIFICATION TAQA INTÉGRÉE
✅ NOUVEAU: Système d'authentification sécurisé par email professionnel @taqa.ma
✅ Protection de toutes les routes critiques
✅ Gestion des sessions utilisateur
✅ Interface de connexion intégrée
✅ Conservation de toutes les fonctionnalités existantes
"""

import os
import sys
import stat
import json
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session
import logging
from typing import List

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ NOUVEAU: Import du système d'authentification
try:
    from auth import AuthManager, EmailValidator, SessionManager
    AUTH_AVAILABLE = True
    logger.info("✅ Modules d'authentification importés avec succès")
except ImportError as e:
    AUTH_AVAILABLE = False
    logger.warning(f"⚠️ Modules d'authentification non disponibles: {e}")

# Imports des modules métier existants
try:
    from core.excel_parser import ExcelParser
    from core.amdec_generator import AMDECGenerator
    from core.gamme_generator import GammeGenerator
    from core.data_trainer import DataTrainer
    from core.utils import (
        create_directories, 
        get_file_info, 
        format_component_display, 
        format_subcomponent_display,
        ComponentConfig
    )
    logger.info("✅ Modules core importés avec succès")
except ImportError as e:
    logger.error(f"❌ Erreur d'import des modules core: {e}")
    sys.exit(1)

# Import RAG avec gestion d'erreurs robuste
try:
    from rag import RAGEngine
    RAG_AVAILABLE = True
    logger.info("✅ Module RAG importé avec succès")
except ImportError as e:
    RAG_AVAILABLE = False
    logger.warning(f"⚠️ Module RAG non disponible: {e}")

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'amdec-gamme-ia-taqa-secure-2024'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# ✅ Variables globales pour l'authentification et RAG
auth_manager = None
rag_engine = None

# ===============================
# 🔐 SYSTÈME D'AUTHENTIFICATION
# ===============================

def init_auth_system():
    """Initialise le système d'authentification"""
    global auth_manager
    
    if not AUTH_AVAILABLE:
        logger.warning("⚠️ Système d'authentification désactivé - Mode développement")
        return False
    
    try:
        logger.info("🔐 Initialisation du système d'authentification TAQA...")
        auth_manager = AuthManager()
        logger.info("✅ Système d'authentification initialisé")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur initialisation authentification: {e}")
        return False

def require_auth(f):
    """
    Décorateur pour protéger les routes nécessitant une authentification
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AUTH_AVAILABLE or not auth_manager:
            # Mode développement sans auth
            logger.info("⚠️ Mode développement - Authentification désactivée")
            return f(*args, **kwargs)
        
        # Récupérer le token depuis les headers ou session
        auth_token = request.headers.get('Authorization')
        if auth_token and auth_token.startswith('Bearer '):
            auth_token = auth_token[7:]  # Supprimer "Bearer "
        else:
            auth_token = session.get('auth_token')
        
        if not auth_token:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Authentification requise',
                    'redirect_url': '/auth/login'
                }), 401
            else:
                return redirect(url_for('auth_login'))
        
        # Vérifier la validité du token
        is_authenticated, user_email = auth_manager.is_user_authenticated(auth_token)
        
        if not is_authenticated:
            session.pop('auth_token', None)
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Session expirée',
                    'redirect_url': '/auth/login'
                }), 401
            else:
                return redirect(url_for('auth_login', error='Session expirée'))
        
        # Ajouter les infos utilisateur au contexte de la requête
        request.user_email = user_email
        request.user_info = auth_manager.get_user_info(auth_token)
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Récupère les informations de l'utilisateur actuel"""
    if not AUTH_AVAILABLE or not auth_manager:
        return None
    
    auth_token = session.get('auth_token')
    if not auth_token:
        return None
    
    return auth_manager.get_user_info(auth_token)

# ===============================
# 🔐 ROUTES D'AUTHENTIFICATION
# ===============================

@app.route('/auth/login')
def auth_login():
    """Page de connexion"""
    # Si déjà connecté, rediriger vers l'accueil
    if AUTH_AVAILABLE and auth_manager and session.get('auth_token'):
        is_authenticated, _ = auth_manager.is_user_authenticated(session['auth_token'])
        if is_authenticated:
            return redirect(url_for('index'))
    
    return render_template('auth/login.html')

@app.route('/api/auth/send_code', methods=['POST'])
def api_send_verification_code():
    """API pour envoyer un code de vérification"""
    if not AUTH_AVAILABLE or not auth_manager:
        return jsonify({
            'success': False,
            'message': 'Système d\'authentification non disponible'
        }), 503
    
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email requis'
            }), 400
        
        # Envoyer le code de vérification
        success, message = auth_manager.send_verification_code(email)
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Erreur envoi code de vérification: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de l\'envoi du code'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    """API pour se connecter avec email et code de vérification"""
    if not AUTH_AVAILABLE or not auth_manager:
        return jsonify({
            'success': False,
            'message': 'Système d\'authentification non disponible'
        }), 503
    
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        verification_code = data.get('verification_code', '').strip()
        
        if not email or not verification_code:
            return jsonify({
                'success': False,
                'message': 'Email et code de vérification requis'
            }), 400
        
        # Tenter la connexion
        success, message, session_token = auth_manager.login_user(email, verification_code)
        
        if success and session_token:
            # Stocker le token dans la session Flask
            session['auth_token'] = session_token
            session['user_email'] = email
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': message,
                'session_token': session_token,
                'redirect_url': url_for('index'),
                'user_info': auth_manager.get_user_info(session_token)
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        logger.error(f"Erreur connexion: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la connexion'
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    """API pour se déconnecter"""
    if not AUTH_AVAILABLE or not auth_manager:
        return jsonify({'success': True})
    
    try:
        auth_token = request.headers.get('Authorization')
        if auth_token and auth_token.startswith('Bearer '):
            auth_token = auth_token[7:]
        else:
            auth_token = session.get('auth_token')
        
        if auth_token:
            auth_manager.logout_user(auth_token)
        
        # Nettoyer la session Flask
        session.pop('auth_token', None)
        session.pop('user_email', None)
        
        return jsonify({
            'success': True,
            'message': 'Déconnexion réussie'
        })
        
    except Exception as e:
        logger.error(f"Erreur déconnexion: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la déconnexion'
        }), 500

@app.route('/api/auth/status')
def api_auth_status():
    """API pour vérifier le statut d'authentification"""
    if not AUTH_AVAILABLE or not auth_manager:
        return jsonify({'authenticated': False})
    
    try:
        auth_token = request.headers.get('Authorization')
        if auth_token and auth_token.startswith('Bearer '):
            auth_token = auth_token[7:]
        else:
            auth_token = session.get('auth_token')
        
        if not auth_token:
            return jsonify({'authenticated': False})
        
        is_authenticated, user_email = auth_manager.is_user_authenticated(auth_token)
        
        if is_authenticated:
            user_info = auth_manager.get_user_info(auth_token)
            return jsonify({
                'authenticated': True,
                'user_email': user_email,
                'user_info': user_info
            })
        else:
            session.pop('auth_token', None)
            return jsonify({'authenticated': False})
            
    except Exception as e:
        logger.error(f"Erreur vérification statut auth: {e}")
        return jsonify({'authenticated': False})

@app.route('/auth/logout')
def auth_logout():
    """Route de déconnexion"""
    if AUTH_AVAILABLE and auth_manager:
        auth_token = session.get('auth_token')
        if auth_token:
            auth_manager.logout_user(auth_token)
    
    session.clear()
    return redirect(url_for('auth_login', logout='success'))

# ===============================
# 🏠 ROUTES PRINCIPALES (PROTÉGÉES)
# ===============================

@app.route('/')
@require_auth
def index():
    """Page d'accueil protégée"""
    try:
        # Statistiques de base
        stats = {
            'amdec_generated': len(os.listdir('data/generated/amdec')) if os.path.exists('data/generated/amdec') else 0,
            'gammes_generated': len(os.listdir('data/generated/gammes')) if os.path.exists('data/generated/gammes') else 0,
            'datasets_available': 2,
            'components_supported': 6,
            'rag_available': RAG_AVAILABLE and rag_engine is not None
        }
        
        # Ajouter les informations utilisateur si authentifié
        user_info = get_current_user()
        
        return render_template('index.html', stats=stats, user_info=user_info)
    except Exception as e:
        logger.error(f"Erreur page d'accueil: {e}")
        flash(f'Erreur lors du chargement: {str(e)}', 'error')
        return render_template('index.html', stats={'rag_available': False}, user_info=None)

@app.route('/amdec')
@require_auth
def amdec_page():
    """Page de génération AMDEC protégée"""
    user_info = get_current_user()
    return render_template('amdec.html', user_info=user_info)

@app.route('/gamme')
@require_auth
def gamme_page():
    """Page de génération des gammes protégée"""
    components = get_available_components()
    user_info = get_current_user()
    return render_template('gamme.html', components=components, user_info=user_info)

@app.route('/chatbot')
@require_auth
def chatbot_page():
    """Page du chatbot intelligent protégée"""
    user_info = get_current_user()
    return render_template('chatbot.html', 
                         rag_available=RAG_AVAILABLE and rag_engine is not None,
                         user_info=user_info)

# ===============================
# 🔧 ROUTES API MÉTIER (PROTÉGÉES)
# ===============================

@app.route('/api/upload_historique', methods=['POST'])
@require_auth
def upload_historique():
    """Upload et traitement avec regroupement automatique (PROTÉGÉ)"""
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nom de fichier vide'
            }), 400
        
        # Valider le fichier
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Format de fichier non supporté. Utilisez .xlsx ou .xls'
            }), 400
        
        # Log de l'action utilisateur
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.info(f"📊 Upload historique par {user_email}: {file.filename}")
        
        # Sauvegarder le fichier uploadé
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"historique_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        file.save(filepath)
        logger.info(f"📁 Fichier historique sauvegardé: {filepath}")
        
        # Parser le fichier Excel
        parser = ExcelParser(filepath)
        processed_data = parser.parse()
        
        if processed_data.empty:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée valide trouvée dans le fichier'
            }), 400
        
        logger.info(f"📊 Données parsed: {len(processed_data)} lignes avant regroupement")
        
        # Générer l'AMDEC avec regroupement automatique
        amdec_generator = AMDECGenerator(processed_data)
        amdec_df = amdec_generator.generate()
        
        if amdec_df.empty:
            return jsonify({
                'success': False,
                'error': 'Impossible de générer l\'AMDEC à partir de cet historique'
            }), 400
        
        logger.info(f"✅ AMDEC générée par {user_email}: {len(amdec_df)} lignes après regroupement intelligent")
        
        # Sauvegarder l'AMDEC généré
        amdec_file_path = amdec_generator.save_to_file()
        
        # Statistiques
        stats = amdec_generator.get_statistics()
        parser_stats = parser.get_statistics()
        
        # Génération automatique des gammes avec images
        try:
            logger.info("🔄 Génération automatique des gammes avec images...")
            gammes_generated = amdec_generator.generate_gammes_from_amdec(amdec_file_path)
            auto_gammes_success = True
            gammes_count = len(gammes_generated)
            gammes_files = [os.path.basename(g) for g in gammes_generated]
            
            logger.info(f"✅ {gammes_count} gammes générées automatiquement par {user_email}")
            
        except Exception as gamme_error:
            logger.warning(f"⚠️ Erreur génération gammes pour {user_email}: {gamme_error}")
            gammes_generated = []
            auto_gammes_success = False
            gammes_count = 0
            gammes_files = []
        
        # Nettoyer le fichier temporaire
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(amdec_file_path),
            'rows_processed': int(parser_stats.get('total_rows', 0)),
            'amdec_entries': int(len(amdec_df)),
            'avg_criticality': round(float(stats.get('avg_criticality', 0)), 1),
            'max_criticality': int(stats.get('max_criticality', 0)),
            'auto_gammes_generated': auto_gammes_success,
            'gammes_count': int(gammes_count),
            'gammes_files': gammes_files,
            'grouped_entries': True,
            'images_in_gammes': auto_gammes_success,
            'user_email': user_email,
            'statistics': {
                'unique_components': int(stats.get('unique_components', 0)),
                'unique_subcomponents': int(stats.get('unique_subcomponents', 0)),
                'criticality_distribution': stats.get('criticality_distribution', {})
            }
        })

    except Exception as e:
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.error(f"❌ Erreur upload historique par {user_email}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate_amdec_from_dataset', methods=['POST'])
@require_auth
def generate_amdec_from_dataset():
    """Génère AMDEC depuis dataset (PROTÉGÉ)"""
    try:
        data = request.get_json()
        component = data.get('component')
        subcomponent = data.get('subcomponent')
        
        if not component:
            return jsonify({
                'success': False,
                'error': 'Composant requis'
            }), 400
        
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.info(f"🔄 Génération AMDEC dataset par {user_email}: {component} - {subcomponent}")
        
        # Utiliser le trainer pour générer depuis le dataset
        trainer = DataTrainer()
        amdec_data = trainer.generate_amdec_from_dataset(component, subcomponent)
        
        if not amdec_data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée trouvée pour ce composant dans le dataset'
            }), 404
        
        # Créer l'AMDEC Generator et sauvegarder
        amdec_generator = AMDECGenerator()
        amdec_file_path = amdec_generator.save_dataset_amdec(amdec_data, component, subcomponent)
        
        # Calculer les statistiques
        stats = {
            'total_entries': len(amdec_data),
            'avg_criticality': sum(entry['C'] for entry in amdec_data) / len(amdec_data),
            'max_criticality': max(entry['C'] for entry in amdec_data),
            'unique_components': len(set(entry['Composant'] for entry in amdec_data)),
            'unique_subcomponents': len(set(entry['Sous-composant'] for entry in amdec_data))
        }
        
        # Génération automatique des gammes avec images
        try:
            logger.info("🔄 Génération automatique des gammes avec images d'appareils...")
            gammes_generated = amdec_generator.generate_gammes_from_amdec(amdec_file_path)
            
            response_data = {
                'success': True,
                'amdec_file': os.path.basename(amdec_file_path),
                'gammes_files': [os.path.basename(g) for g in gammes_generated],
                'entries_count': len(amdec_data),
                'avg_criticality': round(stats['avg_criticality'], 1),
                'max_criticality': stats['max_criticality'],
                'component': format_component_display(component),
                'subcomponent': format_subcomponent_display(subcomponent) if subcomponent else 'Tous',
                'auto_gammes_generated': True,
                'gammes_count': len(gammes_generated),
                'images_included': True,
                'user_email': user_email
            }
            
            logger.info(f"✅ AMDEC + {len(gammes_generated)} gammes avec images générées par {user_email}")
            
        except Exception as gamme_error:
            logger.warning(f"⚠️ Erreur génération gammes automatiques par {user_email}: {gamme_error}")
            
            response_data = {
                'success': True,
                'amdec_file': os.path.basename(amdec_file_path),
                'entries_count': len(amdec_data),
                'avg_criticality': round(stats['avg_criticality'], 1),
                'max_criticality': stats['max_criticality'],
                'component': format_component_display(component),
                'subcomponent': format_subcomponent_display(subcomponent) if subcomponent else 'Tous',
                'auto_gammes_generated': False,
                'gamme_error': str(gamme_error),
                'user_email': user_email
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.error(f"❌ Erreur génération AMDEC dataset par {user_email}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate_gamme', methods=['POST'])
@require_auth
def generate_gamme():
    """Génère gamme avec images d'appareils (PROTÉGÉ)"""
    try:
        data = request.get_json()
        component = data.get('component')
        subcomponent = data.get('subcomponent') 
        criticality = data.get('criticality')
        
        if not all([component, subcomponent]):
            return jsonify({
                'success': False,
                'error': 'Composant et sous-composant requis'
            }), 400
        
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        
        # Utiliser la criticité fournie ou calculer automatiquement
        if criticality is None:
            criticality = ComponentConfig.get_default_criticality(component, subcomponent)
        
        logger.info(f"🔄 Génération gamme avec images par {user_email}: {component} - {subcomponent} (C={criticality})")
        
        # Générer la gamme avec images d'appareils intégrées
        gamme_generator = GammeGenerator()
        gamme_data = gamme_generator.generate(component, subcomponent, criticality)
        
        # Enrichir avec des informations AMDEC si disponibles
        gamme_data['enhanced_with_amdec'] = False
        try:
            trainer = DataTrainer()
            amdec_data = trainer.generate_amdec_from_dataset(component, subcomponent)
            
            if amdec_data:
                amdec_entry = amdec_data[0]
                gamme_data['amdec_mode'] = amdec_entry.get('Mode de Défaillance', '')
                gamme_data['amdec_cause'] = amdec_entry.get('Cause', '')
                gamme_data['amdec_actions'] = amdec_entry.get('Actions Correctives', '')
                gamme_data['enhanced_with_amdec'] = True
                
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'enrichir avec AMDEC: {e}")
        
        # Sauvegarder la gamme avec images d'appareils intégrées
        output_path = gamme_generator.save_to_file(gamme_data, component, subcomponent)
        
        # Préparer les aperçus d'opérations
        operations_preview = []
        for op in gamme_data.get('operations', [])[:3]:
            operations_preview.append(f"{op.get('name', 'Opération')} ({op.get('time', 0)} min)")
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(output_path),
            'component_display': gamme_data['component'],
            'subcomponent_display': gamme_data['subcomponent'],
            'criticality': criticality,
            'criticality_level': gamme_data['criticality_level'],
            'estimated_time': gamme_data['estimated_time'],
            'frequency': gamme_data['maintenance_frequency'],
            'operations_count': len(gamme_data.get('operations', [])),
            'operations_preview': operations_preview,
            'materials_count': len(gamme_data.get('materials', [])),
            'enhanced_with_amdec': gamme_data.get('enhanced_with_amdec', False),
            'safety_instructions': len(gamme_data.get('safety_instructions', [])),
            'images_included': len(gamme_data.get('images', [])),
            'images_count': len(gamme_data.get('images', [])),
            'images_integrated_in_word': True,
            'user_email': user_email
        })
        
    except Exception as e:
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.error(f"❌ Erreur génération gamme par {user_email}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/train_models', methods=['POST'])
@require_auth
def train_models():
    """Entraîne les modèles ML (PROTÉGÉ)"""
    try:
        data = request.get_json()
        model_type = data.get('model_type', 'both')
        
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.info(f"🧠 Entraînement modèles par {user_email}: {model_type}")
        
        trainer = DataTrainer()
        results = trainer.train_models(model_type)
        
        return jsonify({
            'success': True,
            'message': 'Modèles entraînés avec succès',
            'results': results,
            'user_email': user_email
        })
        
    except Exception as e:
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.error(f"❌ Erreur entraînement par {user_email}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/components')
@require_auth
def get_components():
    """Retourne la liste des composants disponibles (PROTÉGÉ)"""
    components = get_available_components()
    return jsonify(components)

@app.route('/api/criticality', methods=['POST'])
@require_auth
def calculate_criticality():
    """Calcule la criticité pour un composant/sous-composant (PROTÉGÉ)"""
    try:
        data = request.get_json()
        component = data.get('component')
        subcomponent = data.get('subcomponent')
        
        # Calculer la criticité
        trainer = DataTrainer()
        criticality = trainer.predict_criticality(component, subcomponent)
        
        return jsonify({
            'criticality': criticality,
            'level': get_criticality_level(criticality),
            'description': get_criticality_description(criticality)
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur calcul criticité: {e}")
        return jsonify({'error': str(e)}), 500

# ===============================
# 🤖 ROUTES CHATBOT RAG (PROTÉGÉES)
# ===============================

@app.route('/api/chatbot/query', methods=['POST'])
@require_auth
def chatbot_query():
    """API pour les questions du chatbot (PROTÉGÉ)"""
    try:
        if not RAG_AVAILABLE or not rag_engine:
            return jsonify({
                'success': False,
                'error': 'Chatbot non disponible',
                'response': 'Désolé, le chatbot intelligent n\'est pas encore configuré.'
            }), 503
        
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question vide'
            }), 400
        
        if len(question) > 1000:
            return jsonify({
                'success': False,
                'error': 'Question trop longue (max 1000 caractères)'
            }), 400
        
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.info(f"🤖 Question chatbot par {user_email}: {question[:100]}...")
        
        # Traitement via RAG
        result = rag_engine.query(question, max_context_length=3000)
        
        # Formater la réponse
        response_data = {
            'success': True,
            'response': result.get('response', 'Aucune réponse générée'),
            'sources': result.get('sources', []),
            'detected_components': result.get('detected_components', []),
            'detected_defects': result.get('detected_defects', []),
            'confidence': result.get('confidence', 0.0),
            'timestamp': result.get('timestamp'),
            'context_length': len(result.get('context', '')),
            'has_context': bool(result.get('context', '').strip()),
            'user_email': user_email
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.error(f"❌ Erreur chatbot query par {user_email}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': 'Désolé, une erreur technique s\'est produite.'
        }), 500

@app.route('/api/chatbot/status')
@require_auth
def chatbot_status():
    """Statut du système chatbot (PROTÉGÉ)"""
    try:
        if not RAG_AVAILABLE:
            return jsonify({
                'available': False,
                'error': 'Module RAG non disponible',
                'rag_installed': False
            })
        
        if not rag_engine:
            return jsonify({
                'available': False,
                'error': 'Moteur RAG non initialisé',
                'rag_installed': True,
                'initialized': False
            })
        
        # Obtenir le statut détaillé
        status = rag_engine.get_system_status()
        
        return jsonify({
            'available': True,
            'rag_installed': True,
            'initialized': status.get('initialized', False),
            'status': status
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur statut chatbot: {e}")
        return jsonify({
            'available': False,
            'error': str(e)
        }), 500

@app.route('/api/chatbot/suggestions')
@require_auth
def chatbot_suggestions():
    """Retourne des suggestions de questions (PROTÉGÉ)"""
    try:
        suggestions = [
            "J'ai un percement sur l'économiseur BT, que faire ?",
            "Qu'est-ce que la corrosion caustic attack ?",
            "Comment contrôler les surchauffeurs haute température ?",
            "Quelle est la criticité d'une fissure sur un collecteur ?",
            "Comment prévenir l'érosion des tubes porteurs ?",
            "Que signifie F×G×D dans l'analyse AMDEC ?",
            "Quels sont les défauts courants des réchauffeurs HT ?",
            "Comment faire la maintenance préventive d'un économiseur ?"
        ]
        
        import random
        selected = random.sample(suggestions, min(4, len(suggestions)))
        
        return jsonify({
            'success': True,
            'suggestions': selected
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur suggestions: {e}")
        return jsonify({
            'success': False,
            'suggestions': []
        })

# ===============================
# 📁 ROUTES UTILITAIRES (PROTÉGÉES)
# ===============================

@app.route('/api/list_generated_files', methods=['GET'])
@require_auth
def list_generated_files():
    """Liste tous les fichiers AMDEC et Gammes générés (PROTÉGÉ)"""
    try:
        amdec_dir = 'data/generated/amdec'
        gammes_dir = 'data/generated/gammes'
        
        amdec_files = []
        gammes_files = []
        
        # Lister les fichiers AMDEC
        if os.path.exists(amdec_dir):
            for filename in os.listdir(amdec_dir):
                if filename.endswith('.xlsx'):
                    filepath = os.path.join(amdec_dir, filename)
                    stat = os.stat(filepath)
                    amdec_files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        
        # Lister les fichiers Gammes  
        if os.path.exists(gammes_dir):
            for filename in os.listdir(gammes_dir):
                if filename.endswith('.docx'):
                    filepath = os.path.join(gammes_dir, filename)
                    stat = os.stat(filepath)
                    gammes_files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'has_images': True
                    })
        
        # Trier par date de modification (plus récents en premier)
        amdec_files.sort(key=lambda x: x['modified'], reverse=True)
        gammes_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'amdec_files': amdec_files,
            'gammes_files': gammes_files,
            'total_amdec': len(amdec_files),
            'total_gammes': len(gammes_files),
            'images_integrated': True
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur listage fichiers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<path:filename>')
@require_auth
def download_file(filename):
    """Télécharge un fichier généré (PROTÉGÉ)"""
    try:
        user_info = get_current_user()
        user_email = user_info.get('email', 'unknown') if user_info else 'unknown'
        logger.info(f"📥 Téléchargement par {user_email}: {filename}")
        
        # Vérifier si le fichier existe
        full_path = None
        for root, dirs, files in os.walk('data/generated'):
            if filename in files:
                full_path = os.path.join(root, filename)
                break
        
        if not full_path or not os.path.exists(full_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        return send_file(full_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"❌ Erreur téléchargement: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Point de santé de l'application (PUBLIC)"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules': {
            'excel_parser': True,
            'amdec_generator': True,
            'gamme_generator': True,
            'data_trainer': True,
            'rag_engine': RAG_AVAILABLE and rag_engine is not None,
            'auth_system': AUTH_AVAILABLE and auth_manager is not None
        },
        'security': {
            'authentication_enabled': AUTH_AVAILABLE,
            'active_sessions': auth_manager.get_active_sessions_count() if auth_manager else 0,
            'protected_routes': True
        }
    }
    
    # Ajouter les informations RAG
    if RAG_AVAILABLE and rag_engine:
        try:
            rag_status = rag_engine.get_system_status()
            health_data['rag'] = {
                'available': True,
                'initialized': rag_status.get('initialized', False),
                'vector_documents': rag_status.get('vector_store', {}).get('total_documents', 0),
                'llm_healthy': rag_status.get('llm_client', {}).get('healthy', False)
            }
        except Exception as e:
            health_data['rag'] = {'available': True, 'error': str(e)}
    else:
        health_data['rag'] = {'available': False}
    
    return jsonify(health_data)

# ===============================
# 🔧 FONCTIONS UTILITAIRES
# ===============================

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_vector_db_and_permissions():
    """Initialise la base vectorielle et les permissions"""
    try:
        logger.info("🔄 Initialisation base vectorielle...")
        
        directories = [
            "data", "data/vector_db", "data/documents", "data/generated",
            "data/generated/amdec", "data/generated/gammes", "data/dataset",
            "data/templates", "uploads", "logs"
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                if os.name == 'nt':
                    os.chmod(directory, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                else:
                    os.chmod(directory, 0o777)
            except Exception as e:
                logger.warning(f"  ⚠️ Erreur {directory}: {e}")
        
        logger.info("✅ Initialisation base vectorielle terminée")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation base vectorielle: {e}")
        return False

def init_rag_engine():
    """Initialise le moteur RAG"""
    global rag_engine
    
    if not RAG_AVAILABLE:
        logger.warning("⚠️ Module RAG non disponible")
        return False
    
    try:
        logger.info("🧠 Initialisation du moteur RAG...")
        rag_engine = RAGEngine(
            documents_dir="data/documents",
            vector_db_path="data/vector_db", 
            llm_config_path="llm_config.json"
        )
        
        success = rag_engine.initialize(force_reindex=True)
        
        if success:
            logger.info("✅ Moteur RAG initialisé")
        else:
            logger.error("❌ Échec initialisation moteur RAG")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation RAG: {e}")
        rag_engine = None
        return False

def init_app():
    """Initialise l'application avec authentification"""
    try:
        # Créer les répertoires de base
        create_directories()
        logger.info("✅ Répertoires de base créés")
        
        # Initialiser la base vectorielle et permissions
        init_vector_db_and_permissions()
        
        # Initialiser le système d'authentification
        auth_initialized = init_auth_system()
        
        # Initialiser le moteur RAG si disponible
        if RAG_AVAILABLE:
            init_rag_engine()
        
        logger.info("✅ Application initialisée avec succès")
        
        if auth_initialized:
            logger.info("🔐 Système d'authentification TAQA actif")
        else:
            logger.warning("⚠️ Mode développement sans authentification")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation application: {e}")

def get_available_components():
    """Retourne la liste des composants supportés"""
    return ComponentConfig.get_component_list()

def get_criticality_level(criticality):
    """Retourne le niveau de criticité"""
    if criticality <= 12:
        return 'Négligeable'
    elif criticality <= 16:
        return 'Moyenne'
    elif criticality <= 20:
        return 'Élevée'
    else:
        return 'Critique'

def get_criticality_description(criticality):
    """Retourne la description de la criticité"""
    if criticality <= 12:
        return 'Maintenance corrective suffisante'
    elif criticality <= 16:
        return 'Maintenance préventive systématique recommandée'
    elif criticality <= 20:
        return 'Maintenance préventive conditionnelle nécessaire'
    else:
        return 'Remise en cause complète de la conception requise'

# ===============================
# 🔧 GESTIONNAIRES D'ERREURS
# ===============================

@app.errorhandler(401)
def unauthorized(e):
    """Gestionnaire d'erreur pour accès non autorisé"""
    if request.is_json:
        return jsonify({
            'error': 'Accès non autorisé - Connexion TAQA requise',
            'redirect_url': '/auth/login'
        }), 401
    else:
        return redirect(url_for('auth_login', error='Accès non autorisé'))

@app.errorhandler(413)
def too_large(e):
    """Gestionnaire d'erreur pour fichiers trop volumineux"""
    return jsonify({'error': 'Fichier trop volumineux (max 50MB)'}), 413

@app.errorhandler(500)
def internal_error(e):
    """Gestionnaire d'erreur interne"""
    logger.error(f"❌ Erreur interne: {e}")
    return jsonify({'error': 'Erreur interne du serveur'}), 500

@app.errorhandler(404)
def not_found(e):
    """Gestionnaire d'erreur 404"""
    return jsonify({'error': 'Page non trouvée'}), 404

# ===============================
# 🚀 LANCEMENT DE L'APPLICATION
# ===============================

if __name__ == '__main__':
    try:
        # Initialiser l'application
        init_app()
        
        # Message de confirmation
        logger.info("🚀" + "="*60)
        logger.info("🚀 AMDEC & GAMME IA - VERSION SÉCURISÉE TAQA MOROCCO")
        logger.info("🚀" + "="*60)
        logger.info("✅ FIX 1: Regroupement automatique des fréquences AMDEC")
        logger.info("✅ FIX 2: Images d'appareils intégrées dans les gammes")
        logger.info("✅ FIX 3: Génération automatique gammes depuis AMDEC")
        logger.info("✅ FIX 4: Correction erreur huggingface_hub")
        logger.info("✅ FIX 5: Réinitialisation base vectorielle")
        logger.info("🤖 RAG: Chatbot intelligent avec base de connaissances")
        logger.info("🔐 NOUVEAU: Authentification sécurisée @taqa.ma")
        
        # Statut authentification
        if AUTH_AVAILABLE and auth_manager:
            logger.info("🔐 Authentification: ✅ ACTIVE (@taqa.ma uniquement)")
            stats = auth_manager.get_system_stats()
            logger.info(f"👥 Sessions actives: {stats.get('active_sessions', 0)}")
        else:
            logger.warning("🔐 Authentification: ⚠️ DÉSACTIVÉE (mode développement)")
        
        # Statut RAG
        if RAG_AVAILABLE and rag_engine:
            try:
                status = rag_engine.get_system_status()
                if status.get('initialized'):
                    docs = status.get('vector_store', {}).get('total_documents', 0)
                    logger.info(f"🧠 RAG: ✅ Opérationnel ({docs} documents)")
                else:
                    logger.warning("🧠 RAG: ⚠️ Erreur d'initialisation")
            except:
                logger.warning("🧠 RAG: ⚠️ Statut indisponible")
        else:
            logger.warning("🧠 RAG: ⚠️ Non disponible")
        
        logger.info("🚀" + "="*60)
        logger.info("🌐 Application SÉCURISÉE disponible sur:")
        if AUTH_AVAILABLE:
            logger.info("   • http://localhost:5000/auth/login    (🔐 Connexion TAQA)")
            logger.info("   • http://localhost:5000               (🏠 Accueil protégé)")
            logger.info("   • http://localhost:5000/amdec         (📊 AMDEC protégé)")
            logger.info("   • http://localhost:5000/gamme         (🛠️ Gammes protégé)")
            logger.info("   • http://localhost:5000/chatbot       (🤖 Chatbot protégé)")
        else:
            logger.info("   • http://localhost:5000               (🏠 Mode développement)")
        logger.info("   • http://localhost:5000/health        (📋 Statut système)")
        logger.info("🔐 Seuls les emails @taqa.ma sont autorisés !")
        logger.info("🚀" + "="*60)
        
        # Lancer le serveur
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Application arrêtée par l'utilisateur")
    except Exception as e:
        logger.error(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("🔚 Arrêt de l'application AMDEC & Gamme IA")