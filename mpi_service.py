#!/usr/bin/env python3
"""
MPI Fraud Prediction Service – Assignment 4

• Rank 0 (manager) pulls up to P requests from “transactions” (doesn’t require a full batch),
  dispatches them to worker ranks, gathers predictions, and pushes each to “results”.
• Ranks ≥1 (workers) load the broadcast RandomForest model, score each request, and return it.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any, List

from mpi4py import MPI
import joblib
from queue_manager import QueueManager

# ─── Constants ─────────────────────────────────────────────────────
TRANSACTIONS_Q = "transactions"
RESULTS_Q      = "results"
TAG_WORK, TAG_DONE, TAG_STOP = 11, 22, 99

# ─── Queue setup ──────────────────────────────────────────────────
qm = QueueManager()
for q in (TRANSACTIONS_Q, RESULTS_Q):
    try:
        qm.create_queue(q)
    except Exception:
        pass  # ignore if already exists

# ─── Helpers ──────────────────────────────────────────────────────
def fetch_requests(max_n: int) -> List[Any]:
    """Return between 1 and max_n messages; block until at least one is available."""
    while True:
        batch: List[Any] = []
        for _ in range(max_n):
            try:
                batch.append(qm.pull_message(TRANSACTIONS_Q))
            except Exception:
                break
        if batch:
            return batch
        time.sleep(0.1)

def push_prediction(pred: Any) -> None:
    # cast NumPy ints to native Python ints so JSON can serialize them
    qm.push_message(RESULTS_Q, {"prediction": int(pred)})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Distributed Fraud Prediction Service with MPI")
    parser.add_argument(
        "-p", "--processors", type=int, default=5,
        help="Max requests to fetch per batch (default: 5)"
    )
    parser.add_argument(
        "--model", default="fraud_rf_model.pkl",
        help="Path to pretrained RandomForest model"
    )
    return parser.parse_args()

# ─── Main ─────────────────────────────────────────────────────────
def main() -> None:
    cfg = parse_args()               # ← call the correct function here
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Broadcast model
    if rank == 0:
        if not Path(cfg.model).exists():
            print(f"Model file {cfg.model} not found!", file=sys.stderr)
            comm.Abort(1)
        model = joblib.load(cfg.model)
    else:
        model = None
    model = comm.bcast(model, root=0)

    if rank == 0:
        # Manager
        workers = list(range(1, size))
        print(f"[Manager] running with {len(workers)} workers", flush=True)

        while True:
            batch = fetch_requests(cfg.processors)
            print(f"[Manager] fetched {len(batch)} request(s)", flush=True)

            # Dispatch each request
            for i, req in enumerate(batch):
                comm.send(req, dest=workers[i % len(workers)], tag=TAG_WORK)

            # Collect and push results
            for _ in batch:
                result = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_DONE)
                push_prediction(result)
                print(f"[Manager] pushed result {result}", flush=True)

    else:
        # Worker
        while True:
            status = MPI.Status()
            data = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()

            if tag == TAG_WORK:
                # Extract features
                if isinstance(data, dict) and "features" in data:
                    feats = data["features"]
                else:
                    feats = data
                print(f"[Rank {rank}] got  {feats}", flush=True)

                # Predict and send back
                pred = model.predict([feats])[0]
                comm.send(pred, dest=0, tag=TAG_DONE)
                print(f"[Rank {rank}] sent {pred}", flush=True)

            elif tag == TAG_STOP:
                break

if __name__ == "__main__":
    main()
