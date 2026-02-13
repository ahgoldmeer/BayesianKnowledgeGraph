from pathlib import Path
from Bayesian_KG import BayesianKG, node_color_from_conf, color_to_confidence, rgb_string_to_hex
import pandas as pd

def main():
    bkg = BayesianKG(prior_strength=0.5, max_scale=6.0)

    BASE_DIR = Path(__file__).resolve().parent      # MAIN/project
    csv_path = BASE_DIR.parent / "data" / "MedData.csv"  # MAIN/data/csv
    df = pd.read_csv(csv_path)

    # Prepare lists to store CSV rows
    node_rows = []
    edge_rows = []

    for step, row in enumerate(df.itertuples(index=False)):
        subj = row.Subject
        pred = row.Predicate
        obj = row.Object
        conf = row.Confidence

        bayes_conf = bkg.add_observation(subj, pred, obj, conf)

        edge_alpha, edge_beta = bkg.edge_beliefs[(subj, pred, obj)]
        uncertainty = bkg.get_edge_uncertainty(subj, pred, obj)

        # Process nodes
        for node in (subj, obj):
            a, b = bkg.node_reliability[node]
            reliability = bkg.get_node_reliability(node)
            node_rows.append({
                "name": node,
                "alpha": a,
                "beta": b,
                "reliability": reliability,
                "color": rgb_string_to_hex(node_color_from_conf(reliability)),
                "size": 10 + 20 * reliability
            })

        # Process edge
        edge_rows.append({
            "subj": subj,
            "pred": pred,
            "obj": obj,
            "alpha": edge_alpha,
            "beta": edge_beta,
            "confidence": bayes_conf,
            "original_confidence": conf,
            "uncertainty": uncertainty,
            "color": rgb_string_to_hex(color_to_confidence(bayes_conf)),
            "step": step
        })

    # Convert lists to DataFrames
    nodes_df = pd.DataFrame(node_rows).drop_duplicates(subset=["name"], keep="last")  # Ensure unique nodes
    edges_df = pd.DataFrame(edge_rows)

    # Save CSVs
    output_dir = BASE_DIR.parent / "data"
    nodes_df.to_csv(output_dir / "nodes.csv", index=False)
    edges_df.to_csv(output_dir / "edges.csv", index=False)

    print(f"Saved {len(nodes_df)} nodes and {len(edges_df)} edges to CSV.")

if __name__ == "__main__":
    main()
