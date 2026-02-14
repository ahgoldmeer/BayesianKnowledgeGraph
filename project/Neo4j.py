from neo4j import GraphDatabase
from collections import defaultdict
from datetime import datetime

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()

    def upsert_entity(self, name, alpha, beta, reliability, color=None, size=None):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MERGE (n:Entity {name: $name})
                    SET n.alpha = $alpha,
                        n.beta = $beta,
                        n.reliability = $reliability,
                        n.color = $color,
                        n.size = $size
                    """,
                    name=name,
                    alpha=alpha,
                    beta=beta,
                    reliability=reliability,
                    color=color,
                    size=size
                )
            )
    
    def upsert_relation(self, subj, pred, obj, alpha, beta, original_confidence, confidence, uncertainty, color=None, step=None):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (s:Entity {name: $subj})
                    MATCH (o:Entity {name: $obj})
                    MERGE (s)-[r:RELATION {predicate: $pred}]->(o)
                    SET r.alpha = $alpha,
                        r.beta = $beta,
                        r.confidence = $confidence,
                        r.original_confidence = $original_confidence,
                        r.uncertainty = $uncertainty,
                        r.color = $color,
                        r.update_step = $step
                    """,
                    subj=subj,
                    obj=obj,
                    pred=pred,
                    alpha=alpha,
                    beta=beta,
                    confidence=confidence,
                    original_confidence=original_confidence,
                    uncertainty=uncertainty,
                    color=color,
                    step=step
                )
            )
    
    def log_belief_update(self, step, subj, pred, obj, alpha, beta, confidence, node_weight=None):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    CREATE (l:BeliefLog {
                        step: $step,
                        subject: $subj,
                        predicate: $pred,
                        object: $obj,
                        alpha: $alpha,
                        beta: $beta,
                        confidence: $confidence,
                        node_weight: $node_weight,
                        timestamp: $timestamp
                    })
                    """,
                    step=step,
                    subj=subj,
                    pred=pred,
                    obj=obj,
                    alpha=alpha,
                    beta=beta,
                    confidence=confidence,
                    node_weight=node_weight,
                    timestamp=datetime.utcnow().isoformat()
                )
            )
    
    def get_all_entities(self):
        with self.driver.session() as session:
            result = session.run("MATCH (n:Entity) RETURN n")
            return [record["n"] for record in result]
    
    def get_belief_trajectory(self, subj, pred, obj):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (l:BeliefLog)
                WHERE l.subject = $subj
                AND l.predicate = $pred
                AND l.object = $obj
                RETURN l
                ORDER BY l.step
                """,
                subj=subj,
                pred=pred,
                obj=obj
            )
            return [record["l"] for record in result]

# class Neo4jConnection:
#     def __init__(self, uri, user, password, prior_strength=0.5, evidence_scale=3.0):
#         self.driver = GraphDatabase.driver(uri, auth=(user, password))
#         self.prior_strength = prior_strength
#         self.evidence_scale = evidence_scale
#         self.node_reliability = defaultdict(lambda: (prior_strength, prior_strength))
#         self.predicate_priors = defaultdict(lambda: (prior_strength, prior_strength))

#     def close(self):
#         self.driver.close()

#     def add_observation(self, subj, pred, obj, confidence):
#         # Compute node weight
#         subj_rel = self.get_reliability(subj)
#         obj_rel = self.get_reliability(obj)
#         node_weight = (subj_rel + obj_rel) / 2
#         evidence_strength = node_weight * self.evidence_scale

#         # Update predicate prior
#         alpha_pred, beta_pred = self.predicate_priors[pred]
#         alpha_pred += confidence
#         beta_pred += (1 - confidence)
#         self.predicate_priors[pred] = (alpha_pred, beta_pred)

#         # Compute edge alpha/beta
#         edge_alpha = alpha_pred + confidence * evidence_strength
#         edge_beta = beta_pred + (1 - confidence) * evidence_strength
#         bayesian_conf = edge_alpha / (edge_alpha + edge_beta)

#         # Update node reliabilities
#         self.node_reliability[subj] = (self.node_reliability[subj][0] + confidence,
#                                        self.node_reliability[subj][1] + (1 - confidence))
#         self.node_reliability[obj] = (self.node_reliability[obj][0] + confidence,
#                                       self.node_reliability[obj][1] + (1 - confidence))

#         # Push to Neo4j
#         with self.driver.session() as session:
#             session.write_transaction(self._merge_nodes_and_edge, subj, obj, pred, 
#                                       edge_alpha, edge_beta, bayesian_conf)
    
#     @staticmethod
#     def _merge_nodes_and_edge(tx, subj, obj, pred, alpha, beta, conf):
#         tx.run(
#             """
#             MERGE (a:Node {name: $subj})
#             MERGE (b:Node {name: $obj})
#             SET a.alpha = COALESCE(a.alpha, 0) + $alpha,
#                 a.beta = COALESCE(a.beta, 0) + $beta,
#                 b.alpha = COALESCE(b.alpha, 0) + $alpha,
#                 b.beta = COALESCE(b.beta, 0) + $beta
#             MERGE (a)-[r:RELATION {predicate: $pred}]->(b)
#             SET r.alpha = $alpha,
#                 r.beta = $beta,
#                 r.bayesian_confidence = $conf
#             """,
#             subj=subj, obj=obj, pred=pred, alpha=alpha, beta=beta, conf=conf
#         )
