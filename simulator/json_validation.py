from simulator.config import load_config

def validate_config(config_path):
    config = load_config(config_path)
    station_ids = set()
    item_ids = set()
    conn_ids = set()
    
    for station in config['stations']:
        if station['id'] in station_ids:
            raise ValueError(f"Duplicate station ID: {station['id']}")
        station_ids.add(station['id'])

    for item in config['items']:
        if item['id'] in item_ids:
            raise ValueError(f"Duplicate item ID: {item['id']}")
        item_ids.add(item['id'])
        
    for conn in config['connections']:
        if conn['id'] in conn_ids:
            raise ValueError(f"Duplicate connection ID: {conn['id']}")
        conn_ids.add(conn['id'])
        item = get_item_info(conn['item_id'],config)
        if conn['from_station'] not in station_ids:
            raise ValueError(f"Connection from unknown station: {conn['from_station']}")
        if conn['to_station'] not in station_ids:
            raise ValueError(f"Connection to unknown station: {conn['to_station']}")
        if conn['item_id'] not in item_ids:
            raise ValueError(f"Connection with unknown item ID: {conn['item_id']}")
        if conn['from_station'] == conn['to_station']:
            raise ValueError(f"Connection cannot be from and to the same station: {conn['from_station']}")
        if conn['from_station'] != item['produced_by']:
            raise ValueError(f"Station {conn['from_station']} does not produce item {conn['item_id']} as per item definition")
    
    station_with_recipes = set()
    
    for recipe in config['recipes']:
        recipe['station_id']
        station_with_recipes.add(recipe['station_id'])
        if recipe['station_id'] not in station_ids:
            raise ValueError(f"Recipe for unknown station: {recipe['station_id']}")
        for input_item in recipe['inputs']:
            if input_item not in item_ids:
                raise ValueError(f"Recipe for station {recipe['station_id']} has unknown input item ID: {input_item}")
        for output_item in recipe['outputs']:
            item_info = get_item_info(output_item,config)
            if item_info['produced_by'] != recipe['station_id']:
                raise ValueError(f"Recipe for station {recipe['station_id']} has unknown output item ID: {output_item} which is not produced by this station as per item definition")
            if output_item not in item_ids:
                raise ValueError(f"Recipe for station {recipe['station_id']} has unknown output item ID: {output_item}")
    
    if station_with_recipes != station_ids: 
        missing_stations = station_ids - station_with_recipes
        if missing_stations:
            raise ValueError(f"Stations without recipes: {missing_stations}")
        else:
            raise ValueError("All stations must have only one recipe")

    if config['sink_item_id'] not in item_ids:
        raise ValueError(f"Sink item ID {config['sink_item_id']} not defined in items")
        
def get_item_info(item_id,config):
    for item in config['items']:
        if item['id'] == item_id:
            return item
    raise ValueError(f"Item ID {item_id} not found in config")