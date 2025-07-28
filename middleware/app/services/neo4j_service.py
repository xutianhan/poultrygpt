from neo4j import GraphDatabase
from app.config import settings
from app.services.redis_service import r

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
    MATCH (d:Disease)-[:DIAGNOSE]->(f:Feature)
    RETURN d.diseaseID AS disease_id, d.diseaseName AS disease_name, collect(f.featureName) AS symptoms
    """
    with driver.session() as session:
        result = session.run(cypher_query)
        for record in result:
            disease_id = record["disease_id"]
            disease_name = record["disease_name"]
            symptoms = record["symptoms"]
            r.hset("disease_symptoms", disease_id, json.dumps({"disease_name": disease_name, "symptoms": symptoms}))