import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

browser = webdriver.Chrome()

matches_df = pd.DataFrame()
player_id_cache = {}

def goToUrl(url, *params):
    url = url.format(*params)
    browser.get(url)
    return BeautifulSoup(browser.page_source, 'html.parser')
