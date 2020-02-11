from bs4 import BeautifulSoup
import time
import re
import db
import globals
import extraction
import selenium

# removes the allow cookies popup
def allowCookies():
    cookieButton = globals.browser.find_element_by_xpath("//*[text()='Akkoord']")
    cookieButton.click()

# scrapes a tournament and its players and matches from its detail url
def scrapeTournament(tournamentUrl):
    print('visit tournament with id '+tournamentUrl+' detail page')

    result = re.search(r"id=((\w+-?)+)", tournamentUrl)
    tournament_id = result.group(1)

    soup = globals.goToUrl('https://www.toernooi.nl{}', tournament_urls[index])
    extraction.extractTournamentInfo(soup, tournament_id)

    print('visit the players of this tournament')

    url = 'https://www.toernooi.nl/sport/players.aspx?id={}'
    soup = globals.goToUrl(url, tournament_id)

    extraction.extractPlayers(soup)

    extraction.processMatches(tournament_id)

print('reset DB')

db.resetDB()

# before searching select the badminton sporttype (2). After that it redirects to the return url
url = 'https://www.toernooi.nl/sportselection/setsportselection/2?returnUrl=/find?StartDate={}&EndDate={}&CountryCode=NED'
startDate = '2019-12-10'
endDate = '2019-12-31'
globals.goToUrl(url, startDate, endDate)

print('Visit tournament url')

allowCookies()

print('Allow cookies on site')


# 2 second sleep. Otherwise the expected page could be not fully loaded yet
time.sleep(2)

soup = BeautifulSoup(globals.browser.page_source, 'html.parser')
tournament_urls = extraction.extracyTournamentUrls(soup)

# loops through the extracted tournament urls from search overview
for index in range(len(tournament_urls)):
    scrapeTournament(tournament_urls[index])