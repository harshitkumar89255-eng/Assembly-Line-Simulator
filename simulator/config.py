import json
from pathlib import Path


def load_config(path: str|Path):
    conf_path = Path(path)
    if not conf_path.is_absolute():
        project_root = Path(__file__).resolve().parent.parent
        conf_path = project_root / conf_path

    if not conf_path.exists():
        raise FileNotFoundError(f"Config file not found: {conf_path}")

    with open(conf_path, "r", encoding="utf-8") as f:
        return json.load(f)    


def get_recipe_map(config: dict):
    return {recipe["station_id"]: recipe for recipe in config["recipes"]}


def get_station_map(config: dict):
    return {station["id"]: station for station in config["stations"]}


def get_item_map(config: dict):
    return {item["id"]: item for item in config["items"]}
