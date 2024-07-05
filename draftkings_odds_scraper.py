import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from send_message import send_email


def scrape_dk():
    # URL of the DraftKings UFC odds page
    url = "https://sportsbook.draftkings.com/leagues/mma/ufc"

    # Fetch the HTML content from the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Store response content
        html_content = response.content

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the "root" id in the HTML content
        root_id = soup.find(id="root")

        # Make list of all the fighter names found in the HTML content within the "root" id
        all_fighters_list = [fighter.text.strip() for fighter in root_id.find_all("div", class_="event-cell__name-text")]
        
        # Make a list of the first fighters in the bout using the list of all fighters
        fighter_1 = [all_fighters_list[i] for i in range(0, len(all_fighters_list), 2)]

        # Make a list of the second fighters (opponents) in the bout using the list of all fighters
        fighter_2 = [all_fighters_list[i + 1] for i in range(0, len(all_fighters_list), 2)]

        # Make a list of all the fighter moneyline odds
        all_fighters_odds_list = [fighter_odds.text.strip() for fighter_odds in root_id.find_all("span", class_="sportsbook-odds american no-margin default-color")]

        # Make a list of the odds for the first fighters
        fighter_1_odds = [all_fighters_odds_list[i] for i in range(0, len(all_fighters_list), 2)]

        # Make a list of the odds for the second fighters (opponents)
        fighter_2_odds = [all_fighters_odds_list[i + 1] for i in range(0, len(all_fighters_list), 2)]

        # Get all the HTML elements with "a"
        all_a_tags = root_id.find_all("a")

        # Pull the bout id from the href found in the "a" element
        bout_ids = []
        for a_tag in all_a_tags:
            href = a_tag.get('href')
            if href and '/event/' in href:
                bout_id = href.split('/')[-1]
                bout_ids.append(int(bout_id))

        # Make a list of the bout ids 
        fighter_bout_id = [bout_ids[i] for i in range(0, len(all_fighters_list), 2)]

        # Sort the column data to make ready to return
        data = list(zip(fighter_1, fighter_1_odds, fighter_2, fighter_2_odds, fighter_bout_id))

        return data
    
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None
    
# Function to save data to a CSV file
def save_data_to_csv(df, filename):
    df.to_csv(filename, index=False)

# Function to load data from a CSV file
def load_data_from_csv(filename):
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['fighter_1', 'fighter_1_odds', 'fighter_2', 'fighter_2_odds', 'fighter_bout_id'])
    
def main():
    csv_filename = 'UFC_fight_odds.csv'
    previous_df = load_data_from_csv(csv_filename)
    
    while True:
        print('running')
        scraped_data = scrape_dk()

        if scraped_data:
            # Create new dataframe using data scraped from DK website
            current_df = pd.DataFrame(scraped_data, columns=['fighter_1', 'fighter_1_odds', 'fighter_2', 'fighter_2_odds', 'fighter_bout_id'])

            # Identify new fights by comparing fighter_bout_id against previous data
            new_fights = []
            for bout_id in current_df['fighter_bout_id'].tolist():
                if bout_id not in previous_df['fighter_bout_id'].tolist():
                    new_fights.append(bout_id)

            if new_fights:
                new_fights_df = current_df[current_df['fighter_bout_id'].isin(new_fights)]
                body = f"New fights detected:\n\n\n{new_fights_df[['fighter_1', 'fighter_1_odds', 'fighter_2', 'fighter_2_odds']].to_string(index=False, header=False)}"
                print(body)
                # Save current data to CSV file
                save_data_to_csv(current_df, csv_filename)
                send_email(csv_filename, body, "New UFC Fight Odds")

            # Update previous data
            previous_df = current_df.copy()

        time.sleep(60)  # Wait for 60 seconds before scraping again

if __name__ == "__main__":
    main()
