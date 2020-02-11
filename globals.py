import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

""" File contains global variables """

browser = webdriver.Chrome()
matches_df = pd.DataFrame()
player_id_cache = {}

# method for visiting new pages with selenium and then extract the new page's content with Beautiful Soup
# return the newly visited extracted beautiful soup result
def goToUrl(url, *params):
    url = url.format(*params)
    browser.get(url)
    return BeautifulSoup(browser.page_source, 'html.parser')
