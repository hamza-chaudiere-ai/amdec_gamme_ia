
# RAPPORT DE SYNTHÈSE - DATASETS AMDEC & GAMME IA
Généré le : 2025-05-25 18:19:29

## 📊 DATASET AMDEC
- **Nombre total d'entrées** : 16
- **Composants uniques** : 6
- **Sous-composants uniques** : 7
- **Causes uniques** : 5

### Répartition par composant :
Composant
economiseur_bt     3
surchauffeur_ht    3
rechauffeur_bt     3
rechauffeur_ht     3
economiseur_ht     2
surchauffeur_bt    2

### Statistiques de criticité :
- **Criticité moyenne** : 20.6
- **Criticité maximale** : 45
- **Criticité minimale** : 10

### Répartition par niveau de criticité :
- **Négligeable (≤12)** : 4 entrées
- **Moyenne (13-16)** : 0 entrées
- **Élevée (17-20)** : 5 entrées
- **Critique (>20)** : 7 entrées

## 🛠️ DATASET GAMMES
- **Nombre total d'entrées** : 15
- **Composants couverts** : 6
- **Durée moyenne** : 96.3 minutes
- **Durée maximale** : 135 minutes

### Répartition par fréquence de maintenance :
Fréquence_Maintenance
Trimestrielle    8
Mensuelle        6
Semestrielle     1

### Répartition par niveau d'intervention :
Niveau_Intervention
Maintenance préventive conditionnelle    8
Remise en cause complète                 6
Maintenance préventive systématique      1

## 📈 QUALITÉ DES DONNÉES
- **Cohérence AMDEC** : ✅ Tous les composants ont des valeurs F, G, D cohérentes
- **Cohérence Gammes** : ✅ Toutes les gammes ont des durées et matériels définis
- **Couverture complète** : ✅ Tous les composants principaux sont couverts
- **Expertise intégrée** : ✅ Basé sur les modèles fournis dans le projet

## 🎯 UTILISATION RECOMMANDÉE
1. **Entraînement ML** : Utiliser ces datasets pour entraîner les modèles de prédiction
2. **Validation** : Tester les algorithmes avec ces données de référence
3. **Extension** : Ajouter de nouvelles données basées sur ces structures
4. **Amélioration continue** : Enrichir avec l'expérience terrain

## 🔧 FICHIERS GÉNÉRÉS
- `data/dataset/amdec_dataset.xlsx` : Dataset AMDEC complet
- `data/dataset/gamme_dataset.xlsx` : Dataset Gammes complet
- `data/historique/historique_model.xlsx` : Exemple d'historique
- `data/templates/amdec_template.xlsx` : Template AMDEC

## 📋 PROCHAINES ÉTAPES
1. Lancer l'application : `python app.py`
2. Tester l'upload d'historique avec le fichier exemple
3. Entraîner les modèles ML via l'interface
4. Générer des AMDEC et gammes automatiquement
