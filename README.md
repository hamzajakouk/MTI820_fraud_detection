# Projet de Détection de Fraudes Bancaires en Temps Réel

## Description
Le projet de **détection de fraudes bancaires en temps réel** utilise des technologies avancées telles qu'**Apache Kafka**, **Apache Spark**, et des algorithmes d'**apprentissage automatique** pour analyser et détecter les anomalies dans les transactions bancaires. L'objectif est de prévenir les fraudes en temps réel en utilisant un pipeline de données streaming et des modèles de machine learning pour identifier les transactions suspectes.

Le projet inclut :
- Un système de collecte en temps réel des transactions via **Kafka**.
- Un traitement des données en streaming avec **Spark**.
- L'application de modèles de machine learning (Random Forest, XGBoost) pour la détection de fraudes.
- Des visualisations des résultats dans un tableau de bord **Power BI**.

## Objectifs
- Détecter les transactions frauduleuses en temps réel en utilisant des outils modernes de **big data** et de **machine learning**.
- Fournir des **tableaux de bord interactifs** pour visualiser les fraudes potentielles et les tendances.
- Créer un système robuste pour le traitement des données en streaming à grande échelle.

## Technologies Utilisées
- **Apache Kafka** : Pour la gestion des flux de données en temps réel.
- **Apache Spark** : Pour le traitement des données massives en streaming.
- **Machine Learning** :
  - **Random Forest**
  - **XGBoost**
- **Power BI** : Pour la visualisation des résultats.
- **Python** : Pour l'implémentation du prétraitement des données et des modèles d'apprentissage automatique.
- **pandas**, **scikit-learn**, **numpy** : Bibliothèques Python pour la manipulation et l'analyse des données.

## Installation et Utilisation

### Prérequis
Creez votre envirenement virtuel et activer le
```bash
python -m venv .venv
```



Vous pouvez installer les bibliothèques Python requises avec la commande suivante :
```bash
pip install -r requirements.txt
```
## Exécution du Projet

- Clonez ou téléchargez le projet dans votre répertoire local.
- Exécutez le fichier etl_script.py pour prétraiter les données :
```bash
python src/etl/etl_script.py
```
Entraînez les modèles avec train_model.py :
```bash
    python src/model/train_model.py
```
- Traitez les données en temps réel avec spark_streaming.py et kafka_producer.py / kafka_consumer.py.
- Visualisez les résultats dans Power BI à l'aide du fichier fraud_dashboard.pbix.

## Tests

Des tests unitaires et d'intégration sont inclus pour vérifier le bon fonctionnement du projet.

- Tests des modèles : Tests dans tests/test_model.py.
- Tests du processus ETL : Tests dans tests/test_etl.py.
- Tests de streaming : Tests dans tests/test_streaming.py.