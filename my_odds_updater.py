import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime
import sys
import logging
import re

# Configure the root logger to output to both a file and the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%a %I:%M:%p',  # Thu 08:30:AM format
    handlers=[
        logging.FileHandler("new_odds_updater.log", encoding='utf-8'),  # Log to a file named new_odds_updater.log
        logging.StreamHandler()          # Log to the console
    ]
)

def fighters_to_be_tracked(csv_path):
    try:
        data = pd.read_csv(csv_path, dtype={'fighter_1_odds': str, 'fighter_2_odds': str})  # Convert odds columns to str
        fighter_1 = data['fighter_1'].tolist()  # Convert fighter_1 names to a list
        fighter_2 = data['fighter_2'].tolist()  # Convert fighter_2 names to a list
        fighter_1_odds = data['fighter_1_odds'].tolist()  # Convert fighter_1 odds to a list
        fighter_2_odds = data['fighter_2_odds'].tolist()  # Convert fighter_2 odds to a list
        
        # Create a dictionary with both fighters and their odds
        fighters_to_be_tracked_dict = {}
        for i in range(len(fighter_1)):
            # Add fighter_1 to the dictionary
            fighters_to_be_tracked_dict[fighter_1[i]] = fighter_1_odds[i]
            # Add fighter_2 to the dictionary
            fighters_to_be_tracked_dict[fighter_2[i]] = fighter_2_odds[i]
        
        return fighters_to_be_tracked_dict  # Return the dictionary
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return {}
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file is empty or malformed")
        return {}

def scrape_dk():
    # URL of the DraftKings UFC odds page
    url = "https://sportsbook.draftkings.com/leagues/mma/ufc"

    max_retries = 5

    retry_delay = 60  # delay in seconds before retrying

    for attempt in range(max_retries):

        try:

            # Fetch the HTML content from the URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                # Store response content
                html_content = response.content

                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find the "root" id in the HTML content
                root_id = soup.find(id="root")

                # Make list of all the fighter names found in the HTML content within the "root" id
                all_fighters_list = [fighter.text.strip() for fighter in root_id.find_all("div", class_="event-cell__name-text")]

                # Make a list of all the fighter moneyline odds
                all_fighters_odds_list = [fighter_odds.text.strip() for fighter_odds in root_id.find_all("span", class_="sportsbook-odds american no-margin default-color")]

                # Creating a dictionary
                current_fighter_odds_dict = {k: v for k, v in zip(all_fighters_list, all_fighters_odds_list)}

                return current_fighter_odds_dict # Return the dictionary
            else:
                current_time = datetime.now().strftime('%b-%d-%Y %I:%M:%p')
                print(f"{current_time} - Failed to retrieve data: {response.status_code}")
                return None # Return None if data retrieval fails
            
        except requests.RequestException as e:
                current_time = datetime.now().strftime('%b-%d-%Y %I:%M:%p')
                print(f"{current_time} - Request failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

def update_csv_with_new_odds(csv_path, updated_fighters_dict, changed_fighters=None):
    # Read the existing CSV file
    data = pd.read_csv(csv_path)
    # Update the odds columns with new odds from the dictionary
    data['fighter_1_odds'] = data['fighter_1'].map(updated_fighters_dict)
    data['fighter_2_odds'] = data['fighter_2'].map(updated_fighters_dict)

    # Only update timestamp for rows where fighters had odds changes
    if changed_fighters:
        for index, row in data.iterrows():
            if row['fighter_1'] in changed_fighters or row['fighter_2'] in changed_fighters:
                data.at[index, 'updated_at'] = datetime.now().strftime('%b-%d-%Y %I:%M:%p')
    else:
        data['updated_timestamp'] = datetime.now().strftime('%b-%d-%Y %I:%M:%p')

    # Save the updated DataFrame back to the CSV file
    data.to_csv(csv_path, index=False)

def normalize_odds(odds_str):
    try:
        # Handle None or empty strings
        if not odds_str or odds_str in ['', 'nan', 'NaN']:
            return 0
        
        # Convert to string if it's not already
        odds_str = str(odds_str)
        
        # Replace non-standard minus signs with standard ASCII minus sign
        normalized_str = odds_str.replace('−', '-').replace('–', '-').replace('—', '-')
        
        # Remove any extra whitespace
        normalized_str = normalized_str.strip()
        
        # Remove any non-numeric characters except minus sign and plus sign
        normalized_str = re.sub(r'[^\d\-\+]', '', normalized_str)
        
        # Convert to integer
        return int(normalized_str)
    
    except (ValueError, TypeError) as e:
        logging.error(f"Error normalizing odds '{odds_str}': {e}")
        return 0  # Return 0 as default for invalid odds

def odds_comparison_fix(current_odds, tracked_odds):
    # If current and tracked are both positive
    if current_odds > 0 and tracked_odds > 0:
        return current_odds - tracked_odds
    # If current and tracked are both negative
    elif current_odds < 0 and tracked_odds < 0:
        return current_odds - tracked_odds
    # If current is negative and tracked is positive
    elif current_odds < 0 and tracked_odds > 0:
        return (current_odds + 100) - (tracked_odds - 100)
    # If current is positive and tracked is negative
    else:
        return (current_odds - 100) - (tracked_odds + 100)
    

def main():
    # Construct the full path to the CSV file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "odds.csv")
        
    while True:
        current_time = datetime.now().strftime('%b-%d-%Y %I:%M:%p')
        print(f"{current_time} - odds updater running")
        # Get the fighters to be tracked from the CSV file
        fighters_to_be_tracked_dict = fighters_to_be_tracked(csv_path)
        # Scrape the current fighter odds from DraftKings
        current_fighter_odds_dict = scrape_dk()
        changed_fighters = set()  # Track which specific fighters had odds changes

        if fighters_to_be_tracked_dict and current_fighter_odds_dict:
            for fighter in fighters_to_be_tracked_dict:
                # Get the tracked odds and normalize them
                tracked_odds = normalize_odds(fighters_to_be_tracked_dict[fighter])
                # Get the current odds for the fighter (default to tracked odds if not found)
                current_odds_str = current_fighter_odds_dict.get(fighter, str(tracked_odds))
                # Normalize the current odds
                current_odds = normalize_odds(current_odds_str)
                
                # Check if the odds have changed by at least 10 points
                if abs(odds_comparison_fix(current_odds, tracked_odds)) >= 10:
                    current_time = datetime.now().strftime('%b-%d-%Y %I:%M:%p')
                    logging.info(f"Odds change for {fighter}: {fighters_to_be_tracked_dict[fighter]} -> {current_fighter_odds_dict[fighter]}")
                    
                    # Update the dictionary with the new odds
                    fighters_to_be_tracked_dict[fighter] = current_odds_str
                    changed_fighters.add(fighter)  # Add fighter to changed set

            # Update local csv file with new odds
            update_csv_with_new_odds(csv_path, fighters_to_be_tracked_dict, changed_fighters)
            sys.exit("Data processing complete. Exiting program.")
        else:
            current_time = datetime.now().strftime('%b-%d-%Y %I:%M:%p')
            print(f"{current_time} - No fighters to be tracked found or data retrieval failed. Retrying in 60 seconds...")

            time.sleep(60)  # Wait for 60 seconds before scraping again

if __name__ == "__main__":
    main()
