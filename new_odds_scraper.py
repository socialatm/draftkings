import pandas as pd
import os

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV file
csv_path = os.path.join(script_dir, "next_event", "next_event", "next_event.csv")

data = pd.read_csv(csv_path)
total_bouts = data['bout_number'].max() # total number of bouts for this event
print(data.head(total_bouts).to_string(index=False))

#print(data.info())
#print(data.describe())
