import { useEffect, useState } from "react";
import BuildingInfo from "./BuildingInfo";
import farmImage from "../assets/farm.png"; // Import the farm image
import mineImage from "../assets/mine.png"; // Import the mine image
import barrackImage from "../assets/barrack.png"; // Import the barrack image
import developmentImage from "../assets/development.png"; // Import the development image
import DevelopmentTimer from "../components/DevelopmentInfo";
import townhallImage from "../assets/townhall.png"; // Import the townhall image
import spaceshipImage from "../assets/spaceship.png"; // Import the spaceship image
import spaceshipGoneImage from "../assets/spaceshipGone3.png"; // Import the spaceship image
import warpImage from "../assets/warper.png"
import usedWarpImage from "../assets/warper_used.png"

// Importing CSS styles for BuildingGrid components
import "../styles/BuildingGrid.css";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

// defining the interface for the GridCell, GridRow, and BuildingGrid
interface GridCellProps {
  buildMode: boolean;
  toggleBuildMode: () => void;
  structureType: number;
  setStructureType: (structureName: number) => void;
  structureLevel: number;
  setStructureLevel: (structureName: number) => void;
  onUpgrade: () => void; // Function to handle upgrade
  onDelete: () => void; // Function to handle delete
  posXY: { row: number; col: number };
  gridData: string[][] | null;
  settlementNumber: number;
  planetNumber: number;
  toggleMenu: (posXY: { row: number; col: number }) => void;
  isOpen: boolean;
  rerender: () => void;
  selectTile: (posXY: { row: number; col: number }) => void;
  isSelected: boolean;
}
interface GridRowProps {
  buildMode: boolean;
  toggleBuildMode: () => void;
  structureType: number;
  setStructureType: (structureName: number) => void;
  structureLevel: number;
  setStructureLevel: (structureName: number) => void;
  onUpgrade: () => void; // Function to handle upgrade
  onDelete: () => void; // Function to handle delete
  pos: number;
  gridData: string[][] | null;
  settlementNumber: number;
  planetNumber: number;
  rerender: () => void;
}

interface GridBuildProps {
  buildMode: boolean;
  toggleBuildMode: () => void;
  structureType: number;
  setStructureType: (structureName: number) => void;
  structureLevel: number;
  setStructureLevel: (structureName: number) => void;
  onUpgrade: () => void; // Function to handle upgrade
  onDelete: () => void; // Function to handle delete
  settlementNumber: number;
  planetNumber: number;
  rerender: () => void;
}

