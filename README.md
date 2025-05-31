# 🔧 AMDEC & Gamme IA - Assistant Intelligent de Maintenance

**AMDEC & Gamme IA** est une plateforme intelligente de génération automatique d'analyses AMDEC et de gammes de maintenance à partir d'historiques d'arrêts industriels et de datasets d'entraînement.

## 🎯 Objectifs du Projet

### Objectif Principal
Transformer vos données d'historique et datasets en :
- 📊 **Analyses AMDEC structurées** avec calculs automatiques de criticité (F×G×D)
- 🛠️ **Gammes de maintenance personnalisées** pour chaque sous-composant
- 🧠 **Intelligence artificielle** pour améliorer continuellement les prédictions
- 📋 **Documents professionnels** formatés et prêts à l'emploi

### Fonctionnalités Principales
- ✅ **Génération AMDEC** : À partir d'historique Excel ou de datasets IA
- ✅ **Gammes de maintenance** : Procédures détaillées avec images techniques
- ✅ **Machine Learning** : Prédictions intelligentes et apprentissage continu
- ✅ **Interface web moderne** : Bootstrap 5, responsive et intuitive
- ✅ **Export professionnel** : Excel AMDEC formaté, Word Gammes avec images

## 🏗️ Architecture du Projet

```
amdec_gamme_ia/
├── 📄 app.py                    # Application Flask principale
├── 📄 requirements.txt          # Dépendances Python
├── 📄 README.md                # Cette documentation
├── 📄 .gitignore               # Fichiers à ignorer
│
├── 📁 data/                    # Données et modèles
│   ├── 📁 dataset/             # Dataset d'entraînement
│   │   ├── amdec_dataset.xlsx  # Dataset AMDEC existant
│   │   └── gamme_dataset.xlsx  # Dataset Gammes existant
│   ├── 📁 historique/          # Fichiers Excel d'historique
│   ├── 📁 models/              # Modèles AMDEC de référence
│   ├── 📁 generated/           # Fichiers générés
│   │   ├── amdec/              # AMDEC générées
│   │   └── gammes/             # Gammes générées
│   └── 📁 templates/           # Templates d'export
│
├── 📁 core/                    # Logique métier principale
│   ├── __init__.py
│   ├── excel_parser.py         # Analyseur de fichiers Excel
│   ├── amdec_generator.py      # Générateur AMDEC
│   ├── gamme_generator.py      # Générateur de gammes
│   ├── data_trainer.py         # Entraînement sur dataset
│   └── utils.py                # Utilitaires communs
│
├── 📁 ml/                      # Machine Learning
│   ├── __init__.py
│   └── saved_models/           # Modèles ML sauvegardés
│
├── 📁 static/                  # Ressources web
│   ├── css/style.css           # Styles CSS personnalisés
│   ├── js/main.js              # JavaScript principal
│   └── images/                 # Images et composants
│
├── 📁 templates/               # Templates HTML
│   ├── base.html               # Template de base
│   ├── index.html              # Page d'accueil
│   ├── amdec.html              # Génération AMDEC
│   └── gamme.html              # Génération Gammes
│
└── 📁 uploads/                 # Uploads temporaires
```

## 🚀 Installation et Démarrage

### Prérequis
- **Python 3.8+** (recommandé : Python 3.9 ou 3.10)
- **pip** (gestionnaire de paquets Python)
- **Navigateur web moderne** (Chrome, Firefox, Safari, Edge)

### 1. Création du Projet
```bash
# Créer le répertoire du projet
mkdir amdec_gamme_ia
cd amdec_gamme_ia

# Créer la structure des dossiers
mkdir -p data/{dataset,historique,models,generated/{amdec,gammes},templates}
mkdir -p core ml/{saved_models} static/{css,js,images} templates uploads
```

