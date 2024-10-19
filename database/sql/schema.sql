CREATE TABLE Users(
	user_id SERIAL PRIMARY KEY,
	user_name TEXT UNIQUE NOT NULL,
	password TEXT check (
	    length(password) > 8
	    AND password ~ '[A-Z]'
        AND password ~ '[a-z]'
        AND password ~ '[0-9]'
	    )
);

INSERT INTO Users(user_name, password) VALUES('spongebob_square_pants', 'KrustyKr3bbyP3tty');
INSERT INTO Users(user_name, password) VALUES('patrick_starfish', 'Spong3bob');
INSERT INTO Users(user_name, password) VALUES('squidward_tentacles', 'ClarinetMa3stro');
INSERT INTO Users(user_name, password) VALUES('sandy_cheeks', 'TexasRang3r');
INSERT INTO Users(user_name, password) VALUES('mr_krabs', 'M0neyL0v3r');
