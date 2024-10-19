// Importing DisplayBox and DisplayBoxWithPicture components
import DisplayBox from "./DisplayBox";
import DisplayBoxWithPicture from "./DisplayBoxWithPicture";

// Importing ButtonWithPicture component from Buttons.js file
import { ButtonWithPicture } from "./Buttons";

import "../styles/OpponentInfo.css";

import gun from "../assets/gun.png";
import hammer from "../assets/hammer.png";
import profileIcon from "../assets/profileIcon.png";
import spaceFood from "../assets/spaceFood.png";

import axios from "axios";
import { useState, useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL

interface OpponentInfoProps {
  planet_posX: number;
  planet_posY: number;
}

const OpponentInfo = ({
  planet_posX,
  planet_posY,
}: OpponentInfoProps) => {

  const [user, setUser] = useState("");
  const [race, setRace] = useState("");
  const [buildingMaterials, setBuildingMaterials] = useState("0");
  const [ration, setRation] = useState("0");
  const [attackPower, setAttackPower] = useState("0");

  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/planet/opponent`, {
        params: {
          pos_x: planet_posX,
          pos_y: planet_posY,
        },
        
        withCredentials: true,
      });

      setUser(response.data.user_name);
      setRace(response.data.race_name);
      setBuildingMaterials(response.data.resources.building_materials);
      setRation(response.data.resources.rations);
      setAttackPower(response.data.attack_power);

    })();
  }, []);

  return (
    <>
      {/* Display profile button */}
      <div className="opponentProfile">
        <ButtonWithPicture
          imageUrl={profileIcon}
          width={70}
          height={70}
        ></ButtonWithPicture>
      </div>

      {/* Display user name */}
      <div className="opponentUserName">
        <DisplayBox value={user} width={150} height={15}></DisplayBox>
      </div>

      {/* Display race name */}
      <div className="opponentRaceName">
        <DisplayBox value={race} width={150} height={15}></DisplayBox>
      </div>

      {/* Display building resources */}
      <div className="opponentBuildingResources">
        <DisplayBoxWithPicture
          value={buildingMaterials}
          width={100}
          height={15}
          imgUrl={hammer}
        ></DisplayBoxWithPicture>
      </div>

      {/* Display food */}
      <div className="opponentFood">
        <DisplayBoxWithPicture
          value={ration}
          width={100}
          height={15}
          imgUrl={spaceFood}
        ></DisplayBoxWithPicture>
      </div>

      {/* Display troops */}
      <div className="opponentTroops">
        <DisplayBoxWithPicture
          value={attackPower}
          width={100}
          height={15}
          imgUrl={gun}
        ></DisplayBoxWithPicture>
      </div>
    </>
  );
};

export default OpponentInfo;
