#!/usr/bin/env python3
import time
from queue_manager import QueueManager

# Initialize queue manager
qm = QueueManager()

# Poll until a result appears
while True:
    try:
        msg = qm.pull_message("results")
        print("→ received:", msg)
        break
    except Exception:
        time.sleep(0.1)  # wait 100ms and retry
