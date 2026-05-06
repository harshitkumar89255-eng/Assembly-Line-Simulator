class Buffer:
    def __init__(self,buffer_id: str,item_id:str,capacity:int):
        self.buffer_id = buffer_id
        self.item_id = item_id
        self.capacity = capacity
        self.level = 0
        self.history = []
        
    def can_put(self,qty:int):
        return self.level+qty <= self.capacity
    
    def can_take(self,qty:int):
        return self.level >= qty
    
    def put(self,qty:int,now:float):
        if not self.can_put(qty):
            raise ValueError(f"Buffer {self.buffer_id} Overflow")
        self.level+=qty
        self.record(now)
    
    def take(self,qty:int,now:float):
        if not self.can_take(qty):
            raise ValueError(f"Buffer {self.buffer_id} Underflow")
        self.level-=qty
        self.record(now)
        
    def record(self, now:float):
        self.history.append((now,self.level))