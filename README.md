# Distributed Systems – Assignment 4
**High‑Performance Fraud Prediction with MPI**

## Overview
This service parallelises fraud prediction across `P` worker processes (default 5) using `mpi4py` + Open MPI.  
Rank 0 (manager) pulls requests from the **transactions** queue, distributes them to workers (rank ≥ 1), collects predictions, and pushes each to the **results** queue.

## Requirements
* Python 3.12
* Open MPI + `mpi4py`
* `joblib`, `scikit‑learn`
* Your `queue_manager.py` & `config.json` from Assignment 3  
  (already included here)
* Pre‑trained model `fraud_rf_model.pkl` (place in same folder)

## Running Locally

```bash
mpirun -np 6 python mpi_service.py --processors 5
```

*`-np` = manager (1) + workers (5) = 6.*

## Docker (Bonus)

```bash
docker compose build
docker compose up --scale worker=5
```

Compose spins up one **manager** plus five **worker** containers on the same `mpi-net` and launches the MPI job automatically.

## File List
| File | Purpose |
|------|---------|
| `mpi_service.py` | Main MPI application |
| `queue_manager.py` | Queue implementation (copied from Assignment 3) |
| `config.json` | Queue config (copied from Assignment 3) |
| `Dockerfile` | Builds the container image |
| `docker-compose.yml` | Optional multi‑container cluster |
| `fraud_rf_model.pkl` | Pre‑trained model (add your copy) |
| `README.md` | This document |

## Packaging
```bash
zip -r assignment4_yourname.zip .
```
