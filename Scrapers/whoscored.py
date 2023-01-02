# importing the necessary libraries
from selenium import webdriver
import json
import pandas as pd
from pandas.io.json import json_normalize

chrome_driver_path = r'C:\Users\shivank\selenium\chromedriver.exe'

def scrape_pass_data(pass_match_id):
    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    driver.get(
        'https://1xbet.whoscored.com/Teams/32/Fixtures/England-Manchester-United')
    whoscored_match_id = str(pass_match_id['match_id'][0])
    print(type(whoscored_match_id))
    print(whoscored_match_id)
    try:
        fixture = driver.find_element_by_xpath(
            f'/html/body/div[4]/div[3]/div[1]/div[4]/div[2]/div/div/div/div[{whoscored_match_id}]/div[9]/a')
        fixture.click()
        print(fixture)
    except:
        driver.close()
        return None
    try:
        element = driver.find_element_by_xpath(
            '//*[@id="layout-wrapper"]/script[1]')
    except:
        try:
            match_centre = driver.find_element_by_xpath(
                '//*[@id="sub-navigation"]/ul/li[4]/a')
            match_centre.click()
            element = driver.find_element_by_xpath(
                '//*[@id="layout-wrapper"]/script[1]')
        except:
            driver.close()
            return None
    script_content = element.get_attribute('innerHTML')
    script_ls = script_content.split(sep="  ")
    script_ls = list(filter(None, script_ls))
    script_ls = [name for name in script_ls if name.strip()]
    try:
        dictstring = script_ls[2][17:-2]
    except:
        driver.close()
        return None
    content = json.loads(dictstring)
    match = json_normalize(content['events'], sep='_')
    url = driver.current_url
    match_id = int(url.split('/')[4])
    match['match_id'] = match_id
    hometeam = content['home']['name']
    awayteam = content['away']['name']
    homeid = content['home']['teamId']
    awayid = content['home']['teamId']
    players = pd.DataFrame()
    homepl = json_normalize(content['home']['players'], sep='_')[
        ['name', 'position', 'shirtNo', 'playerId']]
    awaypl = json_normalize(content['away']['players'], sep='_')[
        ['name', 'position', 'shirtNo', 'playerId']]
    players = players.append(homepl)
    players = players.append(awaypl)
    match = match.merge(players, how='left')
    pass_match_id['match_id'] = pass_match_id['match_id'] + 1
    pass_match_id.to_csv('whoscored_pass_match_id.csv', index=False)
    driver.close()
    return match
