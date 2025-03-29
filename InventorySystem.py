import numpy as np

def generate_demand():
    return np.random.choice([1, 2, 3, 4], p=[1/6, 1/3, 1/3, 1/6])

def place_order(current_time, inventory_level, s, S, params, pending_orders):
    if inventory_level > s:
        return inventory_level, pending_orders, 0
    
    order_quantity = S - inventory_level
    cost = params['K'] + params['i'] * order_quantity
    lead_time = np.random.uniform(params['min_lead'], params['max_lead'])
    pending_orders.append((current_time + lead_time, order_quantity))
    pending_orders.sort()
    
    return inventory_level, pending_orders, cost

def update_metrics(time_delta, inventory_level, total_holding, total_shortage):
    if inventory_level > 0:
        total_holding += inventory_level * time_delta
    else:
        total_shortage += -inventory_level * time_delta
    return total_holding, total_shortage

def simulate_policy(s, S, params):
    current_time = 0.0
    inventory_level = params['initial_inventory']
    pending_orders = []
    total_ordering_cost, total_holding, total_shortage = 0, 0, 0
    
    for month in range(params['simulation_months']):
        inventory_level, pending_orders, ordering_cost = place_order(
            current_time, inventory_level, s, S, params, pending_orders
        )
        total_ordering_cost += ordering_cost
        
        while True:
            time_to_next_demand = np.random.exponential(params['mean_demand_time'])
            next_event_time = current_time + time_to_next_demand
            if next_event_time >= (month + 1):
                break
            
            while pending_orders and pending_orders[0][0] <= next_event_time:
                arrival_time, quantity = pending_orders.pop(0)
                total_holding, total_shortage = update_metrics(
                    arrival_time - current_time, inventory_level, total_holding, total_shortage
                )
                current_time = arrival_time
                inventory_level += quantity
            
            total_holding, total_shortage = update_metrics(
                next_event_time - current_time, inventory_level, total_holding, total_shortage
            )
            current_time = next_event_time
            inventory_level -= generate_demand()
    
    avg_ordering_cost = total_ordering_cost / params['simulation_months']
    avg_holding_cost = params['h'] * total_holding / params['simulation_months']
    avg_shortage_cost = params['pi'] * total_shortage / params['simulation_months']
    total_cost = avg_ordering_cost + avg_holding_cost + avg_shortage_cost
    
    return s, S, avg_ordering_cost, avg_holding_cost, avg_shortage_cost, total_cost

def showTable(estimate, params):
    results = [simulate_policy(s, S, params) for s, S in estimate]
    results.sort(key=lambda x: x[-1])
    
    print("\nPolicy/Estimate Comparison Results:")
    print("-" * 80)
    print(f"{'Estimate':15} {'Ordering Cost':>15} {'Holding Cost':>15} {'Shortage Cost':>15} {'Total Cost':>15}")
    print("-" * 80)
    for result in results:
        print(f"s={result[0]} & S={result[1]:<6} {result[2]:15.2f} {result[3]:15.2f} {result[4]:15.2f} {result[5]:15.2f}")

if __name__ == "__main__":
    params = {
        'K': 32.0, 'i': 3.0, 'h': 1.0, 'pi': 5.0,
        'mean_demand_time': 0.1, 'min_lead': 0.5, 'max_lead': 1.0,
        'initial_inventory': 60.0, 'simulation_months': 120
    }
    estimate = [(10, 60), (30, 60), (50, 60), (30, 60), (40, 60), (60, 90), (80, 100), (80, 130), (90, 120)]
    showTable(estimate, params)
