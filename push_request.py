#!/usr/bin/env python3
import joblib
from queue_manager import QueueManager

# Initialize queue manager
qm = QueueManager()

# Determine model’s expected feature count
n = joblib.load("fraud_rf_model.pkl").n_features_in_

# Push one request with n dummy features
qm.push_message("transactions", {"features": [0.1] * n})
print("✓ queued 1 message")
