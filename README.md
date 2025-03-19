# Pipeline de Traitement des Données Bancaires

## Introduction générale

Ce projet implémente un pipeline de données complet pour le traitement et l'analyse en temps réel des transactions bancaires. Le système ingère des données de transaction, les traite pour la détection de fraude, les stocke dans différentes bases de données, et visualise les résultats dans un tableau de bord interactif.

Notre architecture combine plusieurs technologies de big data :
- **Apache Kafka** pour la messagerie distribuée en temps réel
- **Apache Spark** pour le traitement distribué des données
- **MongoDB** pour le stockage des données brutes de transaction
- **PostgreSQL** pour les données traitées et l'analyse
- **Dash** pour la visualisation interactive

Le flux de données passe par les étapes suivantes :
1. Ingestion des transactions via Kafka
2. Stockage des données brutes dans MongoDB
3. Traitement et enrichissement avec Spark Streaming
4. Stockage des données traitées dans PostgreSQL
5. Visualisation en temps réel via un dashboard Dash

## Configuration de l'environnement

Pour exécuter ce pipeline, vous aurez besoin de configurer les composants suivants :

### Prérequis
- Java 8 ou supérieur
- Python 3.8 ou supérieur
- Apache Kafka 3.x
- Apache Spark 3.5.x
- MongoDB 5.x
- PostgreSQL 14+

### Installation

1. Créez un environnement virtuel Python :
```bash
python -m venv data_pipeline_env
source data_pipeline_env/bin/activate
```

2. Installez les dépendances Python :
```bash
pip install kafka-python pymongo pyspark psycopg2-binary dash pandas plotly
```

3. Téléchargez et configurez Apache Kafka :
```bash
# Téléchargement et extraction de Kafka
wget https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz
tar -xzf kafka_2.13-3.5.0.tgz
cd kafka_2.13-3.5.0
```

4. Installez et configurez MongoDB :
```bash
# Sur Ubuntu
sudo apt-get install -y mongodb

# Sur macOS avec Homebrew
brew install mongodb-community
```

5. Installez et configurez PostgreSQL :
```bash
# Sur Ubuntu
sudo apt-get install -y postgresql postgresql-contrib

# Sur macOS avec Homebrew
brew install postgresql
```

6. Créez la base de données PostgreSQL pour le projet :
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE banking;
\c banking
CREATE TABLE banking_transactions (
    id SERIAL PRIMARY KEY,
    fraud_bool INTEGER,
    income FLOAT,
    customer_age INTEGER,
    intended_balcon_amount FLOAT,
    payment_type VARCHAR(50),
    employment_status VARCHAR(50),
    credit_risk_score INTEGER,
    housing_status VARCHAR(50),
    risk_category VARCHAR(10),
    fraud_probability FLOAT,
    stream_timestamp TIMESTAMP,
    spark_processing_timestamp TIMESTAMP,
    pg_insertion_timestamp TIMESTAMP
);
```

## Exécution du pipeline

Pour exécuter le pipeline complet, suivez ces étapes dans l'ordre. Vous aurez besoin de huit terminaux pour gérer tous les composants.

### Étape 1 : Démarrage du Serveur ZooKeeper

```bash
# Dans le Terminal 1
bin/zookeeper-server-start.sh config/zookeeper.properties
```

ZooKeeper est maintenant en cours d'exécution sur le port 2181 et attend des connexions.

### Étape 2 : Démarrage du Serveur Kafka

```bash
# Dans le Terminal 2
bin/kafka-server-start.sh config/server.properties
```

Notre broker Kafka est maintenant opérationnel sur le port 9092.

### Étape 3 : Activation de MongoDB et du Connecteur Kafka

```bash
# Dans le Terminal 3
source ~/data_pipeline_env/bin/activate
cd projet_finale
sudo systemctl start mongod
mongosh
```

Dans la console MongoDB, initialisez la base de données :

```
use Banking
db.transactions.deleteMany({})
```

Puis démarrez le connecteur Kafka-MongoDB :

```bash
python kafka-to-mongodb-connector.py
```

### Étape 4 : Démarrage du Processeur Spark Streaming

```bash
# Dans le Terminal 4
source ~/data_pipeline_env/bin/activate
cd projet_finale
python banking-spark-streaming.py
```

### Étape 5 : Configuration de PostgreSQL et du Connecteur de Données Traitées

```bash
# Dans le Terminal 5
source ~/data_pipeline_env/bin/activate
cd projet_finale
sudo -u postgres psql
```

Dans la console PostgreSQL :

```sql
\c banking
\dt
TRUNCATE TABLE banking_transactions;
```

Puis démarrez le connecteur PostgreSQL :

```bash
python processed-data-to-postgresql.py
```

### Étape 6 : Démarrage du Lecteur MongoDB

```bash
# Dans le Terminal 6
source ~/data_pipeline_env/bin/activate
cd projet_finale
python banking-mongodb-reader.py
```

### Étape 7 : Démarrage du Tableau de Bord

```bash
# Dans le Terminal 7
source ~/data_pipeline_env/bin/activate
cd projet_finale
python banking-dashboard.py
```

Le tableau de bord est accessible à l'adresse http://localhost:8050.

### Étape 8 : Démarrage du Producteur Kafka

```bash
# Dans le Terminal 8
source ~/data_pipeline_env/bin/activate
cd projet_finale
python banking-kafka-producer.py
```

## Structure des Fichiers

- `banking-kafka-producer.py` : Simule un flux de transactions bancaires
- `kafka-to-mongodb-connector.py` : Connecteur entre Kafka et MongoDB pour les données brutes
- `banking-spark-streaming.py` : Processeur de transactions avec Spark Streaming
- `processed-data-to-postgresql.py` : Connecteur pour stocker les données traitées dans PostgreSQL
- `banking-mongodb-reader.py` : Outil de surveillance pour les données brutes
- `banking-dashboard.py` : Application de visualisation Dash

## Licence

[Votre licence ici]
