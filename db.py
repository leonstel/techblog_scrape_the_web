import psycopg2
from configparser import ConfigParser
import psycopg2.extras

psycopg2.extras.register_uuid()

# read database.ini config file with al the initials
def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


""" Connect to the PostgreSQL database server """
def connect():
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        conn.close()


""" Db class wrapper for executing queries """
class Db:
    client = None

    @staticmethod
    def setup():
        connection = connect()
        return Db(connection)

    def __init__(self, client):
        self.client = client

    def __del__(self):
        self.client.close()

    def run(self, query, *params):

        try:
            cur = self.client.cursor()
            cur.execute(query, params)
            self.client.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        except:
            print('Something else went wrong')

    def insert(self, query, *params):

        lastInsertId = None

        try:
            cur = self.client.cursor()
            cur.execute(query, params)
            lastInsertId = cur.fetchone()[0]
            self.client.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        except:
            print('Something else went wrong')

        return lastInsertId

    def select(self, query, *params):
        rows = None

        try:
            cur = self.client.cursor()
            cur.execute(query, params)

            rows = cur.fetchall()
            print("The number of parts: ", cur.rowcount)
            for row in rows:
                print(row)

            self.client.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        except:
            print('Something else went wrong')

        return rows

# drops the databases table by running the droptable.sql
def droptables():
    """ create tables in the PostgreSQL database"""
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        # for command in commands:

        cur.execute(open("./sql/droptables.sql", "r").read())

        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# resting the db means, first dropping al table then creating them again
def resetDB():
    droptables()

    """ create tables in the PostgreSQL database"""
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        # for command in commands:


        cur.execute(open("./sql/migration.sql", "r").read())

        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

# returns a new DB instance
def getDb():
    return Db.setup()


""" 
    Database manipulation methods below, like inserting and creating entities 
    Those will be used by the page extraction methods for inserting the scraped data to the database
"""

def insertTournament(tournament):
    db = getDb()

    t_id = tournament.get('id')
    location = tournament.get('location')
    address = tournament.get('address')
    phone = tournament.get('phone')
    email = tournament.get('email')
    website = tournament.get('website')
    fax = tournament.get('fax')

    query = """
                INSERT INTO tournament(id, location, address, phone, email, website, fax)
                VALUES(%s, %s, %s, %s, %s, %s, %s);
            """

    db.run(query, t_id, location, address, phone, email, website, fax)

def insertPlayer(player):
    db = getDb()

    firstname = player.get('firstname')
    lastname = player.get('lastname')

    query = """
                    INSERT INTO players(firstname, lastname)
                    VALUES(%s, %s)
                    RETURNING id;
                """

    player_id = db.insert(query, firstname, lastname)

    return player_id

def findPlayerByName(name):
    db = getDb()

    query = """
                SELECT id, fullname
                FROM
                (
                  select id, concat_ws(' ', firstname, lastname) AS fullname
                  FROM players
                ) AS t
                where fullname = %s
            """

    rows = db.select(query, name)

    if len(rows) > 0:
        return rows[0][0]
    else:
        print('Player with name not found')
        return None

def insertGame(tournament_id, player_id):
    db = getDb()

    query = """
                INSERT INTO games(tournament_id, winner)
                VALUES(%s, %s)
                RETURNING id;
            """

    game_id = db.insert(query, tournament_id, player_id)
    return game_id

def insertScore(game_id, player_id, amount):
    db = getDb()

    query = """
                INSERT INTO scores(game_id, player_id, amount)
                VALUES(%s, %s, %s)
                RETURNING id;
            """

    score_id = db.insert(query, game_id, player_id, amount)
    return score_id
