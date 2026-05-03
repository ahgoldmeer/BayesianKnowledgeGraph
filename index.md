---
title: Bayesian Knowledge Graph
---

# Bayesian Knowledge Graph

Bayesian Knowledge Graph explores uncertainty-aware knowledge representation by attaching confidence values to subject-predicate-object triples and updating beliefs with Bayesian-style evidence accumulation.

## Quick Links

- [Abstract](#abstract)
- [Report](report)
- [Core Items](#core-code)
- [Data and experiments](#data-and-experiments)
<!-- - [Repository layout](#repository-layout) -->

## Abstract

 Knowledge Graphs are widely used to represent structured information, but often assume binary truth values for entities and relationships, which limits applicability for domains where uncertain data is widespread. This project presents a Bayesian Knowledge Graph (BKG) framework which alters the traditional subject-predicate-object triple format with confidence values and applies Bayesian style belief updating to define relationship strength overtime. Utilizing alpha/beta distributed priors, the system updates and propagates node \& edge confidence, edge beliefs, and node reliability as new evidence enters the system. This framework for handling uncertain data is compared against the Non-Axiomatic Reasoning System (NARS) as an alternative system for handling uncertain data, due to its inspiration of this project, and its status as a more mature framework for handling uncertain data in practice.

## Report

- [Technical report PDF](files/BKG_Technical_Report.pdf) - the full project writeup and evaluation summary.

## Core Items

- [Bayesian KG model](https://github.com/ahgoldmeer/BayesianKnowledgeGraph/tree/main/project/Bayesian_KG.py) - The core belief-update logic, confidence scoring, and propagation routines.
- [CSV runner](https://github.com/ahgoldmeer/BayesianKnowledgeGraph/tree/main/project/CSV_Runner.py) - Generates node and edge CSV outputs from the model. **Good for single loads, will overwrite old data on new runs.**
- [Neo4j runner](https://github.com/ahgoldmeer/BayesianKnowledgeGraph/tree/main/project/Neo4j_Runner.py) - Loads the model output into Neo4j for graph storage and inspection. **Data persists between data loads unless manually removed from the graph in Neo4j.**
- [Neo4j class](https://github.com/ahgoldmeer/BayesianKnowledgeGraph/tree/main/project/Neo4j.py) - Neo4j class with custom Cypher scripts to properly read out data within the graph, and load in new data.

## Data and Experiments

- [General data](https://github.com/ahgoldmeer/BayesianKnowledgeGraph/tree/main/data/general/) - the main medical knowledge base in NAL format.
- [Experiment data](https://github.com/ahgoldmeer/BayesianKnowledgeGraph/tree/main/data/experiments/) - generated inputs and outputs, including ordering and contradiction runs.
- [CN15k data](https://github.com/ahgoldmeer/BayesianKnowledgeGraph/tree/main/data/CN15k/) - decoded validation data and supporting ID maps.

<!-- ## Repository Layout

The repository keeps the implementation, generated data, and report assets side by side so the site can point directly to the underlying project files without duplicating content. -->
