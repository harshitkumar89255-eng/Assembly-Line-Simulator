import copy
class Scenario:
    def __init__(self,config:dict):
        self.base_config = copy.deepcopy(config)
        self.changes = []
        self.config = copy.deepcopy(config)
        
    def apply_cycle_time_change(self,station_id:str,new_cycle_time:float):
        for station in self.config['stations']:
            if station['id'] == station_id:
                station['cycle_time'] = new_cycle_time
                self.changes.append(f"Cycle time of station {station_id} changed to {new_cycle_time}")
                return self
        raise ValueError(f"Station with id {station_id} not found")
    
    def apply_buffer_capacity_change(self,connection_id:str,new_capacity:int):
        for conn in self.config['connections']:
            if conn['id'] == connection_id:
                conn['buffer_capacity'] = new_capacity
                self.changes.append(f"Buffer capacity of connection {connection_id} changed to {new_capacity}")
                return self
        raise ValueError(f"Connection with id {connection_id} not found")

    def apply_recipe_input_change(self,station_id:str,item_id:str,qty:int):
        for recipe in self.config['recipes']:
            if recipe['station_id'] == station_id:
                if item_id not in recipe['inputs']:
                    raise ValueError(f"Item {item_id} not found in inputs of station {station_id}")
                recipe['inputs'][item_id] = qty
                self.changes.append(f"Input {item_id} of station {station_id} changed to {qty}")
                return self
        raise ValueError(f"Recipe for Station: {station_id} not found")
    
    def apply_recipe_output_change(self,station_id:str,item_id:str,new_qty:int):
        for recipe in self.config['recipes']:
            if recipe['station_id'] == station_id:
                if item_id not in recipe['outputs']:
                    raise ValueError(f"Item {item_id} not found in outputs of station {station_id}")
                recipe['outputs'][item_id] = new_qty
                self.changes.append(f"Output {item_id} of station {station_id} changed to {new_qty}")
                return self
        raise ValueError(f"Recipe for Station: {station_id} not found")
    
    def get_config(self):
        return self.config
    
    def reset(self):
        self.config = copy.deepcopy(self.base_config)
        self.changes = []
        return self 