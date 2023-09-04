import csv
import datetime
import os
import argparse
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select



STEAM_BASE_URL = "store.steampowered.com"


def find_all_games(steam_db_url):
    driver = webdriver.Chrome()
    driver.get(steam_db_url)
    
    profile_data = {}
    # wait for table to load
    try:
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "table-apps"))
            )
    except:
        raise Exception("Table not found")
    
    # Get profile name
    profile_name = driver.find_element(By.CLASS_NAME, 'player-name').text
    date_string = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"{profile_name}_game_list_{date_string}.csv"
    profile_data["name"] = profile_name
    profile_data["output_file"] = file_name
    
    # switch table to show all entries
    dropdown = Select(driver.find_element(By.NAME,'table-apps_length'))
    dropdown.select_by_value('-1')
    table = driver.find_element(By.ID, 'table-apps')
    soup = bs(table.get_attribute('innerHTML'), 'html.parser')

    # close browser to free up memory
    driver.close()

    # get all games from table
    table_rows = soup.find_all('tr',{'class':'app'})
    games_list = []
    for row in table_rows:
        game = row.find('td',{'class':'text-left'})
        cols = row.find_all('td')
        game_name = game.find('a').text
        game_url = game.find('a')['href']
        game_url = STEAM_BASE_URL + game_url
        game_price = cols[4].text
        game_playtime_m = cols[5]['data-sort']
        game_rating = cols[6].text.strip().replace('%', '')
        game = {
            'name': game_name,
            'url': game_url,
            'price': game_price,
            'playtime_m': game_playtime_m,
            'rating': game_rating
        }
        games_list.append(game)
    profile_data["games"] = games_list
    return profile_data

def save_csv_file(profile_data):
    
    file_name = profile_data["output_file"]
    games_list = profile_data["games"]
    # create csv file and write data to it
    is_file_created = False
    csv_file = None
    while not is_file_created:
        try:
            csv_file = open(file_name, 'x', newline='')
            is_file_created = True
        except PermissionError:
            print("Please close the file")
            input("Press Enter to continue...")
        except FileExistsError:
            print("File already exists")
            overwrite = input("Want to overwrite? (Y/n):\t").lower()
            if overwrite == 'n':
                is_file_created = False
                exit()
            elif overwrite == 'y':
                os.remove(file_name)
        finally:
            if csv_file:
                csv_file.close()
                
    with open(file_name, 'w', encoding="utf-8") as csv_file:
        fieldnames = ['name', 'url', 'price', 'playtime_m', 'rating']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for game in games_list:
            writer.writerow(game)
    print(f"File {file_name} created successfully")

    
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Steam Games parser",description='Scrape SteamDB for game list',)
    parser.add_argument('steam_db_url', help='URL for your SteamDB profile',).required = False
    
    args = parser.parse_args()
    if args.steam_db_url:
        steam_db_url = args.steam_db_url
    else:
        steam_db_url = input("Enter SteamDB URL: ")
        
    if not steam_db_url:
        print("URL not provided")
        exit()
    game_list_steamdb = find_all_games(steam_db_url)
    save_csv_file(game_list_steamdb)