### 2. Environnement Virtuel
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur Linux/Mac :
source venv/bin/activate
```

### 3. Installation des Dépendances
```bash
# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
python -c "import flask, pandas, sklearn; print('✅ Toutes les dépendances sont installées')"
```

### 4. Préparation des Données

#### Créer les fichiers __init__.py
```bash
# Créer les fichiers __init__.py pour les modules Python
touch core/__init__.py
touch ml/__init__.py
```

#### Dataset d'exemple (optionnel)
Si vous n'avez pas de datasets existants, l'application créera automatiquement des datasets par défaut basés sur l'expertise industrielle.

### 5. Lancement de l'Application
```bash
# Lancer l'application Flask
python app.py
```

L'application sera accessible à l'adresse : **http://localhost:5000**

## 💼 Guide d'Utilisation

### 📊 1. Génération d'AMDEC

#### À partir d'un fichier historique
1. **Accédez à la page "Génération AMDEC"**
2. **Préparez votre fichier Excel** avec les colonnes suivantes :
   - `Composant` : Nom du composant (ex: "Économiseur BT")
   - `Sous-composant` : Nom du sous-composant (ex: "Collecteur sortie")
   - `Cause` : Cause de la défaillance (ex: "Corrosion")
   - `Durée` : Durée de l'arrêt en heures (ex: 2.5)

3. **Upload du fichier** :
   - Glissez-déposez votre fichier Excel
   - Ou cliquez sur "Parcourir" pour le sélectionner
   - Formats supportés : .xlsx, .xls (max 50MB)

4. **Traitement automatique** :
   - ✅ Validation de la structure du fichier
   - ✅ Normalisation des données
   - ✅ Calcul des valeurs F, G, D
   - ✅ Génération de la criticité (C = F×G×D)
   - ✅ Export Excel formaté

#### À partir du dataset IA
1. **Sélectionnez "Génération à partir du dataset"**
2. **Choisissez le composant** dans la liste
3. **Spécifiez le sous-composant** (optionnel)
4. **L'IA génère l'AMDEC** basée sur l'apprentissage

### 🛠️ 2. Création de Gammes de Maintenance

1. **Accédez à la page "Gammes Maintenance"**
2. **Sélection du composant** :
   - Choisissez dans la liste déroulante
   - Les sous-composants se mettent à jour automatiquement
3. **Analyse de criticité** :
   - La criticité est calculée automatiquement
   - Affichage du niveau et des recommandations
4. **Génération de la gamme** :
   - ✅ Liste des matériels nécessaires
   - ✅ Opérations détaillées avec temps
   - ✅ Consignes de sécurité
   - ✅ Images techniques intégrées
   - ✅ Export Word professionnel

### 🧠 3. Entraînement des Modèles IA

1. **Page d'accueil** → Cliquez sur "Entraîner Modèles"
2. **Sélectionnez le type** :
   - Tous les modèles
   - Modèles AMDEC seulement
   - Modèles Gammes seulement
3. **Démarrage de l'entraînement** :
   - Progression en temps réel
   - Utilisation des datasets disponibles
   - Amélioration des prédictions

## 🧩 Composants Supportés

### Économiseurs
- **Économiseur BT** : Collecteur sortie, Épingle
- **Économiseur HT** : Collecteur entrée, Tubes suspension

### Surchauffeurs
- **Surchauffeur BT** : Épingle, Collecteur entrée
- **Surchauffeur HT** : Tube porteur, Branches entrée, Collecteur sortie

### Réchauffeurs
- **Réchauffeur BT** : Collecteur entrée, Tubes suspension, Tube porteur
- **Réchauffeur HT** : Branches sortie, Collecteur entrée, Collecteur sortie

## 🔧 Configuration et Personnalisation

### Paramètres de l'Application
Dans `app.py`, modifiez :
```python
# Port d'écoute
app.run(host='0.0.0.0', port=5000, debug=True)

# Taille maximale des fichiers
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

