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

# add new columns fighter_1_odds , fighter_2_odds and updated_at and add a default value for each
data['updated_at'] = pd.Timestamp.now()
data['fighter_1_odds'] = -100
data['fighter_2_odds'] = +100

# Define formatters to apply to the columns when printing
formatters = {
    'fighter_1_odds': '{:+g}'.format,
    'fighter_2_odds': '{:+g}'.format,
    'updated_at': '{:%b-%d-%Y %I:%M:%p}'.format
}

data.sort_index(axis=1, inplace=True)  # Sort columns alphabetically

print(data.head(total_bouts).to_string(index=False, formatters=formatters))

print(data.info())
#print(data.describe())

# Save the updated DataFrame to a CSV file named 'odds.csv'
output_csv_path = os.path.join(script_dir, "odds.csv")
data.to_csv(output_csv_path, index=False)

# Print the path where the CSV file is saved
print(f"Updated odds saved to {output_csv_path}")
