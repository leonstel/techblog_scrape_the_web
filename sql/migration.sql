CREATE TABLE tournament (
    id UUID PRIMARY KEY,
    location VARCHAR(255),
    address VARCHAR(255),
    phone VARCHAR(255),
    email VARCHAR(255),
    website VARCHAR(255),
    fax VARCHAR(255)
);

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(255),
    lastname VARCHAR(255)
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    tournament_id UUID,
    winner INTEGER ,
    FOREIGN KEY (tournament_id) REFERENCES tournament(id),
    FOREIGN KEY (winner) REFERENCES players(id)
);

CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    amount INTEGER,
    player_id INTEGER ,
    game_id INTEGER,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (game_id) REFERENCES games(id)
);