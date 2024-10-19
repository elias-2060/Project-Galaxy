import React, { useEffect, useImperativeHandle, useState } from "react";
import "../styles/CombatView.css";

// Importing ButtonWithPicture component from Buttons.js file
import { ButtonWithPicture } from "./Buttons";
import { ButtonWithText } from "./Buttons"
const API_URL = import.meta.env.VITE_API_URL
// Importing images
import planet from "../assets/planet.png";
import space_marine from "../assets/space_marine.png";
import space_commando from "../assets/space_commando.png";
import space_drone from "../assets/space_drone.png";
import attackIcon from "../assets/attackIcon.png";
import autoplayIcon from "../assets/autoplayIcon.png";
import axios from "axios";

interface dropdownProps {
  selected: string;
  setSelected: (arg0: string) => void;
  isOpponent: boolean;
  attackUnits: {"attack_power": number, "type": string}[];
}

const DropDownMenu = ({ selected, setSelected, isOpponent , attackUnits}: dropdownProps) => {
  const [isActive, setIsActive] = useState(false);
  const [unitSprite, setUnitSprite] = useState("");
  const options = ["Space-Marines", "Space-Commandos", "Space-Drones"];

  useEffect(() => {
    if (selected == "Space-Marines") {
      setUnitSprite(space_marine);
    } else if (selected == "Space-Commandos") {
      setUnitSprite(space_commando);
    } else if (selected == "Space-Drones") {
      setUnitSprite(space_drone);
    }
  }, [selected])

  function hasUnitType(units: {"attack_power": number, "type": string}[], unitType: string): boolean {
    return units.some(unit => unit["type"] === unitType);
}

  return (
    <>
      <div className="dropdown">
        <div
          className={isOpponent ? "dropdown-btn-opponent" : "dropdown-btn"}
          onClick={() => {
            setIsActive(!isActive);
          }}
        >
          {selected.startsWith("Space-")? selected.substring(6): selected}
          {unitSprite && <img src={unitSprite} className="unit-sprite"  alt={"unitSprite"}/>}
          {!isOpponent && <span className="carret"></span>}
        </div>
        {isActive && !isOpponent && (
          <div className="dropdown-content">
            {options.map((option) => (hasUnitType(attackUnits, option) &&
              <div
                className="dropdown-item"
                onClick={() => {
                  setSelected(option);
                  setIsActive(false);
                }}
              >
                {option}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
};

interface props {
  playerPlanetName: string;
  opponentPlanetPos: number[];
  rerender: () => void;
  toggleCombat: () => void;
}

const CombatView = ({ playerPlanetName, opponentPlanetPos, rerender, toggleCombat}: props) => {
  const [playerSelectedUnit, setPlayerSelectedUnit] = useState("Choose Unit");
  const [playerUnitCount, setPlayerUnitCount] = useState(0);
  const [playerDiceRoll, setPlayerDiceRoll] = useState(0);
  const [opponentPlanetName, setOpponentPlanetName] = useState("")

  const [opponentSelectedUnit, setOpponentSelectedUnit] = useState("Space-Marines");
  const [opponentUnitCount, setOpponentUnitCount] = useState(0);
  const [opponentDiceRoll, setOpponentDiceRoll] = useState(0);

  const [rollingDice, setRollingDice] = useState(false);

  const [playerPassiveProc, setPlayerPassiveProc] = useState(false);
  const [opponentPassiveProc, setOpponentPassiveProc] = useState(false)

  const [autoPlay, setAutoPlay] = useState(false)
  
  const [playerWon, setPlayerWon] = useState(false)
  const [opponentWon, setOpponentWon] = useState(false)

  const [attackUnits, setAttackUnits] =
      useState([
          {
            "attack_power": 0,
            "type": "Space-Marines"
          },
        {
          "attack_power": 0,
          "type": "Space-Commandos"
        },{
        "attack_power": 0,
          "type": "Space-Drones"
      }])
  const [defenceUnits, setDefenceUnits] =
      useState([
          {"attack_power": 0,
            "type": "None"
          }])


  const randomNumberInRange = (min: number, max: number) => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  };

  const delay = (ms:number) => new Promise((resolve) => setTimeout(resolve, ms));

  useEffect(() => {
        (async () => {
      const response = await axios.post(`${API_URL}/combat/load_attack_data`, {
      params: {
        planet_name: playerPlanetName,
        planet_xy_to: opponentPlanetPos,
        create_attack: true
      }}, {withCredentials: true});
        setOpponentPlanetName(response.data.opponent.planet_name);
        setAttackUnits(response.data["attacking_units"])
        setDefenceUnits(response.data["defending_units"])
        setOpponentUnitCount(response.data["defending_units"].length);
        setPlayerUnitCount(response.data["attacking_units"].length);
    })();
  }, []);

  const [seconds, setSeconds] = useState(-2);

    useEffect(() => {
    const interval = setInterval(() => {
      setSeconds(prevSeconds => prevSeconds + 1);
      updateFunction();
    }, 5000);
    // Cleanup function to clear the interval when the component unmounts
    return () => clearInterval(interval);
  }, [autoPlay]);

    // Plays a round
    const playRound = () =>{
      console.log("playing round");
      // Calls the play round function from backend
    (async () => {
    const response = await axios.post(`${API_URL}/combat/play_round`, {
    params: {
        planet_name: playerPlanetName,
        selected_attack_type: playerSelectedUnit
      }}, {withCredentials: true});
        setRollingDice(true);
        for (let i = 0; i < 10; i++) {
          setPlayerDiceRoll(randomNumberInRange(0, 6));
          setOpponentDiceRoll(randomNumberInRange(0, 6));
          await delay(50);
        }
        setPlayerDiceRoll(response.data["roll_a"]);
        setOpponentDiceRoll(response.data["roll_b"]);
        setPlayerPassiveProc(response.data.passive_a);
        setOpponentPassiveProc(response.data.passive_b);
        if (response.data.combat_result !== ""){
          if (response.data === "Win"){
            setPlayerWon(true);
          }
          else {
            setOpponentWon(true);
          }
        }
        
        setRollingDice(false);
    })();
    }

    // Toggles autoplay
    const toggle_autoplay = () =>{
      console.log("autoplay toggled", !autoPlay);
      setAutoPlay(!autoPlay);
    }

  const updateFunction = () => {
      console.log("update");
      console.log("autoplay: ", autoPlay);
      // If autoplay is enabled, play a round
        if (autoPlay){
          playRound();
        }
    // Update all values, does this every 5 seconds
    (async () => {
      const response = await axios.post(`${API_URL}/combat/load_attack_data`, {
      params: {
        planet_name: playerPlanetName,
        planet_xy_to: opponentPlanetPos,
        create_attack: false
      }}, {withCredentials: true});

        // Reload all the variables
        setAttackUnits(response.data["attacking_units"])
        setDefenceUnits(response.data["defending_units"])
        setOpponentUnitCount(response.data["defending_units"].length)
        setPlayerUnitCount(response.data["attacking_units"].length)

        // Leave the screen if there are either no attack or defense units.
        if (response.data["defending_units"].length == 0 || response.data["attacking_units"].length == 0){
        toggleCombat();
        }

        // Select the (strongest) opponent unit
        setOpponentSelectedUnit(response.data["defending_units"][0]["type"]);

        rerender();
    })();
  };

  const endCombat = () => {
    (async () => {
      await axios.post(`${API_URL}/combat/end_attack`, {
      params: {
        planet_name: playerPlanetName,
        planet_xy_to: opponentPlanetPos,
        opponent_won: opponentWon,
      }}, {withCredentials: true});
    })();
    toggleCombat();
  }

  return (
    <>
      {!playerWon && !opponentWon && (<>
      {/* display both planets and their names*/}
      <div className="friendlyNameAndPlanet">
        <div className="friendly-planet-name">{playerPlanetName}</div>
        <img className="friendlyPlanet" src={planet} alt={"planet"}></img>
      </div>
      <div className="opponentNameAndPlanet">
        <div className="opponent-planet-name">{opponentPlanetName}</div>
        <img className="opponentPlanet" src={planet} alt={"planet"}></img>
      </div>
      {/* display unit selectors*/}
      <div className="player-unit-dropdown-selector">
        <DropDownMenu
          attackUnits={attackUnits}
          selected={playerSelectedUnit}
          setSelected={setPlayerSelectedUnit}
          isOpponent={false}
        ></DropDownMenu>
        <div className="player-unit-count">{playerUnitCount}</div>
        <div
          className={
            "dice-roll" +
            (rollingDice? "" : playerDiceRoll == opponentDiceRoll? "" : playerDiceRoll > opponentDiceRoll ? " round-won" : " round-lost")
          }
        >
          {playerDiceRoll}
        </div>
        <div className={playerPassiveProc? "passive-description active" : "passive-description"}>
          {playerSelectedUnit == "Space-Marines"? "Passive: For every 2 rounds survived, gain 10 power.": ""}
          {playerSelectedUnit == "Space-Commandos"? "Passive: 5% chance of winning the round, regardless of round outcome.": ""}
          {playerSelectedUnit == "Space-Drones"? "Passive: 5% chance to die regardless of round outcome. On death, 25% chance to kill the enemy in it's explosion.": ""}
        </div>
      </div>
      <div className="opponent-unit-dropdown-selector">
        <div
          className={
            "dice-roll" +
            (rollingDice? "" : playerDiceRoll == opponentDiceRoll ? "" : playerDiceRoll < opponentDiceRoll ? " round-won" : " round-lost")
          }
        >
          {opponentDiceRoll}
        </div>
        <div className="opponent-unit-count">{opponentUnitCount}</div>
        <DropDownMenu
          attackUnits={defenceUnits}
          selected={opponentSelectedUnit}
          setSelected={setOpponentSelectedUnit}
          isOpponent={true}
        ></DropDownMenu>
        {/* placeholder divs to properly position te passive description*/}
        <div></div>
        <div></div>
        <div className={opponentPassiveProc? "passive-description active" : "passive-description"}>
          {opponentSelectedUnit == "Space-Marines"? "Passive: For every 2 rounds survived, gain 10 power.": ""}
          {opponentSelectedUnit == "Space-Commandos"? "Passive: 5% chance of winning the round, regardless of round outcome.": ""}
          {opponentSelectedUnit == "Space-Drones"? "Passive: 5% chance to die regardless of round outcome. On death, 25% chance to kill the enemy in it's explosion.": ""}
        </div>
      </div>

      {/* display attack button*/}
      <div className="startTurnButton">
        <ButtonWithPicture
          event={playRound}
          imageUrl={attackIcon}
          width={100}
          height={100}
          disabled={playerSelectedUnit == "Choose Unit"}
        ></ButtonWithPicture>
      </div>

      {/* display attack button*/}
      <div className="autoPlayButton">
        <ButtonWithPicture
          event={toggle_autoplay}
          imageUrl={autoplayIcon}
          width={100}
          height={100}
          disabled={playerSelectedUnit == "Choose Unit"}
        ></ButtonWithPicture>
      </div>      
      </>)
      }
      {playerWon && (
      <>
      <div className="combat-result">
        <div className="victory">Victory</div>
        <div className="victory-text-1">Your troops have won the battle!</div>
        <div className="victory-text-2">Resource rewards will be collected and be added to your planet shortly.</div>
        <ButtonWithText value="Return to Planet" width={400} height={100} event={endCombat}></ButtonWithText>
      </div>
      </>)
      }
      {opponentWon && (
      <>
      <div className="combat-result">
        <div className="defeat">Defeat</div>
        <div className="defeat-text-1">Your troops have been defeated in battle.</div>
        <div className="defeat-text-2">Can't win them all.<br/> Regroup and rearm, tommorow is another day.</div>
        <ButtonWithText value="Return to Planet" width={400} height={100} event={endCombat}></ButtonWithText>
      </div>
      </>)
      }
    </>
  );
};

export default CombatView;
