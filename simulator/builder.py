import json
from pathlib import Path   
    
class Builder:
    def __init__(self):
        self.station_ids = []
        self.items = []
        
        self.data = {
            "simulation": {},
            "stations": [],
            "items": [],
            "connections": [],
            "recipes": [],
            "sink_item_id": None
        }
    def define_simulation(self,duration,tick):
        self.data["simulation"]["duration"] = duration
        self.data["simulation"]["tick"] = tick
        
    def define_station(self,station_id,station_name,station_type,cycle_time):
        station = {
            "id": station_id,
            "name": station_name,
            "type": station_type,
            "cycle_time": cycle_time
        }
        self.station_ids.append(station_id)
        self.data["stations"].append(station)
        
    def define_items(self,item_id,item_name,produced_by):
        item = {
            "id": item_id,
            "name": item_name,
            "produced_by": produced_by
        }
        self.items.append(item_id)
        self.data["items"].append(item)
    
    def define_connections(self,connection_id,from_station,to_station,item_id,buffer_capacity):
        connection = {
            "id": connection_id,
            "from_station": from_station,
            "to_station": to_station,
            "item_id": item_id,
            "buffer_capacity": buffer_capacity
        }
        self.data["connections"].append(connection)
        
    def define_recipes(self,station_id,inputs=None,input_qtys=None,outputs=None,output_qtys=None):
        if inputs is None:
            inputs = []
        if input_qtys is None:
            input_qtys = []
        if outputs is None:
            outputs = []
        if output_qtys is None:
            output_qtys = []

        if len(inputs) != len(input_qtys):
            raise ValueError("inputs and input_qtys length mismatch")

        if len(outputs) != len(output_qtys):
            raise ValueError("outputs and output_qtys length mismatch")
        recipe = {
            "station_id": station_id,
            "inputs" : {item: qty for item, qty in zip(inputs, input_qtys)},
            "outputs" : {item: qty for item, qty in zip(outputs, output_qtys)}
        }
        self.data["recipes"].append(recipe)
        
    def define_sink_item(self,item_id):
        if item_id not in [item['id'] for item in self.data['items']]:
            raise ValueError(f"Item ID {item_id} not defined in items")
        else:
            self.data["sink_item_id"] = item_id

    def save_to_json(self, filename, folder="examples"):

        folder_path = Path(folder)
        folder_path.mkdir(parents=True, exist_ok=True)

        save_path = folder_path / filename

        with open(save_path, "w") as f:
            json.dump(self.data, f, indent=4)
            
        print(f"Saved to {filename}")
    
    def reset(self):
        self.data = {
            "simulation": {},
            "stations": [],
            "items": [],
            "connections": [],
            "recipes": [],
            "sink_item_id": None
        }
        self.station_ids = []
        self.items = []
