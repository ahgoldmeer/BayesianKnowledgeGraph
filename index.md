---
title: Bayesian Knowledge Graph
---

# Bayesian Knowledge Graph

Bayesian Knowledge Graph explores uncertainty-aware knowledge representation by attaching confidence values to subject-predicate-object triples and updating beliefs with Bayesian-style evidence accumulation.

## Quick Links

- [What this is](#what-this-is)
- [Main report](#main-report)
- [Core code](#core-code)
- [Data and experiments](#data-and-experiments)
- [Repository layout](#repository-layout)

## What This Is

This project extends a traditional knowledge graph with local belief updating, node reliability, and predicate-level trustworthiness. It is designed for settings where relationships are not simply true or false, but evolve as new evidence arrives.

## Main Report

- [Technical report PDF](files/BKG_Technical_Report.pdf) - the full project writeup and evaluation summary.

## Core Code

- [Bayesian KG model](project/Bayesian_KG.py) - the core belief-update logic, confidence scoring, and propagation routines.
- [CSV runner](project/CSV_Runner.py) - generates node and edge CSV outputs from the model.
- [Neo4j runner](project/Neo4j_Runner.py) - loads the model output into Neo4j for graph storage and inspection.

## Data and Experiments

- [General data](data/general/) - the main medical knowledge base in NAL format.
- [Experiment data](data/experiments/) - generated experiment inputs and outputs, including ordering and contradiction runs.
- [CN15k data](data/CN15k/) - decoded validation data and supporting ID maps.

## Repository Layout

The repository keeps the implementation, generated data, and report assets side by side so the site can point directly to the underlying project files without duplicating content.
