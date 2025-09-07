import json
from typing import List
from .models import RestaurantResult, MenuItem

def save_results(path: str, results: List[RestaurantResult]):
    payload = {"restaurants": [r.model_dump() for r in results]}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
