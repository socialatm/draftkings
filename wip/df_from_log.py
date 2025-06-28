# attempt at plotting odds changes for a fighter
import pandas as pd
import re
from datetime import datetime

def replace_unicode_minus(text):
    """Replace Unicode minus sign (U+2212) with ASCII hyphen-minus (U+002D)"""
    return text.replace('−', '-')

def extract_odds_to_dataframe(log_file_path):
    """Extract odds changes from log file to pandas DataFrame"""
    
    data = []
    
    with open(log_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if 'Odds change' in line:
                # Handle different log formats in the file
                if ' - INFO - ' in line:
                    # Format: 2025-06-23 14:45:36,726 - INFO - Jun-23-2025 02:45:PM - Odds change detected for...
                    parts = line.split(' - INFO - ')
                    if len(parts) >= 2:
                        timestamp_part = parts[0]
                        message_part = ' - INFO - '.join(parts[1:])
                        
                        # Extract fighter name and odds
                        if 'Odds change detected for' in message_part:
                            match = re.search(r'Odds change detected for (.+?): (.+?) -> (.+?)$', message_part)
                        else:
                            match = re.search(r'Odds change for (.+?): (.+?) -> (.+?)$', message_part)
                        
                        if match:
                            fighter_name = match.group(1)
                            old_odds = match.group(2)
                            new_odds = match.group(3)
                            
                            # Parse timestamp
                            try:
                                dt = datetime.strptime(timestamp_part, '%Y-%m-%d %H:%M:%S,%f')
                            except:
                                # Handle cases where timestamp might be different
                                dt = None
                            
                            data.append({
                                'timestamp': dt,
                                'fighter_name': fighter_name,
                                'old_odds': old_odds,
                                'new_odds': new_odds,
                                'raw_line': line
                            })
                else:
                    # Format: Jun-24-2025 07:10:AM - INFO - Odds change for...
                    match = re.search(r'(.+?) - INFO - Odds change (?:detected )?for (.+?): (.+?) -> (.+?)$', line)
                    if match:
                        timestamp_str = match.group(1)
                        fighter_name = match.group(2)
                        old_odds = match.group(3)
                        new_odds = match.group(4)
                        
                        # Parse timestamp
                        try:
                            dt = datetime.strptime(timestamp_str, '%b-%d-%Y %I:%M:%p')
                        except:
                            dt = None
                        
                        data.append({
                            'timestamp': dt,
                            'fighter_name': fighter_name,
                            'old_odds': old_odds,
                            'new_odds': new_odds,
                            'raw_line': line
                        })
    
    df = pd.DataFrame(data)
    return df

# Usage
df = extract_odds_to_dataframe('new_odds_updater.log')
print(df.head())
print(f"\nDataFrame shape: {df.shape}")
print(f"\nUnique fighters: {df['fighter_name'].nunique()}")