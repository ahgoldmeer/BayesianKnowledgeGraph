from pathlib import Path
from Bayesian_KG import BayesianKG, node_color_from_conf, color_to_confidence, rgb_string_to_hex
from Neo4j import Neo4jConnection
import pandas as pd
from pathlib import Path

def main():

    bkg = BayesianKG(prior_strength=0.5, max_scale=6.0)
    neo4j = Neo4jConnection(uri="neo4j://127.0.0.1:7687", user="neo4j", password="password")

    BASE_DIR = Path(__file__).resolve().parent      # MAIN/project
    csv_path = BASE_DIR.parent / "data" / "MedData.csv"  # MAIN/data/csv
    df = pd.read_csv(csv_path)

    for row in df.itertuples(index=False):
        subj = row.Subject
        pred = row.Predicate
        obj = row.Object
        conf = row.Confidence

        bkg.propagate_edge(subj, pred, obj, conf, depth=0)

    for node, (a, b) in bkg.node_reliability.items():
        reliability = bkg.get_node_reliability(node)
        neo4j.upsert_entity(
            name = node,
            alpha = a,
            beta = b,
            reliability = reliability,
            color = rgb_string_to_hex(node_color_from_conf(reliability)),
            size = 10 + 20 * reliability
        )

    step = 0
    for (subj, pred, obj), (edge_alpha, edge_beta) in bkg.edge_beliefs.items():
        confidence = edge_alpha / (edge_alpha + edge_beta)
        uncertainty = bkg.get_edge_uncertainty(subj, pred, obj)

        neo4j.upsert_relation(
            subj = subj,
            pred = pred,
            obj = obj,
            alpha = edge_alpha,
            beta = edge_beta,
            confidence = confidence,
            original_confidence = df.Confidence[step] if step < len(df) else None,
            uncertainty = uncertainty,
            color = rgb_string_to_hex(color_to_confidence(confidence))
        )
        step += 1

    # for step, row in enumerate(df.itertuples(index=False)):
    #     subj = row.Subject
    #     pred = row.Predicate
    #     obj = row.Object
    #     conf = row.Confidence

    #     bayes_conf = bkg.add_observation(subj, pred, obj, conf)

    #     edge_alpha, edge_beta = bkg.edge_beliefs[(subj, pred, obj)]
    #     # print(f"Step {step}: ({subj}, {pred}, {obj}) - Confidence: {conf:.2f} | Bayesian Confidence: {bayes_conf:.4f} | Edge Alpha: {edge_alpha:.2f}, Beta: {edge_beta:.2f}")

    #     uncertainty = bkg.get_edge_uncertainty(subj, pred, obj)
    #     # print(f"Uncertainty for edge ({subj}, {pred}, {obj}): {uncertainty:.4f}")

    #     for node in (subj, obj):
    #         a, b = bkg.node_reliability[node]
    #         reliability = bkg.get_node_reliability(node)
    #         # print(f"Node '{node}' - Reliability: {reliability:.4f} | Alpha: {a:.2f}, Beta: {b:.2f}")

    #         neo4j.upsert_entity(
    #             name = node,
    #             alpha = a,
    #             beta = b,
    #             reliability = reliability,
    #             color = rgb_string_to_hex(node_color_from_conf(reliability)),
    #             size = 10 + 20 * reliability
    #         )
        
    #     neo4j.upsert_relation(
    #         subj = subj,
    #         pred = pred,
    #         obj = obj,
    #         alpha = edge_alpha,
    #         beta = edge_beta,
    #         confidence = bayes_conf,
    #         uncertainty = uncertainty,
    #         color = rgb_string_to_hex(color_to_confidence(bayes_conf)),
    #         step=step
    #     )

    neo4j.close()

if __name__ == "__main__":
    main()