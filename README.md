# Bayesian Knowledge Graph Project

Knowledge Graphs are widely used to represent structured information but often assume binary truth values for entities and relationships, which limits their applicability for domains where uncertain data is widespread. 

This project presents a Bayesian Knowledge Graph (BKG) framework which alters the traditional subject-predicate-object triple format with confidence values, and applies Bayesian belief updating todefine relationship strength over time. Utilizing beta-distributed priors, the system locally updates edge beliefs, node reliability, and predicate-level trustworthiness asnew evidence enters the system. 

Unlike a traditional Bayesian Network, it does not utilize conditional probability tables, enforce acyclic graphs, or compute global probability distribution, instead performing localized belief aggregation. Initial results suggest that the BKG framework offers an uncertainty-aware alternative for knowledge representation.
