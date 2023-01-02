# importing the necessary libraries
import tweepy
import requests
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
from understatscraper import Understat
from mplsoccer import Pitch, VerticalPitch
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from highlight_text import HighlightText, ax_text, fig_text
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import random
from collections import Counter
chrome_driver_path = r'C:\Users\shivank\selenium\chromedriver.exe'
pass_match_id = pd.read_csv('./data/whoscored_pass_match_id.csv')

print(pass_match_id)

print(3)