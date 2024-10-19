import "../styles/AttackMap.css";

import { Space } from "react-zoomable-ui";

import axios from "axios";
import { useState, useEffect } from "react";

// defining the interface for the planets on the map
interface AttackMapPlantetProps {
  style: { top: number; left: number };
  OpponentToggle: () => void;
  handlePlanetPosition: (posX: number, posY: number) => void;
  id: string;
  posX: number;
  posY: number;
}
// defining the interface for the map
interface AttackMapProps {
  OpponentToggle: () => void;
  handlePlanetPosition: (posX: number, posY: number) => void;
  // Starting coordinates of the current planet on the map
  planetX: number,
  planetY: number
}

// defining AttackMapPlanet component
const AttackMapPlanet = ({
  style,
  OpponentToggle,
  handlePlanetPosition,
  id,
  posX,
  posY,
}: AttackMapPlantetProps) => {
  return (
    <>
      <button
        className="AttackMapPlanet"
        style={style}
        onClick={() => {
          OpponentToggle();
          handlePlanetPosition(posX, posY);
        }}
        id={id}
      ></button>
    </>
  );
};

const API_URL = import.meta.env.VITE_API_URL

// defining AttackMap component
const AttackMap = ({ OpponentToggle, handlePlanetPosition, planetX, planetY}: AttackMapProps) => {

  const [coordinates, setCoordinates] = useState([]);

  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/planet/all`, {withCredentials: true});
      setCoordinates(response.data);
      })();
    }, []);

  // Map of planets
  let planets: any[] = [];

  // Map of planet coordinates
  let planetCoords =
    coordinates;

  // Largest x and y coordinates
  let largestX = 0;
  let largestY = 0;

  if (coordinates !== null){
      // Create a planet for each coordinate and put it in the planet map
      for (let i = 0; i < planetCoords.length; i++) {
        if (planetCoords[i]["planet_x"] > largestX) largestX = planetCoords[i]["planet_x"];
        if (planetCoords[i]["planet_y"] > largestY) largestY = planetCoords[i]["planet_y"];
        const style = {
          left: planetCoords[i]["planet_x"],
          top: planetCoords[i]["planet_y"],
        };
        planets.push(
          <AttackMapPlanet
            style={style}
            id={i.toString()}
            OpponentToggle={OpponentToggle}
            handlePlanetPosition={handlePlanetPosition}
            posX={planetCoords[i]["planet_x"]}
            posY={planetCoords[i]["planet_y"]}
          ></AttackMapPlanet>
        );
      }
  }
  
  // Add padding so planets arent rendered off the map
  largestX = largestX;
  largestY = largestY;

  // Making the map square and have a size of at least 3000
  if (largestX > largestY) largestY = largestX;
  if (largestY > largestX) largestX = largestY;
  if (largestX < 3000) {
    largestX = 3000;
    largestY = 3000;
  }
  // Setting the size of the map
  const style = {
    width: largestX,
    height: largestY,
  };

  if (coordinates === null) return <div>Loading...</div>;

  // Returning JSX for the shop bar
  return (
    <>
      <Space
        onCreate={(viewPort) => {
          viewPort.setBounds({ x: [0, 10000], y: [0, 10000] });
          viewPort.camera.centerFitAreaIntoView({
            left: planetX - 500,
            top: planetY - 500,
            width: 1000,
            height: 1000,
          });
        }}
      >
        <div className="MapContainer" style={style}>
          {planets}
        </div>
      </Space>
    </>
  );
};

export default AttackMap;
