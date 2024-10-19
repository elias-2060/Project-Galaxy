from typing import TYPE_CHECKING
from uuid import UUID, uuid1

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from backend.game_classes.Buildings import Building, Warper, Spaceport
from database.database_access import Base, auto_session, default_factory
from sqlalchemy.exc import IntegrityError

if TYPE_CHECKING:
    from backend.game_classes.Planet import Planet


class Settlement(Base):
    __tablename__ = "settlements"

    settlement_id: Mapped[UUID] = mapped_column(primary_key=True)
    "Id of the settlement"

    settlement_nr: Mapped[int]
    "Number of the settlement"

    planet_id: Mapped[UUID] = mapped_column(ForeignKey("planets.planet_id", ondelete="CASCADE"))
    "Id of the planet the settlement is on"

    __table_args__ = (UniqueConstraint("settlement_nr", "planet_id"),)

    buildings: Mapped[list[Building]] = relationship(back_populates="settlement")
    "List of the buildings on the settlement"

    planet: Mapped["Planet"] = relationship(back_populates="settlements")
    "Planet that the settlement is on"

    @default_factory(settlement_id=uuid1)
    def __init__(self, settlement_nr: int, planet_id: UUID, settlement_id: UUID = None) -> None:
        """
        Initialize a Settlement object with a settlement number and a planet.
        """
        assert isinstance(settlement_id, UUID), "settlement_id must be of type 'UUID'"

        self.settlement_nr: int = settlement_nr
        self.planet_id: UUID = planet_id
        self.settlement_id: UUID = settlement_id

        self.grid_height = 5
        self.grid_width = 5

    def get_grid(self, show: bool) -> list[list[Building | None]]:
        """
        Update the grid based on the current buildings
        """
        # Make an emtpy grid:
        grid: list[list[Building | None]] = []
        for row_nr in range(5):
            row: list[Building | None] = []
            for col_nr in range(5):
                row.append(None)
            grid.append(row)

        # For all buildings, add them to this grid on the correct x and y position
        building: Building
        buildings = self.buildings

        if buildings == [None]:
            return grid

        if show:
            for building in buildings:
                assert grid[building.grid_pos_y][building.grid_pos_x] is None, "Error: Overlapping buildings"
                if isinstance(building, Warper) and building.planet_link is not None:
                    grid[building.grid_pos_y][building.grid_pos_x] = "UsedWarper"
                elif isinstance(building, Spaceport) and building.space_ship is not None and building.space_ship.moving_time_left > 0:
                    grid[building.grid_pos_y][building.grid_pos_x] = "SpaceshipGone"
                else:
                    grid[building.grid_pos_y][building.grid_pos_x] = type(building).__name__

        else:
            for building in buildings:
                assert grid[building.grid_pos_y][building.grid_pos_x] is None, "Error: Overlapping buildings"
                grid[building.grid_pos_y][building.grid_pos_x] = building

        return grid

    @auto_session
    def store(self, session: Session = None) -> None:
        try:
            session.commit()
        except IntegrityError as DuplicateErr:
            print(type(DuplicateErr))  # the exception type
            print("Cannot Store Settlement. Settlement already exist. id :" + self.settlement_id.__str__() + " )")
        except Exception as err:
            print(type(err))  # the exception type

    @auto_session
    def get_building(self, pos_y: int, pos_x: int) -> Building:

        """
        Get the building located at the given position.
        """
        return self.get_grid(False)[pos_y][pos_x]

    @auto_session
    def update(self, seconds: float) -> None:
        """
        Update the settlement with the time that has passed since last update
        """
        for building in self.buildings:
            building.update(seconds=seconds)

    @auto_session
    def remove_building(self, building: Building, session: Session = None) -> None:
        """
        Removes a building from a settlement.
        """
        # First delete the 'Building' part
        item = session.query(Building).filter_by(building_id=building.building_id).first()
        session.delete(item)
        session.commit()

        """
        # Now remove the specialization part
        if isinstance(building, Farm):
            self.farms.remove(building)
        elif isinstance(building, Mine):
            self.mines.remove(building)
        elif isinstance(building, TownHall) :
            self.town_hall: None = None
        elif isinstance(building, Barrack):
            self.barracks.remove(building)
        else:
            raise NotImplementedError(f"Unknown building type: {type(building)}")
        """

    @auto_session
    def build(self, building: Building) -> bool:
        """
        Builds a building, returns whether it is possible to build it.
        """
        # Check if there are enough resources on the planet
        planet: "Planet" = self.planet
        materials: int = planet.building_materials

        if isinstance(building, Warper):
            build_cost = building.build_cost
        else:
            build_cost = building.build_cost  # TODO remove this

        if materials < build_cost:
            print("error: not enough resources")
            return False

        # Now that we know that it is possible, we can build it:
        self.buildings.append(building)

        # Now we extract the build cost from the planet

        if isinstance(building, Warper):
            planet.building_materials -= building.build_cost
            building.construction_time_left = 1000  # TODO Construction time warper
        else:
            planet.building_materials -= building.build_cost

            # And we append the wait time
            building.construction_time_left = building.build_cost

        building.level = 1

        building.store()

        return True