const GridCell: React.FC<GridCellProps> = ({
  buildMode,
  toggleBuildMode,
  structureType,
  posXY,
  gridData,
  settlementNumber,
  planetNumber,
  toggleMenu,
  isOpen,
  rerender,
  isSelected,
  selectTile
}) => {
  // use state indicating whether the cell is empty or not
  const [isEmpty, setIsEmpty] = useState(true);

  // use state indicating the type of structure in the cell
  const [currentStruct, setStruct] = useState("");

  // use state indicating the level of structure in the cell
  const [currentLevel, setLevel] = useState<number>(0);

  // Variable to store the start time for development
  const [startTime, setStartTime] = useState<number | null>(null);
  const [totalTime, setTotalTime] = useState<number | null>(null);


  // function to handle upgrade
  const handleUpgrade = () => {
    setLevel(currentLevel + 1)
  };

  const updateStructureType = ()  => {
    if (currentStruct === "Spaceport") {
      setStruct("SpaceshipGone");
    }
    // For the warpers
    if (currentStruct === "Warper"){
      setStruct("UsedWarper")
    } else if (currentStruct === "UsedWarper"){
      setStruct("Warper")
    }
  }

  const handleDelete = () => {
    setIsEmpty(true); // Set the cell to empty
    setStruct(""); // Clear the structureType
    toggleMenu(posXY); // Toggle menu visibility
    selectTile(posXY); // Unselect the tile
  };

  const update = async (e: React.FormEvent) => {
    if (isEmpty && buildMode) {
      setIsEmpty(false);
      toggleBuildMode();
      let originalType = structureType.toString();
      setStruct("inDevelopment");
      setLevel(1);
      var startTime = Date.now(); // Capture the start time
      setStartTime(startTime); // Store the start time
      let totalTime = 10000; // Total time for development in milliseconds
      setTotalTime(totalTime); // Store the total time


      setTimeout(() => {
        if (originalType == "6"){
          setStruct("Warper");
        }
        else if (originalType === "5") {
          setStruct("Spaceport");
        }
        else if (originalType === "4") {
          setStruct("Farm");
        } else if (originalType === "3") {
          setStruct("Mine");
        } else if (originalType === "2") {
          setStruct("Barrack");
        }
      }, totalTime);

      // e.preventDefault();
      const response = await axios.post(
        `${API_URL}/settlement/building`,
        {
          building: structureType.toString(),
          pos_x: posXY.row,
          pos_y: posXY.col,
          settlement_number: settlementNumber,
          planet_number: planetNumber,
        },
        { withCredentials: true }
      );
      rerender();
    }
    else if (!isEmpty) {
      toggleMenu(posXY); // Toggle menu visibility
      selectTile(posXY);
    }
  };

  useEffect(() => {
    if (gridData) {
      setStruct(gridData[posXY.col][posXY.row]);
      setIsEmpty(gridData[posXY.col][posXY.row] === null);
    }
  }, [gridData]);

  // Render building image if current structure is a building
  const renderStructure = () => {
    if (currentStruct === "Farm") {
      return <img src={farmImage} alt="Farm" />;
    } else if (currentStruct === "Mine") {
      return <img src={mineImage} alt="Mine" />;
    } else if (currentStruct === "Barrack") {
      return <img src={barrackImage} alt="Barrack" />;
    }else if (currentStruct === "TownHall") {
      return <img src={townhallImage} alt="TownHall" />;
    }else if (currentStruct === "Spaceport") {
      return <img src={spaceshipImage} alt="Spaceport" />;
    }else if (currentStruct === "SpaceshipGone") {
      return <img src={spaceshipGoneImage} alt="SpaceshipGone" />;
    }else if (currentStruct == "Warper"){
      return <img src={warpImage} alt="Warper"/>
    } else if (currentStruct == "UsedWarper"){
      return <img src={usedWarpImage} alt="UsedWarper"/>
    }
    // Render development image if current structure is in development
    else if (currentStruct === "inDevelopment") {
      return <img src={developmentImage} alt="Development" />;
    }

    return currentStruct;
  };

  // Returning JSX for the grid cell
  return (
    <>
      <li className="gridcell">
        <button
          className={`${isEmpty ? "cellbutton" : "cellbutton active"} ${isSelected ? "selected" : ""}`}
          onClick={update}
        >
          {renderStructure()}
        </button>
      </li>
      {isOpen && currentStruct != "inDevelopment" && currentStruct != "SpaceshipGone" && (
        <BuildingInfo
          structureLevel={currentLevel}
          structureType={currentStruct}
          cellPosition={{ top: 0, left: 0 }}
          onUpgrade={handleUpgrade} // Pass handleUpgrade function
          onDelete={handleDelete} // Pass onDelete functiont
          cellPosXY={posXY}
          planetNumber={planetNumber}
          settlementNumber={settlementNumber}
          rerender={rerender}
          upgradeCost={200}
          updateStructureType={updateStructureType}
        />
      )}
      {(currentStruct === "inDevelopment") && isOpen && (
        <DevelopmentTimer startTime={startTime || 0} totalTime={totalTime || 0} type="inDevelopment" />
      )}
      {(currentStruct === "SpaceshipGone") && isOpen && (
        <DevelopmentTimer startTime={startTime || 0} totalTime={totalTime || 0} type="SpaceshipGone" />
      )}
    </>
  );
};

