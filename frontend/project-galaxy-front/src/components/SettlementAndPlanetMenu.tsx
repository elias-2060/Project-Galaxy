// Importing useState hook from react library
import { useEffect, useState } from "react";

// Importing ButtonWithText component from Buttons.tsx file
import { ButtonWithText } from "./Buttons";

// Importing CSS styles
import "../styles/settlementPlanetMenu.css";

// Importing images
import hammer from "../assets/hammer.png";
import spaceFood from "../assets/spaceFood.png";
import settlement from "../assets/segment.png";
import { on } from "events";

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

interface props3 {
  onPlanetNumberChange: (planetNumber: number) => void;
  planetNumber: (planetNumber: number) => void;
}

interface props4 {
  toggleView: () => void;
}


// defining SwitchPlanet component which shows the menu for the player to switch planets
const SwitchPlanet: React.FC<props3> = ({
  onPlanetNumberChange,
  planetNumber,
}) => {
  type Planet = 
    {
      planet_id: string,
      coordinates: {
        planet_x: number,
        planet_y: number,
      },
      user_id: string,
      planet_name: string,
      resources: {
        building_materials: number,
        rations: number,
        attack_power: number,
    },
  }
  const [responsePlanets, setResponsePlanets] = useState<Planet[]>([]); // State to store the names of the planets
  
  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/planet/all`, { params: { own_only: true }, withCredentials: true });
      setResponsePlanets(response.data);
    })();
  }, []);

  let planets = [];
  for (let i = 0; i < responsePlanets.length; i++) {
    planets.push(
      <ButtonWithText
        value={responsePlanets[i].planet_name}
        height={50}
        width={280}
        event={() => {
          onPlanetNumberChange(i);
          planetNumber(i);
        }}
        disabled={false}
      ></ButtonWithText>
    );
  }

  // Returning JSX for SwitchPlanet
  return (
    <>
      <div className="SwitchPlanet">{planets}</div>
    </>
  );
};

// defining BuyPlanet component which shows the menu for the player to buy planets
const BuyPlanet: React.FC<props4> = ({
  toggleView,
}) => {

  const [coordinates, setCoordinates] = useState<[number, number][]>([]);

  const add_planet = async (posX: Number, posY: Number) => {
    const name = prompt('Enter planet name:'); // store this name in the database
   await axios.post(`${API_URL}/planet`,{pos_x: posX, pos_y: posY, planet_name: name}, { withCredentials: true });
  }

  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/planet/buy_list`, { withCredentials: true });
      console.log(response.data);
      setCoordinates(response.data.coordinates);
    }
    )();
  }, []);

  let planets = [];
  for (let i = 0; i < coordinates.length; i++) {
    planets.push(
      <ButtonWithText
        value={"(" + coordinates[i][0].toString() + "," + coordinates[i][1].toString() + ")"}
        height={50}
        width={280}
        event={() => {
          add_planet(coordinates[i][0], coordinates[i][1])
          toggleView();
        }}
        disabled={false}
      ></ButtonWithText>
    );
  }

  // Returning JSX for BuyPlanet
  return (
    <div className="BuyPlanet">
      {planets}
      <div className="CostBar">
        &nbsp; Cost: X &nbsp;
        <img src={spaceFood} className="cost-icon" />
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; X &nbsp;
        <img src={hammer} className="cost-icon" />
      </div>
    </div>
  );
};

interface props {
  unlockSecondSettlement: () => void;
  unlockThirdSettlement: () => void;
  secondSettlementBought: boolean;
  thirdSettlementBought: boolean;
  planetNumber: number;
}

interface props2 {
  unlockSecondSettlement: () => void;
  unlockThirdSettlement: () => void;
  secondSettlementBought: boolean;
  thirdSettlementBought: boolean;
  onPlanetNumberChange: (planetNumber: number) => void;
  planetNumber: number;
  toggleView: () => void;
  building_materials: number;
}

