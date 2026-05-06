class Station:
    def __init__(self,env,station_config:dict,recipe:dict,input_buffers:dict,output_buffers:dict, sink_item_id):
        self.env = env
        self.id = station_config['id']
        self.name = station_config['name']
        self.type = station_config['type']
        self.cycle_time = station_config['cycle_time']
        self.sink_item = sink_item_id
        self.inputs = recipe['inputs']
        self.outputs = recipe['outputs']
        self.finished_output_count = 0
        
        self.input_buffers = input_buffers
        self.output_buffers = output_buffers
        
        self.state = "IDLE"
        self.completed_cycles = 0
        self.busy_time = 0
        self.starved_time = 0
        self.blocked_time = 0
        
    def inputs_available(self):
        for item_id,qty in self.inputs.items():
            if item_id not in self.input_buffers:
                return False
            if not self.input_buffers[item_id].can_take(qty):
                return False
        return True
    

    def outputs_available(self):
        for item_id,qty in self.outputs.items():
            if item_id in self.output_buffers:
                if not self.output_buffers[item_id].can_put(qty):
                    return False
            elif item_id == self.sink_item:
                continue
            else:
                return False
        return True 
    
            
    def consume_input(self):
        for item_id,qty in self.inputs.items():
            self.input_buffers[item_id].take(qty,self.env.now)
        
    def produce_output(self):
        for item_id, qty in self.outputs.items():
            if item_id == self.sink_item:   
                self.finished_output_count += qty

                if item_id in self.output_buffers:
                    self.output_buffers[item_id].put(qty, self.env.now)

            elif item_id in self.output_buffers:
                self.output_buffers[item_id].put(qty, self.env.now)

            else:
                raise ValueError(f"Station {self.id} produced {item_id} but no buffer exists")            
    
    
    def run(self,duration:float,tick:float=1):
        while self.env.now < duration:
            if not self.inputs_available():
                self.state = "STARVED"
                self.starved_time += tick
                yield self.env.timeout(tick)
                continue
            
            if not self.outputs_available():
                self.state = "BLOCKED"
                self.blocked_time += tick
                yield self.env.timeout(tick)
                continue
            
            self.consume_input()
            self.state = 'PROCESSING'
            yield self.env.timeout(self.cycle_time)
            self.busy_time += self.cycle_time
            
            self.produce_output()
            self.completed_cycles += 1
        
        self.state = "DONE"