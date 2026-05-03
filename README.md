# Bayesian Knowledge Graph Project

Knowledge Graphs are widely used to represent structured information, but often assume binary truth values for entities and relationships, which limits applicability for domains where uncertain data is widespread. 

This project presents a Bayesian Knowledge Graph (BKG) framework which alters the traditional subject-predicate-object triple format with confidence values and applies Bayesian style belief updating to define relationship strength overtime. Utilizing alpha/beta distributed priors, the system updates and propagates node & edge confidence, edge beliefs, and node reliability as new evidence enters the system. 

This framework for handling uncertain data is compared against the Non-Axiomatic Reasoning System (NARS) as an alternative system for handling uncertain data, due to its inspiration of this project, and its status as a more mature framework for handling uncertain data in practice.
