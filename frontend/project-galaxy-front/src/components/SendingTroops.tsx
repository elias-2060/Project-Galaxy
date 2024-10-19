// Importing React and useState hook from react library
import React, { useEffect, useState } from "react";

// Importing images
import attackIcon from "../assets/attackIcon.png";
import planet from "../assets/planet.png";
const API_URL = import.meta.env.VITE_API_URL
// Importing ButtonWithPicture component from Buttons.js file
import { ButtonWithPicture } from "./Buttons";

// Importing DevelopmentTimer component
import DevelopmentTimer from "../components/DevelopmentInfo";

// Importing CSS styles for BuildingGrid components
import "../styles/SendingTroops.css";
import axios from "axios";

interface props {
  toggleCombatMode: () => void;
  playerPlanetName: string;
  opponentPlanetPos: number[];
  rerender: () => void;
  toggleSendingTroops: () => void;
}

const SendingTroops = ({
  toggleCombatMode,
  playerPlanetName,
  opponentPlanetPos,
  rerender,
    toggleSendingTroops
}: props) => {
  const [startTime, setstartTime] = useState(Date.now());
  const [totalTime, setTotalTime] = useState(5000); // Troop send time
  const [timeLeft, setTimeLeft] = useState(
    totalTime - (Date.now() - startTime)
  );
    const [opponentPlanetName, setOpponentPlanetName] = useState("")

  useEffect(() => {
    const timer = setTimeout(() => {
      setTimeLeft((prevTimeLeft) => Math.max(0, prevTimeLeft - 1000)); // Decrease time by 1 second
    }, 1000);

    return () => clearTimeout(timer); // Clear the timer on unmounting
  }, [timeLeft]);


    // Gets all the planet attributes
  useEffect(() => {
    (async () => {
      const response = await axios.post(`${API_URL}/combat/load_enemy`, {
      params: {
        planet_name: playerPlanetName,
        planet_x: opponentPlanetPos[0],
        planet_y: opponentPlanetPos[1]
      }}, {withCredentials: true});
      if (response.data === "User can't attack its own planet"){
          toggleSendingTroops();
      }
      console.log(response.data)
      if (!response.data["can_start"]){
        setOpponentPlanetName(response.data["planet_name"])
      }

    })();
  }, [rerender]);

  return (
    <>
      <div className="friendlyNameAndPlanet">
        <div className="friendly-planet-name">{playerPlanetName}</div>
        <img className="friendlyPlanet" src={planet}></img>
      </div>
      <div className="opponentNameAndPlanet">
        <div className="opponent-planet-name">{opponentPlanetName}</div>
        <img className="opponentPlanet" src={planet}></img>
      </div>

      <div className="troop-arrival-timer">
        <DevelopmentTimer
          startTime={startTime}
          totalTime={totalTime}
          type="sendingTroops"
        />
      </div>

      <div className="startCombatButton">
        <ButtonWithPicture
          imageUrl={attackIcon}
          width={100}
          height={100}
          disabled={timeLeft > 0}
          event={toggleCombatMode}
        ></ButtonWithPicture>
      </div>
    </>
  );
};

export default SendingTroops;
