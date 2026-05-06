import simpy

from simulator.buffer import Buffer
from simulator.station import Station
from simulator.config import get_recipe_map

class SimulationEngine:
    def __init__(self,config:dict):
        self.env = simpy.Environment()
        self.config = config
        self.tick = config['simulation'].get('tick',1)
        self.duration = config['simulation']['duration']
        self.sink_item_id = config["sink_item_id"]
        
        self.recipe_map = get_recipe_map(config)
        self.buffers = {}
        self.stations = {}
        
        self._build_buffers()
        self._build_stations()
        
    def _build_buffers(self):
        for conn in self.config['connections']:
            buffer_id = f"buffer_{conn['id']}"
            self.buffers[conn['id']] = Buffer(buffer_id=buffer_id,
                                              item_id=conn['item_id'],
                                              capacity=conn['buffer_capacity']
                                              )
            
    def _build_stations(self):
        for stat in self.config['stations']:
            station_id = stat['id']
            recipe = self.recipe_map[station_id]
            
            input_buffers = {}
            output_buffers = {}
            
            for conn in self.config['connections']:
                if conn['to_station']==station_id:
                    input_buffers[conn['item_id']] = self.buffers[conn['id']]
                
                if conn['from_station']==station_id:
                    output_buffers[conn['item_id']] = self.buffers[conn['id']]
                    
            station = Station(env = self.env,
                              station_config=stat,
                              recipe=recipe,
                              input_buffers=input_buffers,
                              output_buffers=output_buffers,
                              sink_item_id=self.sink_item_id)
            
            
            self.stations[station_id] = station
            
    def run(self):
        for station in self.stations.values():
            self.env.process(station.run(self.duration,self.tick))
        
        self.env.run(until=self.duration)