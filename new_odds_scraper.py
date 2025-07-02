import pandas as pd
import os

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV file
csv_path = os.path.join(script_dir, "next_event", "next_event", "next_event.csv")

data = pd.read_csv(csv_path)
print(data.head())
# Display the first few rows of the DataFrame
print(data.info())
print(data.describe())