from neo4j import GraphDatabase
from app.config import settings
from app.services.redis_service import r
import json

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
    max_connection_pool_size=20,
)

def query_graph(tx, symptom: str):
    cypher = """
    MATCH (s:Symptom {name: $symptom})-[:INDICATES]->(d:Disease)
    RETURN d.name AS disease
    LIMIT 5
    """
    return tx.run(cypher, symptom=symptom).data()

def get_diseases_by_symptom(symptom: str):
    with driver.session() as session:
        return session.execute_read(query_graph, symptom)

def preload_diseases_with_symptoms():
    cypher_query = """
    MATCH (d:Disease)-[:RELATION]->(f:Feature)
    RETURN d.diseaseID AS disease_id, d.diseaseName AS disease_name, collect(f.featureName) AS symptoms
    """
    with driver.session() as session:
        result = session.run(cypher_query)
        for record in result:
            disease_id = record["disease_id"]
            disease_name = record["disease_name"]
            symptoms = record["symptoms"]
            r.hset("disease_symptoms", disease_id, json.dumps({"disease_name": disease_name, "symptoms": symptoms}))

from neo4j import GraphDatabase
from app.config import settings
from app.services.redis_service import r
import json

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
    max_connection_pool_size=20,
)

def query_graph(tx, symptom: str):
    cypher = """
    MATCH (s:Symptom {name: $symptom})-[:INDICATES]->(d:Disease)
    RETURN d.name AS disease
    LIMIT 5
    """
    return tx.run(cypher, symptom=symptom).data()

def get_diseases_by_symptom(symptom: str):
    with driver.session() as session:
        return session.execute_read(query_graph, symptom)

def preload_diseases_with_symptoms():
    cypher_query = """
    MATCH (d:Disease)-[:RELATION]->(f:Feature)
    RETURN d.diseaseID AS disease_id, d.diseaseName AS disease_name, collect(f.featureName) AS symptoms
    """
    with driver.session() as session:
        result = session.run(cypher_query)
        for record in result:
            disease_id = record["disease_id"]
            disease_name = record["disease_name"]
            symptoms = record["symptoms"]
            r.hset("disease_symptoms", disease_id, json.dumps({"disease_name": disease_name, "symptoms": symptoms}))

def get_suggested_symptoms(disease_ids: list, existing_symptoms: list):
    """
    根据疾病 ID 和已有症状，推荐其他可能相关的症状。
    """
    cypher_query = """
    MATCH (d:Disease)-[:RELATION]->(f:Feature)
    WHERE d.diseaseID IN $disease_ids AND NOT (f.featureName IN $existing_symptoms)
    RETURN DISTINCT f.featureName AS symptom
    LIMIT 5
    """
    with driver.session() as session:
        result = session.run(cypher_query, disease_ids=disease_ids, existing_symptoms=existing_symptoms)
        suggested_symptoms = [record["symptom"] for record in result]
        return suggested_symptoms
