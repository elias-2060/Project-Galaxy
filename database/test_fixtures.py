import pytest
from database.database_access import Base, engine


@pytest.fixture(name="clear-db")
def uses_db():
    # clear all tables by dropping and recreating them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
