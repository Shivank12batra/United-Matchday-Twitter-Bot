# importing the necessary libraries
import sys
import os
import tweepy
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


sys.path.insert(0, r'C:\Users\shivank\United Twitter Bot\scrapers')
sys.path.insert(0, r'C:\Users\shivank\United Twitter Bot\dataviz')
from understat import scrape_shots_data
from whoscored import scrape_pass_data
from xg_flowchart import xG_flowchart
from goal_probability_dashboard import goal_probability_dashboard

pass_match_id = pd.read_csv('./data/whoscored_pass_match_id.csv')
shots_match_id = pd.read_csv('./data/understat_shots_match_id.csv')

print(pass_match_id)
print(shots_match_id)

print(3)

def tweet_images(pass_match_id, shots_match_id):
    pass_data = scrape_pass_data(pass_match_id)
    if pass_data is None:
        print('hey')
        pass
#         return 
    shots_data = scrape_shots_data(shots_match_id)
    
    # if (pass_data is not None and shots_data is not None):
    if (shots_data is not None):
        h_team = shots_data['h_team'].unique()[0]
        a_team = shots_data['a_team'].unique()[0]
        h_goals = shots_data['h_goals'].unique()[0]
        a_goals = shots_data['a_goals'].unique()[0]

        # api keys for authentication and tweet access
        consumer_key = os.getenv('CONSUMER_KEY')
        consumer_secret = os.getenv('CONSUMER_SECRET')
        access_token = os.getenv('ACCESS_TOKEN')
        access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

        # authenticate to twitter
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # create API object
        api = tweepy.API(auth, wait_on_rate_limit=True)

        try:
            api.verify_credentials()
            print("Authentication OK")
        except:
            print("Error during authentication")
            return None

        try:
            # invoking the functions to create the latest visualizations from United's recent game
            xG_flowchart(shots_data)
            print('xg_chart')
            goal_probability_dashboard(shots_data)
            print('functions done')
            # match_summary_dashboard(pass_data, shots_data)
        except:
            print('data viz not functional!')
            return None
        try:
            media_1 = api.media_upload('images/xG_flowchart_twitter_bot.png')
            media_2 = api.media_upload('images/goal_probability_dashboard_twitter_bot.png')
            #media_3 = api.media_upload('match_summary_dashboard_twitter_bot.png')
            print('done_media')
            message_1 = f'{h_team} {h_goals}-{a_goals} {a_team}\n\nRunning xG Flowchart:\n\n\n'
            message_2 = f'{h_team} {h_goals}-{a_goals} {a_team}\n\nGoal Probability Dashboard:\n\n\n'
            #message_3 = f'{h_team} {h_goals}-{a_goals} {a_team}\n\nMatch Summary Dashboard:\n\n\n'
            print('done_message')

            api.update_status(message_1, media_ids=[media_1.media_id_string])
            api.update_status(message_2, media_ids=[media_2.media_id_string])
            #api.update_status(message_3, media_ids=[media_3.media_id_string])
            print('done_tweet')
        except:
            print('problem uploading media')
            return None
    else:
        print('both pass data and shots data are not available right now!')
        return None

tweet_images(pass_match_id, shots_match_id)