// defining GridRow component which makes up one row of the grid
const GridRow: React.FC<GridRowProps> = ({
  buildMode,
  toggleBuildMode,
  structureType,
  setStructureType,
  structureLevel,
  setStructureLevel,
  onUpgrade,
  onDelete,
  pos,
  gridData,
  settlementNumber,
  planetNumber,
  rerender,
}) => {
  // Returning JSX for the grid row
  return (
    <ul className="gridrow">
      {[1, 2, 3, 4, 5].map((_, index) => (
        <GridCell
          gridData={gridData}
          posXY={{ row: pos, col: index }}
          key={index}
          onDelete={onDelete}
          onUpgrade={onUpgrade}
          buildMode={buildMode}
          toggleBuildMode={toggleBuildMode}
          structureType={structureType}
          setStructureType={setStructureType}
          settlementNumber={settlementNumber}
          planetNumber={planetNumber}
          structureLevel={structureLevel}
          setStructureLevel={setStructureLevel}
          isOpen={false}
          toggleMenu={() => {}}
          rerender={rerender}
          isSelected={false}
          selectTile={() => {}}
        />
      ))}
    </ul>
  );
};

// defining BuildingGrid component
const BuildingGrid: React.FC<GridBuildProps> = ({
  buildMode,
  toggleBuildMode,
  structureType,
  setStructureType,
  structureLevel,
  setStructureLevel,
  onUpgrade,
  onDelete,
  settlementNumber,
  planetNumber,
  rerender,
}) => {
  const [gridData, setGridData] = useState<string[][] | null>(null);
  const [openMenuPosition, setOpenMenuPosition] = useState<{ row: number; col: number } | null>(null);
  const [selectedTile, setSelectedTile] = useState<{ row: number; col: number } | null>(null);
  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/settlement`, {
        params: {
          planet_number: planetNumber,
          settlement_number: settlementNumber,
          include_grid: true,
        },
        withCredentials: true,
      });
      setGridData(response.data);
    })();
  }, []);

  // Function to handle opening/closing menu
  const toggleMenu = (posXY: { row: number; col: number }) => {
    if (openMenuPosition && openMenuPosition.row === posXY.row && openMenuPosition.col === posXY.col) {
      // If the clicked cell's menu is already open, close it
      setOpenMenuPosition(null);
    } else {
      // If another cell's menu is open, close it first and then open the clicked cell's menu
      setOpenMenuPosition(posXY);
    }
  };

  const selectTile = (posXY: { row: number; col: number }) => {
    if (selectedTile && selectedTile.row === posXY.row && selectedTile.col === posXY.col) {
        // If the clicked cell is already selected, close it
        setSelectedTile(null);
      } else {
        // If another cell is selected, close it first and then select the selected cell
        setSelectedTile(posXY);
    }
  };

  // Returning JSX for the building grid
  return (
    <div className="buildgrid">
      {[1, 2, 3, 4, 5].map((_, rowIndex) => (
        <ul className="gridrow" key={rowIndex}>
          {[1, 2, 3, 4, 5].map((_, colIndex) => (
            <GridCell
              gridData={gridData}
              posXY={{ row: rowIndex, col: colIndex }}
              key={colIndex}
              onDelete={onDelete}
              onUpgrade={onUpgrade}
              buildMode={buildMode}
              toggleBuildMode={toggleBuildMode}
              structureType={structureType}
              setStructureType={setStructureType}
              structureLevel={structureLevel}
              setStructureLevel={setStructureLevel}
              settlementNumber={settlementNumber}
              planetNumber={planetNumber}
              toggleMenu={toggleMenu} // Pass toggleMenu function
              isOpen={openMenuPosition?.row === rowIndex && openMenuPosition?.col === colIndex} // Pass isOpen state
              rerender={rerender}
              selectTile={selectTile}
              isSelected={selectedTile?.row === rowIndex && selectedTile?.col === colIndex}
            />
          ))}
        </ul>
      ))}
    </div>
  );
};

export default BuildingGrid;