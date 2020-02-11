import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

""" File contains global variables """

browser = webdriver.Chrome()

# collects all the extacted matches which will be used for processing at the end of the scraping process
matches_df = pd.DataFrame()

# Right after the instertion of the player into the database its database id will be saved into the dictionary
# so that later code could retrieve the database player ids in a fast and easy manner.
# Without these the database must be selecting players constantly, NOT GOOD
player_id_cache = {}

# method for visiting new pages with selenium and then extract the new page's content with Beautiful Soup
# return the newly visited extracted beautiful soup result
def goToUrl(url, *params):
    url = url.format(*params)
    browser.get(url)
    return BeautifulSoup(browser.page_source, 'html.parser')
