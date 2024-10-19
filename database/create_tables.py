import backend.game_classes
from database.database_access import engine, Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