// defining BuySettlement component which shows the menu for the player to buy settlements
const BuySettlement: React.FC<props> = ({
  unlockSecondSettlement,
  unlockThirdSettlement,
  secondSettlementBought,
  thirdSettlementBought,
  planetNumber,
}) => {

  const add_settlement = async () => {
    await axios.post(`${API_URL}/planet/settlement`,{planet_number: planetNumber}, { withCredentials: true });
  }

  // Returning JSX for BuySettlement
  return (
    <div className="BuySettlement">
      <button
        className="SecondSettlement"
        onClick={() => {
          add_settlement();
          unlockSecondSettlement();
        }}
        disabled={secondSettlementBought}
      >
        <div className="SettlementName">
          <img src={settlement} /> Second Settlement
        </div>
        <div className="SettlementCost">
          Cost: &nbsp; X <img src={spaceFood} className="food" />
          &nbsp;&nbsp; X <img src={hammer} className="hammer" />
        </div>
      </button>
      <button
        className="ThirdSettlement"
        onClick={() => {
          add_settlement();
          unlockThirdSettlement();
        }}
        disabled={thirdSettlementBought}
      >
        <div className="SettlementName">
          <img src={settlement} /> Third Settlement
        </div>
        <div className="SettlementCost">
          Cost: &nbsp; X <img src={spaceFood} className="food" />
          &nbsp;&nbsp; X <img src={hammer} className="hammer" />
        </div>
      </button>
    </div>
  );
};

// defining SettlementAndPlanetMenu component which allows the player to buy/switch planets or settlements
const SettlementAndPlanetMenu: React.FC<props2> = ({
  unlockSecondSettlement,
  unlockThirdSettlement,
  secondSettlementBought,
  thirdSettlementBought,
  onPlanetNumberChange,
  planetNumber,
  toggleView,
    building_materials,
}) => {
  const [SwitchPlanetView, setSwitchPlanetView] = useState(false); // State to track the visibility of the SwitchPlanet menu
  const [BuyPlanetView, setBuyPlanetView] = useState(false); // State to track the visibility of the BuyPlanet menu
  const [BuySettlementView, setBuySettlementView] = useState(false); // State to track the visibility of the BuySettlement menu

  // Function to toggle the visibility of the SwitchPlanet menu and hide others
  const toggleSwitchPlanetView = () => {
    setSwitchPlanetView(!SwitchPlanetView);
    setBuyPlanetView(false);
    setBuySettlementView(false);
  };

  // Function to toggle the visibility of the BuyPlanet menu and hide others
  const toggleBuyPlanetView = () => {
    setSwitchPlanetView(false);
    setBuyPlanetView(!BuyPlanetView);
    setBuySettlementView(false);
  };

  // Function to toggle the visibility of the BuySettlement menu and hide others
  const toggleBuySettlementView = () => {
    setSwitchPlanetView(false);
    setBuyPlanetView(false);
    setBuySettlementView(!BuySettlementView);
  };

  const updatePlanetNumeber = (updatedPlanetNumber: number) => {
    planetNumber = updatedPlanetNumber;
  };

  // Returning JSX for SettlementAndPlanetMenu
  return (
    <>
      <div className="SettlementAndPlanetMenu">
        <ButtonWithText
          value="switch planet"
          height={50}
          width={150}
          event={toggleSwitchPlanetView}
          disabled={false}
        ></ButtonWithText>
        <ButtonWithText
          value="buy planet"
          height={50}
          width={150}
          event={toggleBuyPlanetView}
          disabled={building_materials < 10000}
        ></ButtonWithText>
        <ButtonWithText
          value="buy settlement"
          height={50}
          width={170}
          event={toggleBuySettlementView}
          disabled={building_materials < 3000}
        ></ButtonWithText>
      </div>
      {SwitchPlanetView && <SwitchPlanet onPlanetNumberChange={onPlanetNumberChange} planetNumber={updatePlanetNumeber} />}
      {BuyPlanetView && <BuyPlanet toggleView={toggleView} />}
      {BuySettlementView && (
        <BuySettlement
          unlockSecondSettlement={unlockSecondSettlement}
          unlockThirdSettlement={unlockThirdSettlement}
          secondSettlementBought={secondSettlementBought}
          thirdSettlementBought={thirdSettlementBought}
          planetNumber={planetNumber}
        />
      )}
    </>
  );
};

export default SettlementAndPlanetMenu;
