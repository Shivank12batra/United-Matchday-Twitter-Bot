# importing the necessary libraries
from selenium import webdriver
from understatscraper import Understat
import pandas as pd

chrome_driver_path = r'C:\Users\shivank\selenium\chromedriver.exe'
shots_match_id = pd.read_csv('./data/understat_shots_match_id.csv')


def scrape_shots_data(shots_match_id):
    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    driver.get('https://understat.com/team/Manchester_United/2022')
    understat_match_id = str(shots_match_id['match_id'][0])
    try:
        fixture = driver.find_element_by_xpath(
            f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div[{understat_match_id}]/div[2]/div/a')
        fixture.click()
    except:
        driver.close()
        return None
    url = driver.current_url
    match_id = int(url.split('/')[4])
    understat = Understat()
    match = understat.single_match(match_id)
    # changing to float data type for numerical columns
    match['X'] = match['X'].astype(float)
    match['Y'] = match['Y'].astype(float)
    match['xG'] = match['xG'].astype(float)
    match['minute'] = match['minute'].astype(float)
    match.reset_index(inplace=True, drop=True)
    shots_match_id['match_id'] = shots_match_id['match_id'] + 1
    shots_match_id.to_csv('understat_shots_match_id.csv', index=False)
    driver.close()
    return match
