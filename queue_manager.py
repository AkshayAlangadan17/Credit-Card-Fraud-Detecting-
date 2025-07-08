"""
File-based QueueManager for Assignment 4 (shared across processes)
Stores queues in a JSON file; reloads before each operation, handles corrupt files.
"""
import json
import threading
import time
from datetime import datetime

class QueueManager:
    def __init__(self, config_path='config.json'):
        # Load config
        with open(config_path, 'r') as f:
            cfg = json.load(f)
        self.max_len = cfg.get("max_messages_per_queue", 100)
        self.storage_path = cfg.get("storage_path", "queues.json")
        self.lock = threading.Lock()
        # Load existing queues or start fresh if missing/corrupt
        self.load_queues()

    def load_queues(self):
        try:
            with open(self.storage_path, 'r') as f:
                self.queues = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.queues = {}

    def save_queues(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.queues, f, indent=2)

    def create_queue(self, name: str):
        with self.lock:
            self.load_queues()
            if name in self.queues:
                raise Exception(f"Queue '{name}' already exists.")
            self.queues[name] = []
            self.save_queues()

    def delete_queue(self, name: str):
        with self.lock:
            self.load_queues()
            if name not in self.queues:
                raise Exception(f"Queue '{name}' does not exist.")
            del self.queues[name]
            self.save_queues()

    def push_message(self, queue_name: str, message):
        with self.lock:
            self.load_queues()
            if queue_name not in self.queues:
                raise Exception(f"Queue '{queue_name}' does not exist.")
            if len(self.queues[queue_name]) >= self.max_len:
                raise Exception(f"Queue '{queue_name}' is full.")
            # Attach timestamp only if dict
            if isinstance(message, dict):
                message['__queued_at'] = datetime.now().isoformat()
            self.queues[queue_name].append(message)
            self.save_queues()

    def pull_message(self, queue_name: str):
        with self.lock:
            self.load_queues()
            if queue_name not in self.queues:
                raise Exception(f"Queue '{queue_name}' does not exist.")
            if not self.queues[queue_name]:
                raise Exception(f"Queue '{queue_name}' is empty.")
            msg = self.queues[queue_name].pop(0)
            self.save_queues()
            return msg
