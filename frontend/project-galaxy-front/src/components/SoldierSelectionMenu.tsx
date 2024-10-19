import React, {useEffect, useRef, useState} from "react";
import "../styles/SoldierSelectionMenu.css";
import space_marine from "../assets/space_marine.png"
import space_commando from "../assets/space_commando.png"
import space_drone from "../assets/space_drone.png"
import emtpy_unit from "../assets/empty_unit.png"
import spaceFood from "../assets/spaceFood.png"

import { Link } from "react-router-dom";
import axios from 'axios'
import {Space} from "react-zoomable-ui";

const API_URL = import.meta.env.VITE_API_URL

interface SoldierSelectionProps {
  onClose: () => void;
  onStartFarming: () => void; // Add prop for handleStartFarming function
  setProductionType: (type: string) => void; // Add prop for setter function
  planetNumber: number;
  settlementNumber: number;
  posX: number;
  posY: number;
  rerender: () => void;
}

const SoldierSelection: React.FC<SoldierSelectionProps> = ({
  onClose,
  onStartFarming,
  setProductionType, // Receive setter function
  planetNumber,
  settlementNumber,
  posX,
  posY,
  rerender,

}) => {
  const [selectedSoldier, setSelectedSoldier] = useState<string | null>(null);
  const [hovered_square, setHovered_square] = useState<string | null>(null);
  const [trainingQueue, setTrainingQueue] = useState<string[]>([]);
  const [showStats, setShowStats] = useState<string>("");
  type AttackUnit = {
    unit_id: string;
    type: string;
    level: number;
    building_id: string;
    seconds_since_last_feed: number;
    training_pos: number;
    training_time_left: number;
  }
  type Barrack = {
    building_id: string;
    settlement_id: string;
    grid_pos: { grid_pos_x: number; grid_pos_y: number };
    level: number;
    construction_time_left: number;
    type: string;
    gathering_time_left: number | null;
    stored_resources: number | null;
    space_marine_level: number;
    space_commando_level: number;
    space_drone_level: number;
    space_taken: number;
    space_capacity: number;
    training_units: AttackUnit[] | undefined;
  }
  const [responseData, setResponseData] = useState<Barrack>();
  const [remainingTime, setRemainingTime] = useState<number | null>(null);
  const [rerendering, setRerendering] = useState(false);

  const [refresh, setRefresh] = useState(false);

  const [spaceTaken, setSpaceTaken] = useState<number>(0);
  const [spaceCapacity, setSpaceCapacity] = useState<number>(0);

  const [spaceMarineDisabled, setSpaceMarineDisabled] = useState(false);
  const [spaceCommandoDisabled, setSpaceCommandoDisabled] = useState(false);
  const [spaceDroneDisabled, setSpaceDroneDisabled] = useState(false)
  const [spaceMarineCost, setSpaceMarineCost] = useState(0);
  const [spaceCommandoCost, setSpaceCommandoCost] = useState(0);
  const [spaceDroneCost, setSpaceDroneCost] = useState(0);

  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/building/barrack`, { 
      params: {
        "planet_number": planetNumber,
        "settlement_number": settlementNumber,
        "pos_x": posX,
        "pos_y": posY,
        "include_training_units": true,
      },  
      withCredentials: true });
      setResponseData(response.data);
      setSpaceTaken(response.data.space_taken);
      setSpaceCapacity(response.data.space_capacity);
      setSpaceMarineDisabled(response.data.space_marine_disabled);
      setSpaceCommandoDisabled(response.data.space_commando_disabled);
      setSpaceDroneDisabled(response.data.space_drone_disabled);
      setSpaceMarineCost(response.data.space_marine_cost);
      setSpaceCommandoCost(response.data.space_commando_cost);
      setSpaceDroneCost(response.data.space_drone_cost);

      const trainingTime = response.data.training_units.length ? response.data.training_units[0].training_time_left : 0;
      const deadline = new Date().getTime() + trainingTime * 1000; // time in miliseconds
      const timer = setInterval(() => {
        const currentTime = new Date().getTime();
        const remainingMilliseconds = deadline - currentTime;

        // Stop the timer when time has passed
        if (remainingMilliseconds <= 0) {
          clearInterval(timer);
          setRemainingTime(null);
          removeFromQueue(0);
          rerender();
          setRefresh(prevRefresh => !prevRefresh);
        } else {
          setRemainingTime(remainingMilliseconds);
        }
      }, 1000); // Update every second

    })();
  }, [refresh, rerendering, spaceMarineDisabled, spaceCommandoDisabled, spaceDroneDisabled,
    spaceMarineCost, spaceCommandoCost, spaceDroneCost]);


  const handleSoldierClick = (soldierType: string) => {
    if (selectedSoldier != soldierType){ setSelectedSoldier(soldierType)}
    else {setSelectedSoldier(null)}
  };

   const addToQueue = (soldier: string) => {
    if (trainingQueue.length < 5) {
      setTrainingQueue((prevQueue) => [...prevQueue, soldier]);
    }
  };

  const removeFromQueue = (index: number) => {
    setTrainingQueue((prevQueue) => {
      const newQueue = [...prevQueue];
      newQueue.splice(index, 1);
      setRerendering(!rerendering);
      return newQueue;
    });
  };

  // This function returns the right image source for the type of the soldier in the queue
  function getImageByQueuePosition(soldierPosition: number): string {
    const type = trainingQueue.at(soldierPosition)
  switch (type) {
    case "space_marines":
      return space_marine; // Assuming space_marine is the image path for Space Marine
    case "space_commandos":
      return space_commando; // Assuming space_commando is the image path for Space Commando
    case "space_drones":
      return space_drone; // Assuming space_drone is the image path for Space Drone
    default:
      return emtpy_unit; // Default to an empty string if no matching image found
  }
}
const handleSoldierHover = (soldierType: string) => {
    setHovered_square(soldierType);
  };

  const handleSoldierLeave = () => {
    setHovered_square(null);
  };

  const handleInfoButtonClick = () => {
    // Add logic for info button click if needed
  };

  // Inside SoldierSelection component
  const handleTrainClick =async () => {
    if (selectedSoldier && trainingQueue.length < 6) {
      console.log(`Training soldier: ${selectedSoldier}`);
      //addToQueue()
      // Set productionType based on a selected soldier type
      setProductionType(selectedSoldier.toLowerCase());
      // Call handleStartFarming function from parent
      //onStartFarming();

      const response = await axios.post(`${API_URL}/building/barrack/unit`, {
        "planet_number": planetNumber,
        "settlement_number": settlementNumber,
        "pos_x": posX,
        "pos_y": posY,
        "unit": selectedSoldier
      }, { withCredentials: true });

      setRerendering(!rerendering);

    }
  };
  const handleShowStats = (soldierType: string) => {
    if (showStats === soldierType) {
      setShowStats("");
    } else {
      setShowStats(soldierType);
    }
  };
  if (responseData !== undefined && responseData.training_units !== undefined) {
    for (let i = trainingQueue.length; i < responseData.training_units.length; i++) {
      addToQueue(responseData.training_units[i].type);
    }
  }
    

  return (
      <div className="soldier-selection-window">
        <button className="close-button2" onClick={onClose}>x</button>
        {/* The training queue */}
        <h2>Training Queue </h2>
        <ul className="training-queue">
          <li
              onMouseEnter={() => handleSoldierHover("train_slot_0")}
              onMouseLeave={() => handleSoldierLeave()}
              className={(hovered_square === "train_slot_0" ? "hover" : "")}
          >
            <div className={"soldier-info"}>
              <img src={getImageByQueuePosition(0)} alt="Space Marine" width={120} height={120}/>
              {remainingTime !== null && (
                <div className="time-info">
                  {formatTime(remainingTime)}
                </div>
              )}
            </div>
          </li>
          <li
              onMouseEnter={() => handleSoldierHover("train_slot_1")}
              onMouseLeave={() => handleSoldierLeave()}
              className={(hovered_square === "train_slot_1" ? "hover" : "")}
          >
            <div className={"soldier-info"}>
              <img src={getImageByQueuePosition(1)} alt="Space Marine" width={120} height={120}/>
              <span></span>
            </div>
          </li>
          <li
              onMouseEnter={() => handleSoldierHover("train_slot_2")}
              onMouseLeave={() => handleSoldierLeave()}
              className={(hovered_square === "train_slot_2" ? "hover" : "")}
          >
            <div className={"soldier-info"}>
              <img src={getImageByQueuePosition(2)} alt="Space Marine" width={120} height={120}/>
              <span></span>
            </div>
          </li>
          <li
              onMouseEnter={() => handleSoldierHover("train_slot_3")}
              onMouseLeave={() => handleSoldierLeave()}
              className={(hovered_square === "train_slot_3" ? "hover" : "")}
          >
            <div className={"soldier-info"}>
              <img src={getImageByQueuePosition(3)} alt="Space Marine" width={120} height={120}/>
              <span></span>
            </div>
          </li>
          <li
              onMouseEnter={() => handleSoldierHover("train_slot_4")}
              onMouseLeave={() => handleSoldierLeave()}
              className={(hovered_square === "train_slot_4" ? "hover" : "")}
          >
            <div className={"soldier-info"}>
              <img src={getImageByQueuePosition(4)} alt="Space Marine" width={120} height={120}/>
              <span></span>
            </div>
          </li>
        </ul>
        <h3> {spaceTaken} / {spaceCapacity}</h3>


        <h2>Select Soldier Type</h2>
        {/* List of soldier types */}
        <ul>
          <li
              onClick={() => handleSoldierClick("Space Marine")}
              onMouseEnter={() => handleSoldierHover("Space Marine")}
              onMouseLeave={() => handleSoldierLeave()}
              className={
                  (spaceMarineDisabled ? "disabled" : "") +
            (selectedSoldier === "Space Marine" ? "selected " : "") +
                  (hovered_square === "Space Marine" ? "hover" : "")
          }

          >
            <div className={"soldier-info"}>
              <img src={space_marine} alt="Space Marine" width={120} height={120}/>
              <h4 className={"center_items"}>{
                spaceMarineCost}
                <img className={"reset-image"} src={spaceFood} alt="Space Food"/>
              </h4>
              <button
                  onMouseEnter={() => handleSoldierLeave()}
                  className="info-button"
                  onMouseLeave={() => handleSoldierHover("Space Marine")}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedSoldier("");
                    handleShowStats("Space Marine")
                  }}
              >ℹ️
              </button>
            </div>
          </li>
          <li
              onClick={() => handleSoldierClick("Space Commando")}
              onMouseEnter={() => handleSoldierHover("Space Commando")}
              onMouseLeave={() => handleSoldierLeave()}
              className={(spaceCommandoDisabled ? "disabled" : "") +
                  (selectedSoldier === "Space Commando" ? "selected " : "") +
                  (hovered_square === "Space Commando" ? "hover" : "")}

          >
            <div className={"soldier-info"}>
              <img src={space_commando} alt="Space Commando" width={120} height={120}/>
              <h4 className={"center_items"}>{
                spaceCommandoCost}
                <img className={"reset-image"} src={spaceFood} alt="Space Food"/>
              </h4>
              <button
                  onMouseEnter={() => handleSoldierLeave()} className="info-button"
                  onMouseLeave={() => handleSoldierHover("Space Commando")}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedSoldier("");
                    handleShowStats("Space Commando")
                  }}
              >ℹ️
              </button>
            </div>
          </li>
          <li
              onClick={() => handleSoldierClick("Space Drone")}
              onMouseEnter={() => handleSoldierHover("Space Drone")}
              onMouseLeave={() => handleSoldierLeave()}
              className={(spaceCommandoDisabled ? "disabled" : "") +
                  (selectedSoldier === "Space Drone" ? "selected " : "") +
                  (hovered_square === "Space Drone" ? "hover" : "")}

          >
            <div className={"soldier-info"}>
              <img src={space_drone} alt="Space Drone" width={120} height={120}/>
              <h4 className={"center_items"}>{
                spaceDroneCost}
                <img className={"reset-image"} src={spaceFood} alt="Space Food"/>
              </h4>
              <button
                  onMouseEnter={() => handleSoldierLeave()} className="info-button"
                  onMouseLeave={() => handleSoldierHover("Space Drone")}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedSoldier("");
                    handleShowStats("Space Drone")
                  }}
              >ℹ️
              </button>
            </div>
          </li>

          {/* All the stats*/}
          {showStats === "Space Marine" &&
          <li className={"soldier-stats"}>
            <div>
              <table>
                <tbody>
                <tr>
                  <th>Name:</th>
                  <td>Space Marine</td>
                </tr>
                <tr>
                  <th>Food per Hour</th>
                  <td>3</td>
                </tr>
                <tr>
                  <th>Training cost (food)</th>
                  <td>10</td>
                </tr>
                <tr>
                  <th>Training time (s)</th>
                  <td>60</td>
                </tr>
                <tr>
                  <th>Unit size</th>
                  <td>3</td>
                </tr>
                <tr>
                  <th>Attack Power</th>
                  <td>10</td>
                </tr>
                </tbody>
              </table>

            </div>
          </li>}
          {showStats === "Space Commando" &&
          <li className={"soldier-stats"}>
            <div>
              <table>
                <tbody>
                <tr>
                  <th>Name:</th>
                  <td>Space Commando</td>
                </tr>
                <tr>
                  <th>Food per Hour</th>
                  <td>9</td>
                </tr>
                <tr>
                  <th>Training cost (food)</th>
                  <td>40</td>
                </tr>
                <tr>
                  <th>Training time (s)</th>
                  <td>240</td>
                </tr>
                <tr>
                  <th>Unit size</th>
                  <td>6</td>
                </tr>
                <tr>
                  <th>Attack Power</th>
                  <td>9</td>
                </tr>
                </tbody>
              </table>

            </div>
          </li>}
          {showStats === "Space Drone" &&
          <li className={"soldier-stats"}>
            <div>
              <table>
                <tbody>
                <tr>
                  <th>Name:</th>
                  <td>Space Drone</td>
                </tr>
                <tr>
                  <th>Food per Hour</th>
                  <td>50</td>
                </tr>
                <tr>
                  <th>Training cost (food)</th>
                  <td>1000</td>
                </tr>
                <tr>
                  <th>Training time (s)</th>
                  <td>1800</td>
                </tr>
                <tr>
                  <th>Unit size</th>
                  <td>20</td>
                </tr>
                <tr>
                  <th>Attack Power</th>
                  <td>200</td>
                </tr>
                </tbody>
              </table>

            </div>
          </li>}
        </ul>


        <button
            onClick={() => handleTrainClick()} disabled={!selectedSoldier}>
          Train
        </button>

      </div>
  );
};


const formatTime = (milliseconds: number): string => {
  const hours = Math.floor(milliseconds / (1000 * 60 * 60));
  const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
  return `${hours < 10 ? "0" + hours : hours}:${minutes < 10 ? "0" + minutes : minutes
    }:${seconds < 10 ? "0" + seconds : seconds}`;
};

export default SoldierSelection;
