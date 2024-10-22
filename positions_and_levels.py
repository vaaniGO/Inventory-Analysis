import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd

class Warehouse: 
    def __init__ (self, inventory_level):
        self.i = inventory_level
        self.o = 0 # o is for outstanding orders. What are these? Orders placed by customers but not yet fulfilled by the inventory manager
    
    def receive_order(self, Q, time):
        self.review_inventory(time)
        self.i, self.o = self.i + Q, self.o - Q # if we recieve order then it adds to our inventory, and reduces the number of outstanding units we have to deliver
        self.review_inventory(time)
    
    def order(self, Q, time):
        self.review_inventory(time)
        self.o += Q # if we order then it adds to our outstanding unit orders
        self.review_inventory(time)

    def on_hand_inventory(self):
        return max(0, self.i)

    def issue(self, demand, time):
        self.review_inventory(time)
        self.i = self.i - demand
        self.review_inventory(time+1)
    
    def inventory_position(self):
        return self.o + self.i 
    
    def review_inventory(self, time):
        try:
            self.levels.append([time, self.i])
            self.on_hand.append([time, self.on_hand_inventory()])
            self.positions.append([time, self.inventory_position()])
        except AttributeError:
            self.levels, self.on_hand = [[0, self.i]], [[0, self.on_hand_inventory()]]
            self.positions = [[0, self.inventory_position()]]

from queue import PriorityQueue

class EventWrapper():
    def __init__(self, event):
        self.event = event
    
    def __lt__(self, other):
        return self.event.priority < other.event.priority

class DES():
    def __init__(self, end):
        self.events, self.end, self.time = PriorityQueue(), end, 0
        
    def start(self):
        while True:
            event = self.events.get()
            self.time = event[0]
            if self.time < self.end:
                event[1].event.end()
            else:
                break
                    
    def schedule(self, event: EventWrapper, time_lag: int):
        self.events.put((self.time+time_lag, event))
        
class CustomerDemand: 
    def __init__(self, des: DES, demand_rate: float, warehouse: Warehouse):
        self.d = demand_rate
        self.w = warehouse
        self.des = des
        self.priority = 1
    
    def end(self):
        self.w.issue(self.d, self.des.time)
        self.des.schedule(EventWrapper(self), 1)

class Order:
    def __init__(self, des: DES, Q: float, warehouse: Warehouse, lead_time: float):
        self.Q = Q
        self.w = warehouse
        self.des = des
        self.lead_time = lead_time
        self.priority = 0 # top priority
    
    def end(self):
        self.w.order(self.Q, self.des.time)
        self.des.schedule(EventWrapper(ReceiveOrder(self.des, self.Q, self.w)), self.lead_time)

class ReceiveOrder: 
    def __init__(self, des: DES, Q: float, warehouse: Warehouse):
        self.Q = Q
        self.w = warehouse
        self.des = des
        self.priority = 0 # top priority
    
    def end(self):
        self.w.receive_order(self.Q, self.des.time)

def plot_inventory(values, label):
    df = pd.DataFrame({'x': np.array(values)[:, 0], 
                       'fx': np.array(values)[:, 1]})
    plt.xticks(range(len(values)), range(1, len(values)+1))
    plt.xlabel("$t$")
    plt.ylabel("items")
    plt.plot('x', 'fx', data=df, linestyle='-', marker='o', label = label)



N, initial_inventory = 20, 50 
w = Warehouse(initial_inventory)
des  = DES(N)
d = CustomerDemand(des, 5, w)
des.schedule(EventWrapper(d), 0)
o = Order(des, 50, w, 1)
des.schedule(EventWrapper(o), 9)
des.start()

plot_inventory(w.positions,"inventory positions")
plot_inventory(w.levels, "inventory levels")
plt.legend()
plt.show()
