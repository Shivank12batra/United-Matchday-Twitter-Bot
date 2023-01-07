# importing the necessary libraries
from selenium import webdriver
import time
import bs4
from understatscraper import Understat
import json
import pandas as pd
from pandas.io.json import json_normalize

chrome_driver_path = r'C:\Users\shivank\selenium\chromedriver.exe'

def single_match(page, base_url='https://understat.com/match/{}'):
        """
        Function to scrape data for a single game
        Args:
        base_url (string): url of the understat.com website from where the data has to be scraped.
        page (int): match id of the game for which the user wants the shots data.
        """
        url = base_url.format(page)
        #res = requests.get(url)
        #if 'The page you requested was not found' in str(res.text):
        #    return('Please provide a valid match id from understat.com')
        #soup = bs4.BeautifulSoup(res.text, 'lxml')
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=options)
        driver.get(url)
        soup = bs4.BeautifulSoup(driver.page_source)
        scripts = soup.find_all('script')
        strings = str(scripts[3])
        ind_start = strings.index("('")+2
        ind_end = strings.index("')")
        json_data = strings[ind_start:ind_end]
        json_data = json_data.encode('utf8').decode('unicode escape')
        data = json.loads(json_data)
        home_df = json_normalize(data['h'],sep='_')
        away_df = json_normalize(data['a'],sep='_')
        combined = pd.concat([home_df, away_df])
        driver.close()
        return combined

def scrape_shots_data(shots_match_id):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=options)
    driver.get('https://understat.com/team/Manchester_United/2022')
    understat_match_id = str(shots_match_id['match_id'][0])
    print(understat_match_id)
    # time.sleep(12)
    fixture = driver.find_element('xpath', f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div[{understat_match_id}]/div[2]/div/a')
    fixture.click()
    # try:
    #     # fixture = driver.find_by_css_selector(f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div[{understat_match_id}]/div[2]/div/a')
    #     fixture = driver.find_by_css_selector('.match-info')
    #     print(fixture)
    #     fixture.click()
    # except:
    #     driver.close()
    #     return None
    url = driver.current_url
    match_id = int(url.split('/')[4])
    print(match_id)
    # understat = Understat()
    # match = understat.single_match(match_id)
    match = single_match(match_id)
    print(match)
    # changing to float data type for numerical columns
    match['X'] = match['X'].astype(float)
    match['Y'] = match['Y'].astype(float)
    match['xG'] = match['xG'].astype(float)
    match['minute'] = match['minute'].astype(float)
    match.reset_index(inplace=True, drop=True)
    shots_match_id['match_id'] = shots_match_id['match_id'] + 1
    print(shots_match_id['match_id'])
    print('added')
    shots_match_id.to_csv('data/understat_shots_match_id.csv', index=False)
    driver.close()
    return match
