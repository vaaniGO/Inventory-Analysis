import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Reading the data
data = pd.read_csv('filtered_sku_data.csv')
# Adjusting the data a little bit
data = data.rename(columns= {'Unnamed: 0' : 'Period'})
data = data.rename(columns= {'ATTA BRANDED 5% KG' : 'Forecast'})
# Create the 'Order' column
data_calc = data.copy()
data_calc['Period'] += 1

for i in data_calc['Period'].unique():
    data_calc['Order {}'.format(i)]=0

# Variables contianing set-up and holding costs
set_up = 500
holding = 1

order = 1

# first order
for index, row in data_calc.iterrows():
    current_month = data_calc.loc[index, 'Period']
    cost = 0
    cost += set_up
    if (current_month > 1):
        for t in range (1, current_month+1):
            cost += (t-1) * data_calc.loc[t-1, 'Forecast'] * holding
    data_calc.loc[index, 'Order {}'.format(order)] = cost

# other orders
for order in range(1, 10):
    for index, row in data_calc.iterrows():
        current_month = data_calc.loc[index, 'Period']
        if current_month >= order:
            cost = 0

            values = list(data_calc.loc[order-1, ['Order {}'.format(i) for i in range(1, order+1)]].values)
            best = min([i for i in values if i>0])

            cost += best + set_up
            for t in range(order, current_month+1):
                cost += (t-order)*data_calc.loc[t-1, 'Forecast']*holding
            data_calc.loc[index, 'Order {}'.format(order)] = cost

data_calc = data_calc.set_index('Period').drop(['Forecast'], axis=1).T
data_calc.head()

costs, initials, nexts, quantities = [], [], [], []
i = 9

while i>1:
    # Order with the minimum cost
    initial_step = i
    next_step = data_calc[data_calc[i]>0][i].idxmin()
    cost = data_calc[data_calc[i]>0][i].min()
    # Next Step 
    next_id = int(next_step.replace('Order ',''))
    i = next_id - 1
    # Quantity
    quantity = data[data['Period'].isin(range(next_id, initial_step+1))]['Forecast'].sum()
    
    costs.append(cost)
    initials.append(initial_step)
    nexts.append(next_id)
    quantities.append(quantity)
    
df_results = pd.DataFrame({'backward':range(1, len(initials)+1), 
                           'initial':initials, 
                           'nexts':nexts, 
                           'cost':costs,
                           'quantity':quantities}).set_index('backward')
print("Total Cost: {:,}$".format(df_results.cost.sum()))
df_results


# Holding unit cost per month
hold_cost = 1
# Set Up Cost
setup_cost = 500

# Final Results
results_final = data.copy()
results_final['Period'] += 1;

# Production
month_prod = df_results['nexts'].values
prod_dict = dict(zip(month_prod, df_results.quantity.values))

# Values
results_final['production'] = results_final['Period'].apply(lambda t: prod_dict[t] if t in month_prod else 0)

# Inventory On Hand
results_final['IOH'] = results_final['production'].cumsum() - results_final['Forecast'].cumsum()

# Holding Cost
results_final['Holding Cost'] = (results_final['IOH'] * hold_cost)

# Set Up Cost
results_final['Set-Up Costs'] = results_final['production'].apply(lambda t: setup_cost if t > 0 else 0)

# Total Cost
results_final['Total Cost'] = results_final[['Holding Cost', 'Set-Up Costs']].sum(axis = 1)

results_final
