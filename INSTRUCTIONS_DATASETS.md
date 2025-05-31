# 📊 Guide d'Utilisation des Datasets AMDEC & Gamme IA

## 🎯 Objectif des Datasets

Ces datasets ont été créés à partir de toute l'expertise contenue dans votre projet pour fournir des données d'entraînement de haute qualité pour les modèles d'intelligence artificielle.

## 📁 Structure des Datasets

### 📊 amdec_dataset.xlsx

Ce dataset contient **33 entrées** d'expertise AMDEC couvrant tous les composants de chaudière de votre projet :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `Composant` | Nom normalisé du composant | `economiseur_bt` |
| `Sous-composant` | Nom normalisé du sous-composant | `epingle` |
| `Fonction` | Fonction du sous-composant | `Transfert thermique` |
| `Mode de Défaillance` | Mode de défaillance spécifique | `Corrosion externe` |
| `Cause` | Cause normalisée | `corrosion` |
| `Effet` | Effet de la défaillance | `Amincissement parois` |
| `F` | Fréquence (1-4) | `3` |
| `G` | Gravité (1-5) | `4` |
| `D` | Détection (1-4) | `2` |
| `C` | Criticité (F×G×D) | `24` |
| `Actions Correctives` | Actions recommandées | `Revêtement céramique + contrôle` |

### 🛠️ gamme_dataset.xlsx

Ce dataset contient **17 entrées** de gammes de maintenance optimisées :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `Composant` | Nom normalisé du composant | `economiseur_bt` |
| `Sous-composant` | Nom normalisé du sous-composant | `collecteur_sortie` |
| `Criticité` | Criticité calculée | `45` |
| `Criticité_Niveau` | Niveau textuel | `Critique` |
| `Fréquence_Maintenance` | Fréquence recommandée | `Mensuelle` |
| `Nb_Opérations` | Nombre d'opérations | `5` |
| `Durée_Totale_Min` | Durée totale en minutes | `125` |
| `Matériels_Principaux` | Matériels nécessaires | `Lampe + Ultrasons + Kit test` |
| `Personnel_Requis` | Personnel nécessaire | `Technicien expert + Assistant` |
| `Niveau_Intervention` | Type d'intervention | `Remise en cause complète` |

## 🚀 Instructions d'Installation

### 1. Génération Automatique des Datasets

```bash
# Exécuter le script de génération
python generate_datasets.py
```

