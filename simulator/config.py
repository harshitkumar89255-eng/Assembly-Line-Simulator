import json
from pathlib import Path




def load_config(config_path):

    config_path = Path(config_path)

    with open(config_path, "r") as f:
        return json.load(f)


def get_recipe_map(config: dict):
    return {recipe["station_id"]: recipe for recipe in config["recipes"]}


def get_station_map(config: dict):
    return {station["id"]: station for station in config["stations"]}


def get_item_map(config: dict):
    return {item["id"]: item for item in config["items"]}
