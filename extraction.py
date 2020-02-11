from enum import Enum
import re
import globals

import db

# enum for the tournament's information on its detail page
class TournamentAttr(Enum):
    LOCATION = "locatie"
    ADDRESS = "adres"
    PHONE = "telefoon"
    EMAIL = "e-mail"
    WEBSITE = "website"
    FAX = "fax"

# extracts the tournament urls form the search result overview
def extracyTournamentUrls(soup):
    print('get tournament urls from page')

    searchResultUl = soup.find("ul", {"id": "searchResultArea"})
    tournament_list = searchResultUl.findAll("li", {"class": "list__item"})

    urls = []

    for t in tournament_list:
        tournament_a = t.find("a")
        if tournament_a:
            tournament_link = tournament_a.attrs.get('href')
            urls.append(tournament_link)

    return urls


# extracts the tournament information from its detail page
def extractTournamentInfo(soup, tournament_id):
    print('extract tournament info from page')

    table = soup.find("table", {"id": "cphPage_cphPage_cphPage_tblContactInformation"})
    tbody = soup.find("tbody")
    rows = tbody.findChildren("tr", recursive=False)

    entry = {}

    for row in rows:

        entry['id'] = tournament_id

        attribute = row.find('th').getText().replace(":", "").lower()
        data = row.find('td').getText()

        if TournamentAttr(attribute) == TournamentAttr.LOCATION:
            entry['location'] = data

        elif TournamentAttr(attribute) == TournamentAttr.ADDRESS:
            address_td = rows[1].find('td').find('td').contents
            data = [content for content in address_td if getattr(content, 'name', None) != 'br']
            entry['address'] = data

        elif TournamentAttr(attribute) == TournamentAttr.PHONE:
            entry['phone'] = data

        elif TournamentAttr(attribute) == TournamentAttr.FAX:
            entry['fax'] = data

        elif TournamentAttr(attribute) == TournamentAttr.EMAIL:
            entry['email'] = data

        elif TournamentAttr(attribute) == TournamentAttr.WEBSITE:
            entry['website'] = data

        else:
            print('Attribute not found!!!', attribute)

    print('save tournament info to db')

    db.insertTournament(entry)

# extract the matches from the tournament player's detail page
# the matches won't be saved to the database immediately but saved
# to a matches dataframe for later use
def extractMatches(soup):
    print('extract matches from page')

    table_matches = soup.find("table", {"class": "matches"})

    if table_matches:
        tbody = table_matches.find("tbody")
        rows = tbody.findAll("tr", recursive=False)

        for row in rows:

            entry = {}

            tds = row.findAll("td", recursive=False)

            game_scores = tds[6].getText()

            if game_scores:
                contestant1 = tds[3].getText().strip('\n').lstrip()
                contestant2 = tds[5].getText().strip('\n').lstrip()

                result = re.search(r"((\d+)-(\d+))", game_scores)

                if not result:
                    continue

                score1 = result[2]
                score2 = result[3]
                # rawScore = result[1]

                # for now only one game
                entry['contestant1'] = contestant1
                entry['contestant2'] = contestant2
                entry['score1'] = int(result[2])
                entry['score2'] = int(result[3])

                winner = None
                if entry['score1'] > entry['score2']:
                    winner = contestant1
                else:
                    winner = contestant2

                entry['winner'] = winner

                print('save extracted match '+ score1 + '-' + score2 + ': ' + contestant1 + '-' + contestant2 +' to global variable')

                # save the matches to a pandas dataframe so that they could be processed later on by the processMatches function
                globals.matches_df = globals.matches_df.append(entry, ignore_index=True)
    else:
        print('Not match table found!')

# extracts the players of the tournament in question
# the database id's of the inserted players will be cache in a dictionary (globals.player_id_cache)
# so that you have instant access to them without having the need for unnecessary repetitive select queries on the database
def extractPlayers(soup):
    print('extract players from page')

    table_players = soup.find("table", {"class": "players"})
    tbody = table_players.find("tbody")
    tds = tbody.findAll("td")

    for td in tds:
        link = td.find("a")
        if link:
            entry = {}

            player_url = link.attrs.get('href')
            player = link.getText()

            print('handler player ' + player)

            # check the blog's player' name regex section for additional info
            result = re.search(r"(\w+), (\w+)(.*)", player)

            if not result or (not result[2] or not result[1]):
                continue

            firstname = result[2].lstrip()
            lastname = result[1].lstrip()
            prefix = result[3].lstrip()
            lastname = prefix + ' ' + lastname if prefix else lastname

            entry['firstname'] = firstname
            entry['lastname'] = lastname

            print('save player to database')
            last_inserted_player_id = db.insertPlayer(entry)

            print('cache inserted player id')
            player_id_cache_key = entry['firstname'] + ' ' + entry['lastname']
            globals.player_id_cache[player_id_cache_key] = last_inserted_player_id

            if not last_inserted_player_id:
                raise Exception('Player not inserted into db correctly')

            print('visit matches page of the player')
            url = 'https://www.toernooi.nl{}'
            soup = globals.goToUrl(url, player_url)

            extractMatches(soup)


# The processing of matches happens when all other extracting has been done
# it takes and saves the matches to the database. It uses with that the cached player ids
# without the cached player ids it should do a ton of unnecessary select database queries. You should avoid that!
def processMatches(tournament_id):
    print('process the saved matches, save to db with cached player ids')

    for index, match_row in globals.matches_df.iterrows():

        contestant1 = match_row['contestant1']
        contestant2 = match_row['contestant2']

        # get the player ids from the player_id_cache and use them for saving the match to databse
        # the match needs the player ids from its relation with the players table
        if contestant1 in globals.player_id_cache and contestant2 in globals.player_id_cache:
            contestant1_id = globals.player_id_cache[match_row['contestant1']]
            contestant2_id = globals.player_id_cache[match_row['contestant2']]
            score1 = match_row['score1']
            score2 = match_row['score2']
            winner_id = globals.player_id_cache[match_row['winner']]

            #  save the game to the database
            game_id = db.insertGame(tournament_id, winner_id)

            if game_id:

                # after saving the game insert 2 score entries to the database
                # those will be linked to the game by its id and with a player by its cache player id
                print('save game '+ str(score1) + '-' + str(score2) + ': ' + contestant1 + '-' + contestant2 +' and scores to db, link game to tournament')
                db.insertScore(game_id, contestant1_id, score1)
                db.insertScore(game_id, contestant2_id, score2)
            else:
                print('Could not save game to DB!')