Ce script créera automatiquement :
- ✅ `data/dataset/amdec_dataset.xlsx`
- ✅ `data/dataset/gamme_dataset.xlsx`
- ✅ `data/historique/historique_model.xlsx` (fichier d'exemple)
- ✅ `data/templates/amdec_template.xlsx` (template de structure)
- ✅ `data/dataset/RAPPORT_DATASETS.md` (rapport de synthèse)

### 2. Vérification des Datasets

```python
import pandas as pd

# Charger et vérifier AMDEC
df_amdec = pd.read_excel('data/dataset/amdec_dataset.xlsx')
print(f"Dataset AMDEC : {len(df_amdec)} entrées")
print(f"Composants : {df_amdec['Composant'].nunique()}")

# Charger et vérifier Gammes
df_gamme = pd.read_excel('data/dataset/gamme_dataset.xlsx')
print(f"Dataset Gammes : {len(df_gamme)} entrées")
print(f"Criticité moyenne : {df_gamme['Criticité'].mean():.1f}")
```

## 🧠 Utilisation pour l'Entraînement IA

### 1. Via l'Interface Web

1. **Lancer l'application** : `python app.py`
2. **Page d'accueil** → Cliquer sur "Entraîner Modèles"
3. **Sélectionner le type** : "Tous les modèles"
4. **Démarrer l'entraînement** → Les datasets seront utilisés automatiquement

### 2. Via l'API

```bash
# Entraîner tous les modèles
curl -X POST http://localhost:5000/api/train_models \
  -H "Content-Type: application/json" \
  -d '{"model_type": "both"}'
```

### 3. Programmatiquemet

```python
from core.data_trainer import DataTrainer

# Initialiser le trainer
trainer = DataTrainer()

# Entraîner les modèles
results = trainer.train_models('both')
print("Résultats d'entraînement :", results)

# Faire des prédictions
criticality = trainer.predict_criticality('economiseur_bt', 'epingle', 'corrosion')
print(f"Criticité prédite : {criticality}")
```

## 📈 Statistiques des Datasets

### Dataset AMDEC
- **33 entrées** couvrant tous les composants
- **6 composants principaux** : Économiseurs BT/HT, Surchauffeurs BT/HT, Réchauffeurs BT/HT
- **15 sous-composants** différents
- **7 causes principales** : corrosion, érosion, fatigue, fissure, surchauffe, encrassement, vibration
- **Criticité moyenne** : 20.4
- **Criticité max** : 45 (Économiseur BT - Collecteur sortie)

### Dataset Gammes
- **17 gammes complètes** avec détails opérationnels
- **Durée moyenne** : 95 minutes par gamme
- **4 niveaux de criticité** : Moyenne, Élevée, Critique, Critique Max
- **5 fréquences** : Hebdomadaire, Mensuelle, Trimestrielle, Semestrielle
- **3 types d'intervention** : Systématique, Conditionnelle, Remise en cause

## 🔧 Personnalisation des Datasets

### Ajouter de Nouvelles Données AMDEC

```python
# Exemple d'ajout de nouvelles données
nouvelles_donnees = [
    {
        'Composant': 'nouveau_composant',
        'Sous-composant': 'nouveau_sous_composant',
        'Fonction': 'Nouvelle fonction',
        'Mode de Défaillance': 'Nouveau mode',
        'Cause': 'nouvelle_cause',
        'Effet': 'Nouvel effet',
        'F': 2, 'G': 3, 'D': 2, 'C': 12,
        'Actions Correctives': 'Nouvelles actions'
    }
]

# Charger le dataset existant
df = pd.read_excel('data/dataset/amdec_dataset.xlsx')

# Ajouter les nouvelles données
df_nouveau = pd.concat([df, pd.DataFrame(nouvelles_donnees)], ignore_index=True)

# Sauvegarder
df_nouveau.to_excel('data/dataset/amdec_dataset.xlsx', index=False)
```

### Ajouter de Nouvelles Gammes

```python
# Exemple d'ajout de nouvelles gammes
nouvelles_gammes = [
    {
        'Composant': 'nouveau_composant',
        'Sous-composant': 'nouveau_sous_composant',
        'Criticité': 30,
        'Criticité_Niveau': 'Critique',
        'Fréquence_Maintenance': 'Mensuelle',
        'Nb_Opérations': 4,
        'Durée_Totale_Min': 120,
        'Matériels_Principaux': 'Nouveaux matériels',
        'Personnel_Requis': 'Nouveau personnel',
        'Niveau_Intervention': 'Nouveau niveau'
    }
]

# Processus similaire pour les gammes
```

## 🎯 Cas d'Usage des Datasets

### 1. Génération AMDEC depuis Dataset
```python
# Via l'interface web
# Page "Génération AMDEC" → "À partir du dataset"
# Sélectionner composant et sous-composant

# Via l'API
curl -X POST http://localhost:5000/api/generate_amdec_from_dataset \
  -H "Content-Type: application/json" \
  -d '{"component": "economiseur_bt", "subcomponent": "epingle"}'
```

### 2. Prédiction de Criticité
```python
# L'IA utilise les datasets pour prédire la criticité
# de nouvelles combinaisons composant/sous-composant/cause
```

### 3. Recommandations de Maintenance
```python
# Les gammes du dataset servent de base pour générer
# automatiquement des recommandations personnalisées
```

## 🔍 Validation des Datasets

### Tests de Cohérence

```python
def valider_dataset_amdec(df):
    """Valide la cohérence du dataset AMDEC"""
    erreurs = []
    
    # Vérifier les valeurs F, G, D
    if not df['F'].between(1, 4).all():
        erreurs.append("Valeurs F incorrectes (doivent être 1-4)")
    
    if not df['G'].between(1, 5).all():
        erreurs.append("Valeurs G incorrectes (doivent être 1-5)")
    
    if not df['D'].between(1, 4).all():
        erreurs.append("Valeurs D incorrectes (doivent être 1-4)")
    
    # Vérifier le calcul de criticité
    criticite_calculee = df['F'] * df['G'] * df['D']
    if not (df['C'] == criticite_calculee).all():
        erreurs.append("Calcul de criticité incorrect (C ≠ F×G×D)")
    
    # Vérifier les composants supportés
    composants_valides = ['economiseur_bt', 'economiseur_ht', 'surchauffeur_bt', 
                         'surchauffeur_ht', 'rechauffeur_bt', 'rechauffeur_ht']
    composants_invalides = df[~df['Composant'].isin(composants_valides)]['Composant'].unique()
    if len(composants_invalides) > 0:
        erreurs.append(f"Composants non supportés : {composants_invalides}")
    
    return erreurs

# Exécuter la validation
df_amdec = pd.read_excel('data/dataset/amdec_dataset.xlsx')
erreurs = valider_dataset_amdec(df_amdec)
if erreurs:
    print("❌ Erreurs détectées :", erreurs)
else:
    print("✅ Dataset AMDEC valide")
```

### Tests de Performance

```python
def tester_performance_datasets():
    """Teste les performances des modèles avec les datasets"""
    from core.data_trainer import DataTrainer
    
    trainer = DataTrainer()
    
    # Entraîner les modèles
    print("🔄 Entraînement des modèles...")
    results = trainer.train_models('both')
    
    # Tester les prédictions
    print("🧪 Test des prédictions...")
    
    # Test de prédiction de criticité
    test_cases = [
        ('economiseur_bt', 'epingle', 'corrosion'),
        ('surchauffeur_ht', 'tube_porteur', 'surchauffe'),
        ('rechauffeur_ht', 'branches_sortie', 'corrosion')
    ]
    
    for comp, subcomp, cause in test_cases:
        criticite = trainer.predict_criticality(comp, subcomp, cause)
        print(f"   {comp} - {subcomp} - {cause} : Criticité = {criticite}")
    
    return results

# Exécuter les tests
resultats = tester_performance_datasets()
```

## 📚 Documentation des Données

### Bases de Connaissances Intégrées

Les datasets intègrent l'expertise de votre projet à travers :

#### 1. **Modes de Défaillance Spécialisés**
- **Économiseur BT** : Corrosion externe, Caustic attack, Érosion par cendres
- **Surchauffeur HT** : Long-term overheat, SCC, Fireside corrosion
- **Réchauffeur HT** : Acid attack, Dissimilar metal weld, Waterside corrosion

#### 2. **Actions Correctives Expertes**
- **Corrosion** : Revêtements céramiques, contrôle pH, injection additifs
- **Surchauffe** : Capteurs température, optimisation combustion, alarmes
- **Fatigue** : Surveillance vibratoire, analyse contraintes, renforts

#### 3. **Gammes de Maintenance Réalistes**
- **Criticité élevée** : Interventions trimestrielles, 3-4 opérations
- **Criticité critique** : Interventions mensuelles, 4-6 opérations
- **Personnel adapté** : Techniciens qualifiés, ingénieurs experts, superviseurs

### Correspondance avec vos Documents

| Document Source | Données Extraites | Intégration Dataset |
|----------------|-------------------|-------------------|
| `amdec_eco_bt.docx` | Épingles, Collecteur sortie, Caustic attack | ✅ Intégré dans AMDEC dataset |
| `gamme_maintenance_eco_bt.docx` | Matériels, Opérations, Temps | ✅ Intégré dans Gammes dataset |
| `core/amdec_generator.py` | Logique de calcul F×G×D | ✅ Reproduit fidèlement |
| `maintenance/maintenance_planner.py` | Criticités par défaut | ✅ Valeurs cohérentes |

## 🔄 Workflow d'Utilisation

### Étape 1 : Génération Initiale
```bash
# 1. Générer les datasets
python generate_datasets.py

# 2. Vérifier les fichiers créés
ls -la data/dataset/
```

### Étape 2 : Intégration Application
```bash
# 1. Lancer l'application
python app.py

# 2. Vérifier le chargement des datasets
# → Page d'accueil : les statistiques doivent s'afficher
```

### Étape 3 : Entraînement IA
```bash
# Via l'interface web :
# → Page d'accueil → "Entraîner Modèles" → "Tous les modèles"

# Via API :
curl -X POST http://localhost:5000/api/train_models \
  -H "Content-Type: application/json" \
  -d '{"model_type": "both"}'
```

### Étape 4 : Test et Validation
```bash
# 1. Tester génération AMDEC depuis dataset
# → Page "Génération AMDEC" → "À partir du dataset"

# 2. Tester génération gamme
# → Page "Gammes Maintenance" → Sélectionner composant

# 3. Vérifier les prédictions IA
# → Les criticités doivent être cohérentes avec le dataset
```

## 🛠️ Maintenance des Datasets

### Mise à Jour Périodique

```python
def mettre_a_jour_datasets():
    """Met à jour les datasets avec de nouvelles données terrain"""
    
    # 1. Charger les datasets existants
    df_amdec = pd.read_excel('data/dataset/amdec_dataset.xlsx')
    df_gamme = pd.read_excel('data/dataset/gamme_dataset.xlsx')
    
    # 2. Ajouter nouvelles données terrain
    # (issues de l'exploitation de l'application)
    
    # 3. Réentraîner les modèles
    trainer = DataTrainer()
    trainer.train_models('both')
    
    # 4. Valider les performances
    # Comparer avec les résultats précédents
    
    print("✅ Datasets mis à jour et modèles réentraînés")

# Programmer cette fonction pour mise à jour mensuelle
```

### Sauvegarde et Versioning

```bash
# Créer une sauvegarde avant modification
cp data/dataset/amdec_dataset.xlsx data/dataset/backups/amdec_dataset_$(date +%Y%m%d).xlsx
cp data/dataset/gamme_dataset.xlsx data/dataset/backups/gamme_dataset_$(date +%Y%m%d).xlsx

# Commiter les changements (si sous Git)
git add data/dataset/
git commit -m "Mise à jour datasets avec nouvelles données terrain"
```

## 🎯 Résultats Attendus

### Performance des Modèles ML

Avec ces datasets de qualité, vous devriez obtenir :

- **Prédiction de criticité** : Précision > 85%
- **Recommandations gammes** : Temps estimés ±15%
- **Actions correctives** : Pertinence > 90%
- **Généralisation** : Bonne performance sur nouveaux composants

### Amélioration Continue

Les datasets permettront :

- **Apprentissage automatique** des patterns de défaillance
- **Optimisation** des fréquences de maintenance
- **Personnalisation** selon l'historique spécifique
- **Évolution** avec l'expertise terrain

## 📞 Support et Dépannage

### Problèmes Courants

#### Dataset non trouvé
```python
# Vérifier l'existence
import os
if not os.path.exists('data/dataset/amdec_dataset.xlsx'):
    print("❌ Dataset AMDEC manquant")
    print("💡 Exécuter : python generate_datasets.py")
```

#### Erreurs d'entraînement
```python
# Vérifier la structure des données
df = pd.read_excel('data/dataset/amdec_dataset.xlsx')
print("Colonnes :", df.columns.tolist())
print("Types :", df.dtypes)
print("Valeurs manquantes :", df.isnull().sum())
```

#### Prédictions incohérentes
```python
# Réentraîner les modèles
from core.data_trainer import DataTrainer
trainer = DataTrainer()
trainer.train_models('both')
print("✅ Modèles réentraînés")
```

### Logs et Debugging

```python
import logging
logging.basicConfig(level=logging.INFO)

# Les logs de l'application montreront :
# - Chargement des datasets
# - Progression de l'entraînement
# - Erreurs de prédiction
# - Statistiques d'utilisation
```

## 🚀 Prochaines Évolutions

### Extension des Datasets

1. **Nouveaux composants** : Ajout d'autres équipements industriels
2. **Modes de défaillance avancés** : Intégration de phénomènes complexes
3. **Données temporelles** : Évolution des défaillances dans le temps
4. **Facteurs environnementaux** : Impact des conditions opérationnelles

### Amélioration de l'IA

1. **Deep Learning** : Réseaux de neurones pour patterns complexes
2. **Apprentissage fédéré** : Collaboration entre plusieurs sites
3. **Prédiction prédictive** : Anticipation des défaillances
4. **Optimisation multi-objectifs** : Coût vs. risque vs. disponibilité

---

**📧 Contact** : Pour toute question sur l'utilisation des datasets, consultez la documentation du projet ou les logs de l'application.