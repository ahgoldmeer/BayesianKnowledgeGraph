from pyvis import network as net
import pandas as pd
import numpy as np
from collections import defaultdict
import webbrowser
from Neo4j import Neo4jConnection

class BayesianKG:
    def __init__(self, prior_strength = 0.5, max_scale = 6.0, gamma = 0.7, max_depth = 5):
        # Prior_Strength = how strong the belief WAS
        self.edge_beliefs = {} #subj-pred-obj --> (a,b)
        self.node_reliability = defaultdict(lambda: (prior_strength, prior_strength)) #node --> (a,b)
        self.predicate_priors = defaultdict(lambda: (prior_strength, prior_strength))  # NEW: pred --> (a,b)
        self.prior_strength = prior_strength
        self.max_scale = max_scale
        self.gamma = gamma
        self.max_depth = max_depth
        self.graph_outgoing = defaultdict(list) # For recursive updates: subj --> [(pred, obj)]

    def get_evidence_scale(self, node_weight): # No static amplifier --> Dynamic amplification with max change resistance
        """Evidence scale is a hyperparameter that determines how much a belief should shift given new observations."""
        scale = (self.max_scale * node_weight)/(1 + node_weight)
        return scale

    def get_reliability(self, node):
        alpha, beta = self.node_reliability[node]
        return alpha / (alpha + beta)
    
    def update_node_reliability(self, node, confidence):
        alpha, beta = self.node_reliability[node]
        alpha += confidence
        beta += (1-confidence)
        self.node_reliability[node] = (alpha, beta)
    
    def get_node_reliability(self, node):
        return self.get_reliability(node)
    
    def update_predicate_prior(self, pred, confidence):  # NEW METHOD
        """Update predicate-level statistics"""
        alpha, beta = self.predicate_priors[pred]
        alpha += confidence
        beta += (1 - confidence)
        self.predicate_priors[pred] = (alpha, beta)
    
    def get_edge_confidence(self, subj, pred, obj): # Get confidence for a given edge
        edge_key = (subj, pred, obj)
        if edge_key not in self.edge_beliefs:
            return 0.5
        alpha, beta = self.edge_beliefs[edge_key]
        return alpha / (alpha + beta)

    def get_edge_uncertainty(self, subj, pred, obj): # Get certainty of confidence value --> variance
        edge_key = (subj, pred, obj)
        if edge_key not in self.edge_beliefs:
            return 0.25
        alpha, beta = self.edge_beliefs[edge_key]
        n = alpha + beta
        return (alpha * beta) / (n * n * (n+1))

    def add_observation(self, subj, pred, obj, confidence, depth = 0):
        edge_key = (subj, pred, obj)

        # Add node confidence as weight
        subj_reliability = self.get_reliability(subj)
        obj_reliability = self.get_reliability(obj)
        node_weight = (subj_reliability + obj_reliability)/2

        # Add edge to KG if not already there
        if edge_key not in self.edge_beliefs:
            # NEW: Initialize with predicate prior instead of generic prior
            pred_alpha, pred_beta = self.predicate_priors[pred]
            self.edge_beliefs[edge_key] = (pred_alpha, pred_beta) # set default alpha/beta before overwrite
            self.graph_outgoing[subj].append((pred, obj)) # Track outgoing edges for recursive updates

        alpha, beta = self.edge_beliefs[edge_key]

        decay = self.gamma ** depth # decay = decay factor ^ depth
        evidence_strength = self.get_evidence_scale(node_weight) * decay # Call for dynamic scaling instead of static 3x
        
        alpha += confidence * evidence_strength
        beta += (1 - confidence) * evidence_strength

        self.edge_beliefs[edge_key] = (alpha, beta) # overwrite alpha/beta

        self.update_node_reliability(subj, confidence)
        self.update_node_reliability(obj, confidence)
        self.update_predicate_prior(pred, confidence)  # NEW: Update predicate prior

        return alpha / (alpha + beta)
    
    '''
    Use neighbors of given object to recursively propagate confidence updates.
    This allows new evidence to influence related edges, with diminishing impact as we go further out.

    Infer confidence for neighbor edges based on existing beliefs
    '''
    def propagate_edge(self, subj, pred, obj, confidence, depth=0):
        if depth >= self.max_depth:
            return
        
        # Update the current edge
        self.add_observation(subj, pred, obj, confidence, depth)

        # Recursively propagate to connected edges via object neighbors
        for neighbor_pred, neighbor_obj in self.graph_outgoing[obj]:  # Propagate from obj to its outgoing edges
            # infer confidence for neighbor edge
            inferred_confidence = self.infer_confidene(obj, neighbor_obj)
            # recursive propagation with inferred confidence
            self.propagate_edge(obj, neighbor_pred, neighbor_obj, inferred_confidence, depth + 1)

    def infer_confidene(self, subj, obj):
        confidences = []
        for edge_key in self.edge_beliefs:
            s, p, o = edge_key
            if s == subj and o == obj:
                alpha, beta = self.edge_beliefs[edge_key]
                confidences.append(alpha / (alpha + beta))
            if not confidences:
                return 0.5
        return sum(confidences) / len(confidences)

def color_to_confidence(conf):
    norm_conf = (conf - 0.3) / (1.0 - 0.3)
    norm_conf = max(0, min(1, norm_conf))
    r = int(255 * (1 - norm_conf))
    g = int(255 * norm_conf)
    b = 0
    return f'rgb({r},{g},{b})'

def node_color_from_conf(conf):
    # Clamp 0–1
    conf = max(0, min(1, conf))

    if conf <= 0.5:
        # Interpolate between red (0) → pastel (0.5)
        t = conf / 0.5
        r = int(255 + t * (180 - 255))   # 255 → 180
        g = int(0   + t * (200 - 0))     # 0   → 200
        b = int(0   + t * (255 - 0))     # 0   → 255
    else:
        # Interpolate between pastel (0.5) → green (1)
        t = (conf - 0.5) / 0.5
        r = int(180 + t * (0   - 180))   # 180 → 0
        g = int(200 + t * (255 - 200))   # 200 → 255
        b = int(255 + t * (0   - 255))   # 255 → 0

    return f"rgb({r},{g},{b})"

def rgb_string_to_hex(rgb_str):
    nums = rgb_str.strip().removeprefix("rgb(").removesuffix(")")
    r, g, b = map(int, nums.split(","))
    return "#{:02X}{:02X}{:02X}".format(r, g, b)