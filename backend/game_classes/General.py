import csv
from uuid import UUID, uuid1

from flask import Response, jsonify
from sqlalchemy.orm import Query, Session

from backend.game_classes.Race import Race
from backend.game_classes.User import User
from database.database_access import auto_session


def get_users_json() -> Response:
    """
    Makes a json file with all the userdata.
    """
    # We take all the users in list format and call the function
    users: list = get_users()[1:]
    return jsonify(users)


def get_races_json() -> Response:
    """
    Makes a json file with all the userdata.
    """
    # We take all the users in list format and call
    races: list = get_races()[1:]
    return jsonify(races)


@auto_session
def check_user(user_name: str, user_password: str, session: Session = None) -> bool:
    """
    Checks if the user has a correct login
    """
    # panic on calls manually specifying an invalid type as session
    assert isinstance(session, Session), "session must be of type 'Session'"

    query: Query = session.query(User).filter_by(user_name=user_name, password=user_password)
    assert query.count() <= 1, "Multiple versions of same user in database"
    if query.count() > 0:
        return True
    return False


@auto_session
def load_race(race_name: str, session: Session = None) -> Race:
    """
    Loads a race from the database
    """
    # panic on calls manually specifying an invalid type as session
    assert isinstance(session, Session), "session must be of type 'Session'"

    query: Query = session.query(Race).filter_by(race_name=race_name)
    assert query.count() <= 1, "Multiple versions of same race in the database"
    race_db: Race = query.first()

    return race_db


@auto_session
def get_users(session: Session = None) -> list[User]:
    """
    Returns a list of lists with each list being the user_id, user_name, and password of the user.
    """
    # panic on calls manually specifying an invalid type as session
    assert isinstance(session, Session), "session must be of type 'Session'"

    result: list = []
    # Make a query that takes all the users out of the database
    query = session.query(User)

    # We add the column-names to the result
    result.append(["user_id", "user_name", "user_password"])

    # Now for each user we add a list of its attributes to the result
    user: User
    for user in query:
        result.append([user.user_id, user.user_name, user.password])
    return result


@auto_session
def get_races(session: Session = None) -> list[Race]:
    """
    Returns a list of lists with each list being the user_id, user_name, and password of the user.
    """
    # panic on calls manually specifying an invalid type as session
    assert isinstance(session, Session), "session must be of type 'Session'"

    result: list = []
    # Make a query that takes all the races out of the database
    query = session.query(Race)

    # Now for each race we add a list of its attributes to the result
    race: Race
    for race in query:
        result.append([race.race_name])
    return result


def store_data() -> None:
    """
    Stores all the data in the local database in a .csv file with name output.csv
    """
    results: list = get_users()
    # open a file in the downloads folder
    with open("database/output.csv", "w", newline="") as f:
        # Create a CSV writer
        writer = csv.writer(f)

        # Write the results
        writer.writerows(results)


@auto_session
def add_user(user_name: str, user_password: str, user_id: UUID = uuid1(), session: Session = None) -> User | str:
    """
    Adds a user to the database
    """
    # panic on calls manually specifying an invalid type as session
    assert isinstance(session, Session), "session must be of type 'Session'"

    # Check if the username is available
    in_data: int = session.query(User).filter_by(user_name=user_name).count()
    if in_data > 0:
        return "Username already exists"

    # Password check that gives the error message of what is wrong in the password
    pw_check: str = check_password(user_password)
    if pw_check != "correct":
        return pw_check

    # Add the user to the database
    try:
        user = User(user_name, user_password)
        session.add(user)
    # If an error occurred give an error message and rollback the changes
    except:
        session.rollback()
        return "An error occurred while adding the user to the database"

    # Commit the changes if they were made
    session.commit()
    return "Successfully added user"


def check_password(user_password: str) -> str:
    """
    Checks if the password is correct for a user
    """
    capital_in_password: bool = any(char.isupper() for char in user_password)
    if not capital_in_password:
        return "Password needs capital letter"
    number_in_password: bool = any(char.isdigit() for char in user_password)
    if not number_in_password:
        return "Password needs number"
    len_greater_than_5: bool = bool(len(user_password) > 5)
    if not len_greater_than_5:
        return "Password needs more than 5 characters"
    return "correct"
