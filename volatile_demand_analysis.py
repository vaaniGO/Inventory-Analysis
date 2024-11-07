import pandas as pd
import matplotlib.pyplot as plt

sales_data_22_23 = pd.read_csv('SalesRegister (1).xlsx -22-23.csv')
sales_data_23_24 = pd.read_csv('SalesRegister 23-24.XLS - Sheet1.csv')

demand_data_22_23 = pd.DataFrame({
    'Date': sales_data_22_23['Bill Date'],
    'Name': sales_data_22_23['Product Name'],
    'Demand': sales_data_22_23['Product Qty Qty-1']
})
# demand_data_22_23 = demand_data_22_23.drop(index=3).reset_index(drop=True)
# Drop rows where 'Column2' or 'Column3' have NaN values
demand_data_22_23 = demand_data_22_23.dropna(subset=['Name', 'Demand'])

# Forward-fill NaN values in 'Column1' with the previous valid value
demand_data_22_23['Date'] = demand_data_22_23['Date'].ffill()

demand_data_22_23 = demand_data_22_23.reset_index(drop=True)

# Step 1: Convert 'Date' to datetime format with the correct format
demand_data_22_23['Date'] = pd.to_datetime(demand_data_22_23['Date'], format='%d/%m/%Y')

# Step 2: Convert 'Demand' to numeric, forcing errors to NaN (if any)
demand_data_22_23['Demand'] = pd.to_numeric(demand_data_22_23['Demand'], errors='coerce')

# Step 3: Extract the month from the 'Date' column
demand_data_22_23['Month'] = demand_data_22_23['Date'].dt.month

# Step 4: Group by 'Month' and 'Name' to calculate the average demand for each product in each month
monthly_demand_22_23 = demand_data_22_23.groupby(['Month', 'Name'], as_index=False)['Demand'].mean()

# Step 5: Rename columns to match the desired format
monthly_demand_22_23 = monthly_demand_22_23.rename(columns={'Demand': 'Average_Demand'})

# Display the resulting DataFrame
monthly_demand_22_23.head()

demand_data_23_24 = pd.DataFrame({
    'Date': sales_data_23_24['SHRI BHAGWATI TRADERS'],
    'Name': sales_data_23_24['Unnamed: 6'],
    'Demand': sales_data_23_24['Unnamed: 7']
})
demand_data_23_24 = demand_data_23_24.drop(index=3).reset_index(drop=True)
# Drop rows where 'Column2' or 'Column3' have NaN values
demand_data_23_24 = demand_data_23_24.dropna(subset=['Name', 'Demand'])

# Forward-fill NaN values in 'Column1' with the previous valid value
demand_data_23_24['Date'] = demand_data_23_24['Date'].ffill()

demand_data_23_24 = demand_data_23_24.reset_index(drop=True)

# Step 1: Convert 'Date' to datetime format with the correct format
demand_data_23_24['Date'] = pd.to_datetime(demand_data_23_24['Date'], format='%d/%m/%Y')

# Step 2: Convert 'Demand' to numeric, forcing errors to NaN (if any)
demand_data_23_24['Demand'] = pd.to_numeric(demand_data_23_24['Demand'], errors='coerce')

# Step 3: Extract the month from the 'Date' column
demand_data_23_24['Month'] = demand_data_23_24['Date'].dt.month

# Step 4: Group by 'Month' and 'Name' to calculate the average demand for each product in each month
monthly_demand_23_24 = demand_data_23_24.groupby(['Month', 'Name'], as_index=False)['Demand'].mean()

# Step 5: Rename columns to match the desired format
monthly_demand_23_24 = monthly_demand_23_24.rename(columns={'Demand': 'Average_Demand'})

# Display the resulting DataFrame
monthly_demand_23_24.head()


monthly_demand = pd.merge(monthly_demand_22_23, monthly_demand_23_24, on=['Month', 'Name'], how='inner')

monthly_demand['Average_Demand_x'] = (monthly_demand['Average_Demand_x'] + monthly_demand['Average_Demand_y'])/2

monthly_demand = monthly_demand.drop(columns=['Average_Demand_y'])

monthly_demand.head()

monthly_demand = pd.read_csv('Monthly_Avg_Demand_perSKU.csv')

import seaborn as sns

# Plot monthly demand for each SKU
sns.set(style="whitegrid")
# Step 1: Loop through each unique SKU in 'monthly_demand'
for sku in monthly_demand['Name'].unique():
    # Filter data for the current SKU
    sku_data = monthly_demand[monthly_demand['Name'] == sku]
    
    # Step 2: Create a bar plot
    plt.figure(figsize=(8, 6))
    sns.barplot(x='Month', y='Average_Demand_x', data=sku_data, palette='viridis')
    
    # Customize the plot
    plt.title(f'Monthly Demand for {sku}', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Average Demand', fontsize=12)
    plt.xticks(ticks=range(9), labels=['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
    plt.tight_layout()
    
    # Show the plot
    plt.show()

# Find the SKUs with most volatile demand (top 20)
# Step 1: Filter out products that are sold every month from April through December
valid_skus = monthly_demand.groupby('Name').filter(lambda x: x['Month'].nunique() == 9)

# Step 2: Calculate the demand volatility (standard deviation) for each SKU
volatility = valid_skus.groupby('Name')['Average_Demand_x'].std().reset_index()
volatility.columns = ['Name', 'Demand_Volatility']

# Step 3: Sort by volatility and get the top 20 most volatile products
top_20_volatile = volatility.sort_values(by='Demand_Volatility', ascending=False).head(20)

# Print the top 20 most volatile products
print("Top 20 most volatile products:")
print(top_20_volatile)

# Step 4: Plot demand for each SKU (optional visualization for top 20 most volatile products)
sns.set(style="whitegrid")
for sku in top_20_volatile['Name']:
    # Filter data for the current SKU
    sku_data = monthly_demand[monthly_demand['Name'] == sku]
    
    # Create a bar plot
    plt.figure(figsize=(8, 6))
    sns.barplot(x='Month', y='Average_Demand_x', data=sku_data, palette='viridis')
    
    # Customize the plot
    plt.title(f'Monthly Demand for {sku}', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Average Demand', fontsize=12)
    plt.xticks(ticks=range(9), labels=['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
    plt.tight_layout()
    
    # Show the plot
    plt.show()