### Ajout de Nouveaux Composants
1. **Modifiez** `core/utils.py` → classe `ComponentConfig`
2. **Ajoutez** les nouvelles définitions dans `COMPONENTS`
3. **Mettez à jour** les bases de connaissances dans les générateurs

### Personnalisation des Datasets
1. **Remplacez** `data/dataset/amdec_dataset.xlsx` par vos données
2. **Colonnes requises** : Composant, Sous-composant, Cause, F, G, D, C
3. **Redémarrez** l'application pour charger les nouvelles données

## 🔍 Diagnostic et Résolution de Problèmes

### Vérification de l'État du Serveur
Accédez à : `http://localhost:5000/health`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX",
  "modules": {
    "excel_parser": true,
    "amdec_generator": true,
    "gamme_generator": true,
    "data_trainer": true
  }
}
```

### Problèmes Courants

#### 1. Erreur d'Import des Modules
```bash
# Vérifier le PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou redémarrer l'application
python app.py
```

#### 2. Fichier Excel Non Reconnu
- ✅ Vérifiez les noms de colonnes
- ✅ Assurez-vous que le fichier n'est pas corrompu
- ✅ Utilisez .xlsx plutôt que .xls si possible

#### 3. Erreur de Génération de Gamme
- ✅ Vérifiez que le composant est supporté
- ✅ Redémarrez l'application si nécessaire
- ✅ Consultez les logs pour plus de détails

#### 4. Modèles ML Non Disponibles
```bash
# Entraîner les modèles via l'interface web
# Ou via l'API :
curl -X POST http://localhost:5000/api/train_models \
  -H "Content-Type: application/json" \
  -d '{"model_type": "both"}'
```

## 📊 API Endpoints

### Génération AMDEC
```bash
# Upload historique
POST /api/upload_historique
Content-Type: multipart/form-data
Body: file=historique.xlsx

# Génération depuis dataset
POST /api/generate_amdec_from_dataset
Content-Type: application/json
Body: {"component": "economiseur_bt", "subcomponent": "epingle"}
```

### Gammes de Maintenance
```bash
# Génération gamme
POST /api/generate_gamme
Content-Type: application/json
Body: {
  "component": "economiseur_bt",
  "subcomponent": "epingle",
  "criticality": 24
}

# Calcul criticité
POST /api/criticality
Content-Type: application/json
Body: {"component": "economiseur_bt", "subcomponent": "epingle"}
```

### Machine Learning
```bash
# Entraînement modèles
POST /api/train_models
Content-Type: application/json
Body: {"model_type": "both"}

# Informations composants
GET /api/components
```

### Téléchargements
```bash
# Télécharger fichier généré
GET /download/{filename}
```

## 🔒 Sécurité et Bonnes Pratiques

### Sécurité des Fichiers
- ✅ Validation des extensions (.xlsx, .xls uniquement)
- ✅ Limitation de la taille (50MB max)
- ✅ Nettoyage automatique des fichiers temporaires
- ✅ Noms de fichiers sécurisés

### Performance
- ✅ Traitement asynchrone des gros fichiers
- ✅ Cache des modèles ML en mémoire
- ✅ Optimisation des requêtes de base de données
- ✅ Compression des réponses HTTP

### Maintenance
- ✅ Logs détaillés pour le debugging
- ✅ Point de santé (`/health`) pour monitoring
- ✅ Gestion des erreurs gracieuse
- ✅ Sauvegarde automatique des modèles

## 🚀 Déploiement en Production

### Avec Gunicorn (Recommandé)
```bash
# Installer Gunicorn
pip install gunicorn

# Lancer en production
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Avec configuration avancée
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 --max-requests 1000 app:app
```

### Variables d'Environnement
```bash
# Créer un fichier .env
export FLASK_ENV=production
export FLASK_DEBUG=False
export SECRET_KEY=your-secret-production-key
export MAX_CONTENT_LENGTH=104857600  # 100MB
```

### Avec Docker (Optionnel)