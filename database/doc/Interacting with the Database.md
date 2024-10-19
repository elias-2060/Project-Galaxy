# How to add items to the database

## Adding items through the ORM:
You can add items using the structure SQLAlchemy gives us.

For example, a user can have multiple planets, then you can add a planet like this:

```python
from backend.game_classes.General import load_user
from backend.game_classes import User, Planet
from database.database_access import DefaultSession

# Make a temporary session (SQLAlchemy session, not a Flask session)
with DefaultSession() as BaseSession:
    # Load a user with the requested from the database (User-class format return)
    user: User = load_user(user_name="user_name", session=BaseSession)
    
    # Make / Load the planet you want to add to the user
    planet_to_be_added: Planet = Planet(...)
    
    # Add it to the list of planets automatically made by SQLAlchemy ORM
    user.planets.append(planet_to_be_added)
```

Remember to use `session=` when using the `load_user()` method. This ensures that everything happens in 
the same session.

## Removing items through the ORM:

You can do the same as with adding items, but then with deleting:

```python
from backend.game_classes.General import load_user
from backend.game_classes import User, Planet
from database.database_access import DefaultSession

# Make a temporary session (SQLAlchemy session, not a Flask session)
with DefaultSession() as BaseSession:
    # Load a user with the requested from the database (User-class format return)
    user: User = load_user(user_name="user_name", session=BaseSession)

    # Make / Load the planet you want to remove from the user
    planet_to_be_removed: Planet = Planet(...)

    # Remove it from the list of planets automatically made by SQLAlchemy ORM
    user.planets.remove(planet_to_be_removed)
```

## Adding items by hand
If you want to add items by hand, you do the following:

You import ```session``` and the class which belongs to the table you want to add an item to, for example ```Users``` from database_access.py

Now you make the item you want to add, for example, a ```Users``` item.
```python
user = Users(user_name="user_name", password="password")
```
And now you add it to the database.

```python
session.add(user)
```

And remember to commit.
```python
session.commit()
```

If you don't see an error, it should be added to the database now.
## Making tables

In the **database_access.py** file you can add the table you want, for example here is our table for usernames:

```python
from database.database_access import Base
from sqlalchemy import Column, Integer, Sequence, String

class Users(Base):
    """
    Class that is used to store users in the database and retrieve them
    """
    __tablename__ = "users"

    user_id = Column("user_id", Integer, Sequence("id_sequence", start=1), primary_key=True)
    user_name = Column("user_name", String, unique=True, nullable=False)
    password = Column("password", String, nullable=False)

    def __init__(self, user_name, user_password, user_id=None):
        self.user_id = user_id
        self.user_name = user_name
        self.password = user_password

    def __repr__(self):
        return f"{self.user_id}, {self.user_name}, {self.password}"
```

You add a class for the table you want to make with the following conditions:

- It has to be derived from the ```Base``` class
- ```__tablename__``` is the name of the table in the database
- You can add the columns with the ```Column()``` function and can add all the conditions you want like **primary key** or **not nullable** here.
- Make sure you include them in the ```__init__``` of you class.
- Your class should come **before** the ```Base.metadata.create_all(bind=engine)``` statement in the file.

After this the table should be made after running the program once.

## Executing queries
First you have to include ```session``` from database_access.py. Then you simply just execute:

If you want the whole table:
```python
query = session.query(Table) 
```
If you want an extra filter:
```python
query = session.query(Table).filter_by(user_id="user_name")
```
And then just iterate over the query, and you will have items of the class:
```python
for Table_class_item in query:
    # Here you do what you want with the class items
    print(Table_class_item.attribute1)
```

## Executing raw queries
You have to include ```engine``` from database_access.py. Then it just goes as follows:
```python
engine.execute("<sql here>")
```


