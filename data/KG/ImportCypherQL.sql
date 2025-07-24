-- 1. 约束
CREATE CONSTRAINT disease_id_unique IF NOT EXISTS FOR (d:Disease) REQUIRE d.diseaseID IS UNIQUE;
CREATE CONSTRAINT feature_id_unique IF NOT EXISTS FOR (f:Feature) REQUIRE f.featureID IS UNIQUE;

-- 2. 疾病节点
LOAD CSV WITH HEADERS FROM 'file:///disease.csv' AS row
CREATE (:Disease {diseaseID: row.diseaseID, diseaseName: row.diseaseName, diseaseProperty: row.diseaseProperty});

-- 3. 症状节点
LOAD CSV WITH HEADERS FROM 'file:///feature.csv' AS row
CREATE (:Feature {featureID: row.featureID, featureName: row.featureName, featureProperty: row.featureProperty});

-- 4. 关系
USING PERIODIC COMMIT 5000
LOAD CSV WITH HEADERS FROM 'file:///relation.csv' AS row
MATCH (d:Disease {diseaseID: row.diseaseID})
MATCH (f:Feature {featureID: row.featureID})
CREATE (d)-[:RELATION {operation: row.operation, groupType: row.groupType}]->(f);