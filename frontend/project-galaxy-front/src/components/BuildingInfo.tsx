import React, { useState, useEffect, useRef } from "react";
import "../styles/BuildingInfo.css";
import SoldierSelection from "../components/SoldierSelectionMenu"; // Import the SoldierSelection component
import WarpSelection from "../components/WarpScreen"
import LaunchSpaceship from "../components/SpaceShipLaunch";

import gun from "../assets/gun.png";
import hammer from "../assets/hammer.png";
import spaceFood from "../assets/spaceFood.png";

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

// Define the structure of props passed to BuildingInfo component
interface Props {
  structureType: string; // Type of the structure
  structureLevel: number;
  cellPosition: { top: number; left: number }; // Position of the cell
  onUpgrade: () => void; // Function to handle upgrade
  onDelete: () => void; // Function to handle delete
  cellPosXY: { row: number; col: number }; // Row and column of the cell
  planetNumber: number; // Number of the planet
  settlementNumber: number; // Number of the settlement
  rerender: () => void;
  upgradeCost: number;
  updateStructureType: () => void; // New prop for updating structure type
}

// BuildingInfo component receives props and renders building information
const BuildingInfo: React.FC<Props> = ({
  structureType,
  structureLevel,
  cellPosition,
  onUpgrade,
  onDelete,
  cellPosXY,
  planetNumber,
  settlementNumber,
  rerender,
  upgradeCost,
  updateStructureType
}) => {
  // Initialize production and maxStorage variables based on structureType
  let production = 0;
  let maxStorage = 0;
  let type = "";
  let productionType2 = "";
  let maxLevel = 4;
  let playerBuildMaterialCount = 0; // connect this to the player resource count
  const [productionType, setProductionType] = useState(""); // Initialize productionType state

  if (structureType === "Barrack") {
    production = 100;
    maxStorage = 200;
    type = "Barrack";
    productionType2 = "training";
  } else if (structureType === "Mine") {
    production = 150;
    maxStorage = 300;
    type = "Mine";
    productionType2 = "mining";
  } else if (structureType === "Farm") {
    production = 200;
    maxStorage = 400;
    type = "Farm";
    productionType2 = "farming";
  }else if (structureType === "TownHall") {
    type = "TownHall";
    productionType2 = "";
  }
  else if (structureType === "Spaceport") {
    maxStorage = 1000;
    type = "Spaceport";
    productionType2 = "";
  }
  else if (structureType == "Warper"){
    type = "Warper";
  }
  else if (structureType == "UsedWarper"){
    type = "Warper";
  }
  React.useEffect(() => {
    if (structureType === "Barrack") {
      setProductionType("training");
    } else if (structureType === "Mine") {
      setProductionType("mining");
    } else if (structureType === "Farm") {
      setProductionType("farming");
    }
  }, [structureType]); // Run this effect whenever structureType changes

  // State to manage storage and timer
  const [storage, setStorage] = useState(0);
  const [remainingTime, setRemainingTime] = useState<number | null>(null);
  const [startProduction, setStartProduction] = useState(false);
  const [collectDisabled, setCollectDisabled] = useState(storage === 0);
  const [isLaunched, setIsLaunched] = useState(false);
  const [warpingPlanet, setWarpingPlanet] = useState("")


  const [buildingLevel, setBuildingLevel] = useState(1);

  // State to manage visibility of soldier selection window
  const [soldierSelectionVisible, setSoldierSelectionVisible] = useState(false);
  const [spaceShipSelectionVisible, setSpaceShipSelectionVisible] = useState(false);

  // State for visibility warp setup screen
  const [warpSetupVisible, setWarpSetupVisible] = useState(false)

  // Handler for upgrade button click
  const handleUpgrade = async () => {
    onUpgrade(); // Call the provided onUpgrade function

    const response =  await axios.post(`${API_URL}/building/upgrade`, {
      planet_number: planetNumber,
      settlement_number: settlementNumber,
      pos_x: cellPosXY.row,
      pos_y: cellPosXY.col,
    }, { withCredentials: true });
    setBuildingLevel(response.data);
    rerender();
  };

  const farmTimeRef = useRef(0);

  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/building`, {
        params: {
          planet_number: planetNumber,
          settlement_number: settlementNumber,
          pos_x: cellPosXY.row,
          pos_y: cellPosXY.col,
        },
        withCredentials: true
      });
      setBuildingLevel(response.data.level);
      setStorage(response.data.stored_resources ? response.data.stored_resources : 0);
      farmTimeRef.current = response.data.gathering_time_left ? response.data.gathering_time_left : 0;

      // Set the warp location if present
      if (response.data.warped_to !== undefined){
        setWarpingPlanet(response.data.warped_to);
      }

      const deadline = new Date().getTime() + farmTimeRef.current * 1000; // time in milliseconds
      const timer = setInterval(() => {
        const currentTime = new Date().getTime();
        const remainingMilliseconds = deadline - currentTime;

        // Stop the timer when time has passed
        if (remainingMilliseconds <= 0) {
          clearInterval(timer);
          setRemainingTime(null);
          setStartProduction(false); // Enable start farming button
        } else {
          setRemainingTime(remainingMilliseconds);
        }
      }, 1000); // Update every second
    })();
  }, []);


  // Handler for delete button click
  const handleDelete = async () => {
    onDelete(); // Call the provided onDelete function

    const response = await axios.delete(
      `${API_URL}/settlement/building`,
      {
        params: {
          planet_number: planetNumber,
          settlement_number: settlementNumber,
          pos_x: cellPosXY.row,
          pos_y: cellPosXY.col,
        },
        withCredentials: true,
      }
    );
  };

  // Handler for collect button click
  const handleCollect =async () => {
    console.log("Collect button clicked!"); // Log a message on button click

     const response = await axios.post(`${API_URL}/collect_resources`, {
      planetNumber: planetNumber,
      settlementNumber: settlementNumber,
      posX: cellPosXY.row,
      posY: cellPosXY.col,
    }, { withCredentials: true });

    if(response.data == "True"){
      setStorage(0); // Set storage to 0
    }
    rerender();


  };

  // Handler for start farming button click
  const handleStartFarming =async () => {
    console.log("Start Farming button clicked!"); // Log a message on button click

    const response = await axios.post(`${API_URL}/building/production`, {
      planet_number: planetNumber,
      settlement_number: settlementNumber,
      pos_x: cellPosXY.row,
      pos_y: cellPosXY.col,
    }, { withCredentials: true });

    // Disable start farming button
    setStartProduction(true);

    // Calculate remaining time until 5 hours
    const deadline = new Date().getTime() + response.data * 1000; // time in miliseconds
    const timer = setInterval(() => {
      const currentTime = new Date().getTime();
      const remainingMilliseconds = deadline - currentTime;

      // Stop the timer when time has passed
      if (remainingMilliseconds <= 0) {
        clearInterval(timer);
        setRemainingTime(null);
        setStartProduction(false); // Enable start farming button
      } else {
        setRemainingTime(remainingMilliseconds);
      }
    }, 1000); // Update every second
  };

  // Handler for start training button click
  const handleStartTraining = () => {
    console.log("Start Training button clicked!"); // Log a message on button click
    setSoldierSelectionVisible(!soldierSelectionVisible); // Show soldier selection window
  };
  const handleSetupWarp = () => {
    setWarpSetupVisible(!soldierSelectionVisible);
  }
  // Handler for send resources button click
  const handleLaunch = () => {
    console.log("launch button clicked!"); // Log a message on button click
    setSpaceShipSelectionVisible(!spaceShipSelectionVisible); // Show spaceship selection window
  }
  const handleRemoveWarp = () => {
    /**
     * Makes it so when a warp is removed, the warper is reset.
     */
    updateStructureType();
    (async () => {
      const response = await axios.post(`${API_URL}/building/warper/change_warp_link`, {
      params: {
          planet_number: planetNumber,
          pos_y: cellPosXY.row,
          pos_x: cellPosXY.col,
          settlement_number: settlementNumber,
          planet_to_x: null,
          planet_to_y: null
      }},{withCredentials: true});
    })();
    setWarpingPlanet("")
  }

  // Update collect button disabled state when storage changes
  React.useEffect(() => {
    setCollectDisabled(storage === 0);
  }, [storage]);

  return (
    <div
      className="menu-container"
      style={{ top: cellPosition.top, left: cellPosition.left - 370 }}
    >
      <div className="menu2">
        <div className="structure-info">{type} lvl: {buildingLevel}</div>
        {(<div className="stats-info">
          {(() => {
          if (structureType === "Farm" || structureType === "Mine") {
              return (
                <p>
                  Production: {production} / {productionType2}
                </p>
              );
            } else {
              return <p>&nbsp;</p>;
            }
          })()}

          {structureType === "Farm" && (
            <img
              src={spaceFood}
              className="building-icon"
            />
          )}
          {structureType === "Mine" && (
            <img
              src={hammer}
              className="building-icon"
            />
          )}
          {structureType === "Barrack" && (
            <img
              src={gun}
              className="building-icon"
            />
          )}
        </div>)}
        {structureType === "Mine" || structureType === "Farm" ? (
            <div className="stats-info">
              Storage: {storage}
            </div>
        ): warpingPlanet !== "" ? (
            <div className="stats-info">
              Currently Warped to: {warpingPlanet}
            </div>
        )  :structureType === "Warper" &&  warpingPlanet === "" ? (
            <div className="stats-info">
              Warp cost: {2000} <img src={hammer} className="building-icon"/>
            </div>
        ) : (
            <p>&nbsp;</p>
        )}


        <div className="stats-info">
          Upgrade cost: {playerBuildMaterialCount} /{upgradeCost} <img src={hammer} className="building-icon" />
        </div>
        <div className="button-container">
          {/* Button for upgrading the structure */}
          <button className="upgrade-button" onClick={handleUpgrade} disabled={buildingLevel === maxLevel || upgradeCost > playerBuildMaterialCount}>
            Upgrade
          </button>
          {/* Button for deleting the structure */}
          {structureType != "TownHall" && (<button className="delete-button" onClick={handleDelete}>
            Delete
          </button>)}
          {/* Button for collecting resources */}
          {!collectDisabled && (
              <button
                  className="collect-button"
                  onClick={handleCollect}
                  disabled={collectDisabled}
              >
                Collect
              </button>
          )}
          {/* Render the Start Farming or mining button if structureType is Farm or Mine*/}
          {(structureType === "Farm" || structureType === "Mine") && (
            <button
              className="start-farming-button"
              onClick={handleStartFarming}
              disabled={startProduction}
            >
              Start {productionType}
            </button>
            
          )}
          {/* Render the Barracks training button if structureType is Barrack*/}
          {structureType === "Barrack" && (
            <button
              className="start-farming-button"
              onClick={handleStartTraining}
              disabled={startProduction}
            >
              Start training
            </button>
          )}
          {/* Render the Send resources button if structureType is Spaceship*/}
          {structureType === "Spaceport" && (
            <button
              className="start-farming-button"
              onClick={handleLaunch}
              disabled={isLaunched}
            >
              Launch
            </button>
          )}
          {structureType === "Warper" && (
            <button
              className="start-farming-button"
              onClick={handleSetupWarp}
            >
              Set up warp
            </button>
          )}
          {structureType === "UsedWarper" && (
            <button
              className="start-farming-button"
              onClick={handleRemoveWarp}
            >
              Remove current warp
            </button>
          )}
        </div>
        {soldierSelectionVisible && (
          <SoldierSelection
            onClose={() => setSoldierSelectionVisible(false)}
            onStartFarming={handleStartFarming} // Pass handleStartFarming function
            setProductionType={setProductionType} // Pass setter function
            planetNumber={planetNumber}
            settlementNumber={settlementNumber}
            posX={cellPosXY.row}
            posY={cellPosXY.col}
            rerender={rerender}
          />
        )}
        {spaceShipSelectionVisible && (
          <LaunchSpaceship
            onLaunch={updateStructureType}
            posX={cellPosXY.col}
            posY={cellPosXY.row}
            settlementNr={settlementNumber}
            planetNr={planetNumber}
          />
        )}
        {warpSetupVisible && warpingPlanet === "" && (
          <WarpSelection
            onClose={() => setWarpSetupVisible(false)}
            setWarpSetUp={setWarpingPlanet}
            planetNumber={planetNumber}
            updateStructRenderType={updateStructureType}
            rerender={rerender}
            building_x={cellPosXY.col}
            building_y={cellPosXY.row}
            settlement_nr={settlementNumber}
          />
        )}
        {remainingTime !== null && (structureType !== "Barrack") && (
          <div className="time-info">
            {productionType2} ends in: {formatTime(remainingTime)}
          </div>
        )}
        {remainingTime !== null && (structureType === "Barrack") && (
          <div className="time-info">
            {productionType} training ends in: {formatTime(remainingTime)}
          </div>
        )}
      </div>
    </div>
  );
};

// Function to format remaining time in HH:MM:SS format
const formatTime = (milliseconds: number): string => {
  const hours = Math.floor(milliseconds / (1000 * 60 * 60));
  const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
  return `${hours < 10 ? "0" + hours : hours}:${minutes < 10 ? "0" + minutes : minutes
    }:${seconds < 10 ? "0" + seconds : seconds}`;
};

export default BuildingInfo;
