# 🔧 AMDEC & Gamme IA

<div align="center">

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/hamza-chaudiere-ai/amdec_gamme_ia)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.3+-red.svg)](https://flask.palletsprojects.com)
[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)](https://github.com/hamza-chaudiere-ai/amdec_gamme_ia)

**Assistant Intelligent pour la Maintenance Industrielle de TAQA Morocco**  
*Génération automatique d'analyses AMDEC et de gammes de maintenance enrichies avec IA & RAG*

[🚀 Démarrage Rapide](#-installation-et-démarrage) • [📖 Fonctionnalités](#-fonctionnalités) • [🤖 Chatbot RAG](#-chatbot-intelligent-rag) • [🔐 Authentification](#-authentification-et-sécurité) • [🛠️ Structure du Projet](#-structure-du-projet)

---

</div>

## 🎯 Présentation

**AMDEC & Gamme IA** est une solution intelligente développée pour **TAQA Morocco**, permettant d’analyser automatiquement les historiques d’arrêts industriels et de générer :
- 📊 des analyses AMDEC structurées (F × G × D)
- 🛠️ des gammes de maintenance personnalisées avec images
- 🤖 un chatbot technique RAG exploitant une base documentaire vectorisée

## ✨ Fonctionnalités

- ✅ Génération AMDEC automatique à partir de fichiers Excel
- ✅ Calcul de criticité, regroupement intelligent des défaillances
- ✅ Gammes de maintenance avec images d'appareils
- ✅ Chatbot IA (LLM + RAG) capable de répondre à des questions métiers
- ✅ Export professionnel Word et Excel
- ✅ Authentification sécurisée par email @taqa.ma

## 🚀 Installation et Démarrage

```bash
git clone https://github.com/hamza-chaudiere-ai/amdec_gamme_ia.git
cd amdec_gamme_ia
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python generate_datasets.py
python app.py
```

Accès à l'application :
- 🔐 Connexion : http://localhost:5000/auth/login
- 🏠 Accueil : http://localhost:5000
- 📊 AMDEC : http://localhost:5000/amdec
- 🛠️ Gammes : http://localhost:5000/gamme
- 🤖 Chatbot : http://localhost:5000/chatbot

## 🤖 Chatbot Intelligent RAG

Le moteur RAG permet d'interroger automatiquement les documents Excel, PDF, Word liés à la maintenance et à l’AMDEC via un chatbot intégré.

Exemples de questions :
- "J'ai un percement sur l’économiseur BT, que faire ?"
- "Quelles sont les actions préventives pour la corrosion externe ?"
- "Comment est calculée la criticité F×G×D ?"

## 🔐 Authentification et Sécurité

- 🔑 Authentification à double facteur (email + code)
- 🔒 Accès limité aux utilisateurs @taqa.ma
- 🕐 Session sécurisée valable 8h
- 🔍 Traçabilité des accès et des actions

## 🛠️ Structure du Projet

```
amdec_gamme_ia/
├── app.py                  # Application Flask principale
├── requirements.txt        # Dépendances
├── README.md               # Documentation
├── core/                   # Générateurs AMDEC / Gammes
├── data/                   # Datasets, documents et fichiers générés
├── rag/                    # Moteur RAG (vectorisation + LLM)
├── ml/                     # Entraînement et prédiction IA
├── templates/              # Interface HTML (auth, amdec, gamme, chatbot)
├── static/                 # CSS, JS, images (appareils, défauts)
└── uploads/                # Fichiers uploadés par l'utilisateur
```

---

<div align="center">

💡 **Développé avec 💙 pour TAQA Morocco par l’équipe Digital Innovation**  
*Révolutionner la maintenance industrielle par l’intelligence artificielle*

© 2025 TAQA Morocco. Tous droits réservés.

</div>