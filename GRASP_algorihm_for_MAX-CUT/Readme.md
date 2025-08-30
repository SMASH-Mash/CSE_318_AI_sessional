Solving the Max-Cut Problem by GRASP

---

## Objective
The goal of this project is to solve the **Maximum Cut (MAX-CUT) problem** for undirected weighted graphs using various heuristics and the **GRASP (Greedy Randomized Adaptive Search Procedure)** metaheuristic. The project implements:

- Randomized Algorithm  
- Greedy Heuristic  
- Semi-Greedy Heuristic  
- Local Search  
- GRASP  

---

## Problem Description

Given an undirected graph \(G = (V, E)\) with weights \(w_{uv}\) on edges \((u, v) \in E\), the **MAX-CUT problem** aims to find a subset \(S \subset V\) such that 

The weight of the cut is:

$$
w(S, \bar{S}) = \sum_{u \in S, v \in \bar{S}} w_{uv}
$$

is maximized.  

