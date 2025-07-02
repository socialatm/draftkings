import pandas as pd
import os

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV file
csv_path = os.path.join(script_dir, "next_event", "next_event", "next_event.csv")

data = pd.read_csv(csv_path, usecols=['bout_number', 'fighter_1', 'fighter_2'])
total_bouts = data['bout_number'].max() # total number of bouts for this event

# sort by bout_number decending
data = data.sort_values(by='bout_number', ascending=False)

print(data.head(total_bouts).to_string(index=False))

#print(data.info())
#print(data.describe())
