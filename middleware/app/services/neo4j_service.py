from neo4j import GraphDatabase
from app.config import settings

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