import json
import os
import logging
from rapidfuzz import process

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.data = {}
        self.load_all()

    def load_all(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            return

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                key = filename.replace(".json", "")
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.data[key] = json.load(f)
                    logging.info(f"Loaded {filename} successfully.")
                except Exception as e:
                    logging.error(f"Error loading {filename}: {e}")

    def get_collection(self, collection_name):
        return self.data.get(collection_name, {})

    def find_item(self, collection_name, query):
        collection = self.get_collection(collection_name)
        if not collection:
            return None

        choices = list(collection.keys())
        if not choices: return None

        query_clean = query.lower().replace(" ", "_")
        if query_clean in choices:
            return collection[query_clean]

        result = process.extractOne(query.lower(), choices)
        if result:
            best_match, score, index = result
            if score >= 75:
                return collection[best_match]
        return None

    def reload(self):
        self.data = {}
        self.load_all()

    def get_all_keys(self, collection_name):
        return list(self.get_collection(collection_name).keys())

# Singleton instance
data_manager = DataManager()
