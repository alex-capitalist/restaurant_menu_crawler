import json
from typing import Dict, Any

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_inputs(restaurants_path: str, menutypes_path: str, formats_path: str):
    restaurants = load_json(restaurants_path)["Restaurants"]
    menutypes = load_json(menutypes_path)["menus"]
    formats = load_json(formats_path)["menus"]
    return restaurants, menutypes, formats
