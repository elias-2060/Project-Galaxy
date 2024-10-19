// Importing ButtonWithPicture component from Buttons.js file
import { ButtonWithPicture } from "./Buttons";

// Importing React and useState hook from React library
import React, { useEffect, useState } from "react";

// Importing DisplayBox and DisplayBoxWithPicture components
import DisplayBox from "./DisplayBox";
import DisplayBoxWithPicture from "./DisplayBoxWithPicture";

// Importing DropDownMenu and Planet components
import DropDownMenu from "./DropDownMenu";
import Planet from "./Planet";

// Importing Shop and BuildingGrid components
import Shopbar from "./ShopBar";
import BuildingGrid from "./BuildingGrid";

// Importing AttackMap
import AttackMap from "./AttackMap";

// Importing OpponentInfo
import OpponentInfo from "./OpponentInfo";

// Importing SettlementAndPlanetMenu
import SettlementAndPlanetMenu from "./SettlementAndPlanetMenu";

// Importing SpaceShip component
import SpaceShip from "./SpaceShipsList";

// Importing SendingTroops
import SendingTroops from "./SendingTroops";

// Importing CombatView
import CombatView from "./CombatView";

// Importing Tutorial
import {Tutorial, TutorialSwitch} from "./Tutorial";

// Importing CSS styles
import "../styles/App.css";

// Importing images
import attackIcon from "../assets/attackIcon.png";
import returnIcon from "../assets/returnIcon.png";
import profileIcon from "../assets/profileIcon.png";
import hammer from "../assets/hammer.png";
import spaceFood from "../assets/spaceFood.png";
import gun from "../assets/gun.png";
import planet from "../assets/planet.png";
import shopIcon from "../assets/shopIcon.png";
import planetMenuIcon from "../assets/PlanetMenuIcon.png";

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

// App component definition
function Game() {
  const [user, setUser] = useState("");
  const [race, setRace] = useState("");
  const [buildingMaterials, setBuildingMaterials] = useState("");
  const [ration, setRation] = useState("");
  const [attackPower, setAttackPower] = useState("0");
  const [planetName, setPlanetName] = useState("");

  const [settlementNumber, setSettlementNumber] = useState(0);
  const [planetNumber, setPlanetNumber] = useState(() => {
    const savedPlanetNumber = localStorage.getItem('planetNumber');
    return savedPlanetNumber !== null ? Number(savedPlanetNumber) : 0;
  });
  const [activeSettlement, setActiveSettlement] = useState([false, false, false]);
  const [rerender, setRerender] = useState(0);
  const [planetX, setPlanetX] = useState(0);
  const [planetY, setPlanetY] = useState(0);

  const handlePlanetNumber = (number: number) => {
    setPlanetNumber(number);
  };

  const handleSettlementNumber = (number: number) => {
    setSettlementNumber(number);
  }

  const setActiveSettlements = (settlements: boolean[]) => {
    setActiveSettlement(settlements);
  }

  const handleRerender = () => {
    setRerender(rerender + 1);
  }

  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/user`, {
        withCredentials: true,
      });
      const response2 = await axios.get(`${API_URL}/planet`, {
        params: { planet_number: planetNumber },
        withCredentials: true,
      });
      setUser(response.data.user_name);
      setRace(response.data.race_name ? response.data.race_name : "no race");
      setBuildingMaterials(response2.data.resources.building_materials);
      setRation(response2.data.resources.rations);
      setAttackPower(response2.data.resources.attack_power);
      setPlanetName(response2.data.planet_name)
      setPlanetX(response2.data.coordinates.planet_x);
      setPlanetY(response2.data.coordinates.planet_y);
    })();
  }, [rerender, planetName]);

  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/planet`, { 
        params: { planet_number: planetNumber, include_settlements: true },
        withCredentials: true 
      });
      setActiveSettlements(response.data.settlements);
      
      if (response.data.length > 1) {
        setSecondSettlementUnlocked(true);
      }
      else
        setSecondSettlementUnlocked(false);
    if (response.data["settlements"].length > 2) {
      setThirdSettlementUnlocked(true);
    }
    else
      setThirdSettlementUnlocked(false);

    updateValues(response.data["planet_name"]);
  }
  )();
  localStorage.setItem("planetNumber", planetNumber.toString());
}, [planetNumber, planetName, setPlanetName]);


  /*
    Updates all the planet stats every 5 seconds

    :planet_name: Name of the planet to be updated
  */
  const updateValues = (planet_name: string) => {
    if (planet_name !== ""){
      (async () => {
        const response = await axios.get(`${API_URL}/user`, {
          withCredentials: true,
        });
        /*
        const response2 = await axios.get(`${API_URL}/race`, {
          withCredentials: true,
        });*/
        const response3 = await axios.get(`${API_URL}/planet`, {
        params: { planet_number: planetNumber, include_settlements: true },
        withCredentials: true
        });

        setUser(response.data.user_name);
        // setRace(response2.data);

        setBuildingMaterials(response3.data.resources.building_materials);
        setRation(response3.data.resources.rations);
        setAttackPower(response3.data.resources.attack_power);
        setPlanetName(response3.data.planet_name)

      })();
    }
}

  // Use-effect that updates every 5 seconds
  const TIME = 5000;
  useEffect(() => {
  const interval = setInterval(() => {
    updateValues(planetName);
  }, TIME);


  return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
  }, [planetName, setPlanetName])

  // Define state variable menuVisible and its setter function setMenuVisible using useState hook
  const [menuVisible, setMenuVisible] = useState(false);

  // Define state variable shopVisible and its setter function setShopVisible using useState hook
  const [shopVisible, setShopVisible] = useState(false);

  // Define state variable buildMode and its setter function setBuildMode using useState hook
  const [buildMode, setBuildMode] = useState(false);

  // Define state variable structureType and its setter function setStructureType using useState hook
  const [structureType, setStructureType] = useState(0);

  // Define state variable structureLevel and its setter function setStructureLevel using useState hook
  const [structureLevel, setStructureLevel] = useState(0);

  // Define state variable settlementView and its setter function setSettlementView using useState hook
  const [settlementView, setSettlementView] = useState(false);

  // Define state variable attackMapView and its setter function setAttackMapView using useState hook
  const [attackMapView, setAttackMapView] = useState(false);

  // Define state variable showOpponent and its setter function setShowOpponent using useState hook
  const [showOpponent, setShowOpponent] = useState(false);

  // Define state variable settlementPlanetMenuView and its setter function setSettlementPlanetMenuView using useState hook
  const [settlementPlanetMenuView, setSettlementPlanetMenuView] =
    useState(false);

  // Define state variable secondSettlementUnlocked and its setter function setSecondSettlementUnlocked using useState hook
  const [secondSettlementUnlocked, setSecondSettlementUnlocked] =
    useState(false);

  // Define state variable thirdSettlementUnlocked and its setter function setThirdSettlementUnlocked using useState hook
  const [thirdSettlementUnlocked, setThirdSettlementUnlocked] = useState(false);

  // Define state variable sendingTroops and its setter function setSendingTroops using useState hook
  const [sendingTroops, setSendingTroops] = useState(false);

  // Define state variable sendingTroopsView and its setter function setSendingTroopsView using useState hook
  const [sendingTroopsView, setSendingTroopsView] = useState(false);

  // Define state variable inCombat and its setter function setInCombat using useState hook
  const [inCombat, setInCombat] = useState(false);


  // Gets the selected opponents x and y
  const [opponentXY, setOpponentXY] = useState( {x: 0, y: 0})


  const change_position = (x: number, y: number) =>{
    setOpponentXY({x: x, y:y})
  }

  // Define state variable showTutorials and its setter function set setShowTutorials using useState hook
  const [showTutorials, setShowTutorials] = useState(true);

  // Define state variable tutorialVisibilityList and its setter function setTutorialVisibilityList using useState hook
  const [tutorialVisibilityList, setTutorialVisibilityList] = useState([true, true, true, true, true, true, true, true]);


  // Function to toggle menu visibility
  const toggleMenu = () => {
    setMenuVisible(!menuVisible); // Toggle the menuVisible state
    hideTutorial(1);
  };

  // Function to toggle shop visibility
  const toggleShop = () => {
    setShopVisible(!shopVisible);
    hideTutorial(4);
  };

  // Function to toggle buildMode
  const toggleBuild = () => {
    setBuildMode(!buildMode);
  };

  // Function to toggle settlementView
  const toggleSettlementView = () => {
    setSettlementView(!settlementView);
    setSettlementPlanetMenuView(false);
    hideTutorial(3);
  };

  // Function to toggle attackMapView
  const toggleAttackMapView = () => {
    if (!sendingTroops) {
      setAttackMapView(!attackMapView);
      setSettlementPlanetMenuView(false);
    } else {
      toggleSendingTroopsView();
    }
    hideTutorial(0);
  };

  // Function to toggle opponent visibility
  const toggleOpponent = () => {
    setShowOpponent(!showOpponent);
  };

  // Function to return to planet view
  const returnToPlanet = () => {
    setShowOpponent(false);
    setAttackMapView(false);
    setSendingTroopsView(false);
    setSendingTroops(false)
    setInCombat(false);
  };

  const [opponentPlanetPos, setOpponentPlanetPos] = useState([0, 0]);
  const handlePlanetPosition = (posX: number, posY: number) => {
    setOpponentPlanetPos([posX, posY]);
  }

  // Function to toggle planet and settlement menu view
  const togglesettlementPlanetMenuView = () => {
    setSettlementPlanetMenuView(!settlementPlanetMenuView);
    hideTutorial(2);
  };

  const unlockSecondSettlement = () => {
    setSecondSettlementUnlocked(true);
  };

  const unlockThirdSettlement = () => {
    setThirdSettlementUnlocked(true);
  };

  // Function to toggle sendingTroopsView view visibility
  const toggleSendingTroopsView = () => {
    setSendingTroopsView(!sendingTroopsView);
    setSendingTroops(true);
    setAttackMapView(false);
    setShowOpponent(false);
  };

  // Function to toggle combat view visibility
  const toggleInCombat = () => {
    setInCombat(!inCombat);
    setSendingTroopsView(false);
    setSendingTroops(false);
  };

  // Function to toggle all tutorial visibility
  const toggleTutorials = () => {
    if (!showTutorials){
      const temp = tutorialVisibilityList.map((c, index) => {return true;     
      });
      setTutorialVisibilityList(temp);
    }
    setShowTutorials(!showTutorials);
  };

  // Function to hide tutorial with a given index
  const hideTutorial = (i: number) => {
    const temp = tutorialVisibilityList.map((c, index) => {
      if (index === i) {
        return false;
      } else {
        return c;
      }
    });
    setTutorialVisibilityList(temp);
  };

  // Render JSX
  return (
    <>
      {/* Display attack button when not in settlementView, attackMapView or sendingTroopsView */}
      {!(settlementView || attackMapView || sendingTroopsView || inCombat) && (
        <div className="attackButton">
          <ButtonWithPicture
            imageUrl={attackIcon}
            width={100}
            height={100}
            event={toggleAttackMapView}
          ></ButtonWithPicture>
        </div>
      )}

      {/*Display return button when in settlementView*/}
      {settlementView && (
        <div className="returnButton">
          <ButtonWithPicture
            imageUrl={returnIcon}
            width={100}
            height={100}
            event={toggleSettlementView}
          ></ButtonWithPicture>
        </div>
      )}

      {/* Display profile button with onClick event to toggle menu visibility */}
      <div className="profileButton">
        <ButtonWithPicture
          imageUrl={profileIcon}
          width={70}
          height={70}
          event={toggleMenu} // Use onClick event to toggle menu visibility
        ></ButtonWithPicture>
      </div>

      {/* Display user name */}
      <div className="displayBox1">
        <DisplayBox value={user} width={150} height={15}></DisplayBox>
      </div>

      {/* Display race name */}
      <div className="displayBox2">
        <DisplayBox value={race} width={150} height={15}></DisplayBox>
      </div>

      {/* Display building resource */}
      <div className="displayBoxWithPic">
        <DisplayBoxWithPicture
          value={buildingMaterials}
          width={100}
          height={15}
          imgUrl={hammer}
        ></DisplayBoxWithPicture>
      </div>

      {/* Display food resource */}
      <div className="displayBoxWithPic2">
        <DisplayBoxWithPicture
          value={ration}
          width={100}
          height={15}
          imgUrl={spaceFood}
        ></DisplayBoxWithPicture>
      </div>

      {/* Display troops */}
      <div className="displayBoxWithPic3">
        <DisplayBoxWithPicture
          value={attackPower}
          width={100}
          height={15}
          imgUrl={gun}
        ></DisplayBoxWithPicture>
      </div>

      {/* Conditionally render the dropdown menu based on menuVisible state */}
      <div className="content">
        {menuVisible && (
          <div className="dropdownMenu">
            <DropDownMenu></DropDownMenu>
          </div>
        )}
      </div>

      {/* Display SpaceShip component */}
      <div className="spaceShip">
        <SpaceShip></SpaceShip>
      </div>

      {/* Display planet when not in settlementView, attackMapView, sendingTroopsView */}
      {!(settlementView || attackMapView || sendingTroopsView || inCombat) && (
        <div className="planet">
          <Planet
            planetName={planetName}
            imgUrl={planet}
            event={toggleSettlementView}
            secondSettlementUnlocked={secondSettlementUnlocked}
            thirdSettlementUnlocked={thirdSettlementUnlocked}
            onSettlementNumberChange={handleSettlementNumber}
            activeSettlements={activeSettlement}
          ></Planet>
        </div>
      )}

      {/* Display shop when in settlementView*/}
      {settlementView && (
        <div className="shop">
          <div className="shopButton">
            <ButtonWithPicture
              imageUrl={shopIcon}
              width={70}
              height={70}
              event={toggleShop}
            ></ButtonWithPicture>
          </div>

          <div>
            <Shopbar
              show={shopVisible}
              buildMode={buildMode}
              toggleBuild={toggleBuild}
              structureType={structureType}
              setStructureType={setStructureType}
              building_materials={parseInt(buildingMaterials)}
            ></Shopbar>
          </div>
        </div>
      )}

      {/* Display BuildingGrid when in settlementView*/}
      {settlementView && (
        <div>
          <BuildingGrid
            onDelete={toggleMenu}
            onUpgrade={toggleMenu}
            buildMode={buildMode}
            toggleBuildMode={toggleBuild}
            structureType={structureType}
            setStructureType={setStructureType}
            structureLevel={structureLevel}
            setStructureLevel={setStructureLevel}
            settlementNumber={settlementNumber}
            planetNumber={planetNumber}
            rerender={handleRerender}
          ></BuildingGrid>
        </div>
      )}

      {/* Display AttackMap when in attackMapView */}
      {attackMapView && (
        <>
          <AttackMap
            OpponentToggle={toggleOpponent}
            handlePlanetPosition={handlePlanetPosition}
            planetX={planetX}
            planetY={planetY}
          ></AttackMap>
          <div className="returnToPlannetButton">
            <ButtonWithPicture
              imageUrl={returnIcon}
              width={100}
              height={100}
              event={returnToPlanet}
            ></ButtonWithPicture>
          </div>
        </>
      )}
      {/* Show opponent info when selected */}
      {attackMapView && showOpponent && (
        <OpponentInfo
          planet_posX={opponentPlanetPos[0]}
          planet_posY={opponentPlanetPos[1]}
        ></OpponentInfo>
      )}

      {/* Display send troop button when in attackMapView and opponent is shown */}
      {attackMapView && showOpponent && (
        <div className="sendTroopButton">
          <ButtonWithPicture
            imageUrl={attackIcon}
            width={100}
            height={100}
            event={toggleSendingTroopsView}
          ></ButtonWithPicture>
        </div>
      )}

      {/* Display settlement and planet menu button when not in settlementView, attackMapView or sendingTroopsView*/}
      {!(settlementView || attackMapView || sendingTroopsView || inCombat) && (
        <div className="settlementAndPlanetMenuButton">
          <ButtonWithPicture
            imageUrl={planetMenuIcon}
            width={100}
            height={100}
            event={togglesettlementPlanetMenuView}
          ></ButtonWithPicture>
        </div>
      )}

      {/* Display settlement and planet menu when in settlementPlanetMenuView */}
      {settlementPlanetMenuView && (
        <SettlementAndPlanetMenu
          unlockSecondSettlement={unlockSecondSettlement}
          unlockThirdSettlement={unlockThirdSettlement}
          secondSettlementBought={secondSettlementUnlocked}
          thirdSettlementBought={thirdSettlementUnlocked}
          onPlanetNumberChange={handlePlanetNumber}
          planetNumber={planetNumber}
          toggleView={togglesettlementPlanetMenuView}
          building_materials={parseInt(buildingMaterials)}
        ></SettlementAndPlanetMenu>
      )}

      {/* Display the sending troops screen when in sendingTroopsView */}
      {sendingTroopsView && (
        <>
          <SendingTroops
            toggleCombatMode={toggleInCombat}
            playerPlanetName={planetName}
            rerender={handleRerender}
            opponentPlanetPos={opponentPlanetPos}
            toggleSendingTroops={returnToPlanet}
          ></SendingTroops>

          <div className="returnToPlannetButton">
            <ButtonWithPicture
              imageUrl={returnIcon}
              width={100}
              height={100}
              event={returnToPlanet}
            ></ButtonWithPicture>
          </div>
        </>
      )}

      {/* Show opponent info when the sending troops or combat view */}
      {(sendingTroopsView || inCombat) && (
        <OpponentInfo
          planet_posX={opponentPlanetPos[0]}
          planet_posY={opponentPlanetPos[1]}
        ></OpponentInfo>
      )}

      {/* Display the combat screen when in combat view */}
      {inCombat && (
        <>
          <CombatView
            opponentPlanetPos={opponentPlanetPos}
            playerPlanetName={planetName}
            rerender={handleRerender}
            toggleCombat= {toggleInCombat}
          ></CombatView>

          <div className="returnToPlannetButton">
            <ButtonWithPicture
              imageUrl={returnIcon}
              width={100}
              height={100}
              event={returnToPlanet}
            ></ButtonWithPicture>
          </div>
        </>
      )}

      {/* conditionally Display tutorials */}
      {showTutorials &&
        !(settlementView || attackMapView || sendingTroopsView || inCombat) && (
          <>
            {tutorialVisibilityList[0] && (
              <Tutorial
                className="AttackButtonTutorial"
                hideTutorial={hideTutorial}
                index={0}
              >
                Use the attack map to scout other planets and send your troops
                to steal resources.
              </Tutorial>
            )}
            {tutorialVisibilityList[1] && (
              <Tutorial
                className="ProfileTutorial"
                hideTutorial={hideTutorial}
                index={1}
              >
                Go to your profile to join a race and interact with them, view
                your achievements or log out.
              </Tutorial>
            )}
            {tutorialVisibilityList[2] && (
              <Tutorial
                className="SettlementAndPlanetMenuTutorial"
                hideTutorial={hideTutorial}
                index={2}
              >
                This menu allows you to buy new planets and settlements and
                switch to another planet you own.
              </Tutorial>
            )}
            {tutorialVisibilityList[3] && (
              <Tutorial
                className="SettlementTutorial"
                hideTutorial={hideTutorial}
                index={3}
              >
                Click on a settlement to start building structures that generate
                resources and train troops.
              </Tutorial>
            )}
            {tutorialVisibilityList[7] && (
              <Tutorial
                className="TutorialSwitchTutorial"
                hideTutorial={hideTutorial}
                index={7}
              >
                Switch off/on all tutorials at any time!
              </Tutorial>
            )}
          </>
        )}

      {showTutorials && settlementView && (
        <>
          {tutorialVisibilityList[4] && (
            <Tutorial
              className="ShopTutorial"
              hideTutorial={hideTutorial}
              index={4}
            >
              Use the shop to select a structure, then click an empty grid in
              your settlement to start building it.
            </Tutorial>
          )}
        </>
      )}

      {showTutorials && inCombat && (
        <>
          {tutorialVisibilityList[5] && (
            <Tutorial
              className="CombatAttackButtonTutorial"
              hideTutorial={hideTutorial}
              index={5}
            >
              Once you've selected a unit type to send into battle, press the
              attack button to simulate one combat round.
            </Tutorial>
          )}
          {tutorialVisibilityList[6] && (
            <Tutorial
              className="AutoPlayButtonTutorial"
              hideTutorial={hideTutorial}
              index={6}
            >
              The autoplay button will coninuously simulate combat rounds until
              combat is over.
            </Tutorial>
          )}
        </>
      )}

      {/* switch to turn off/on all tutorials */}
      {!(settlementView || attackMapView || sendingTroopsView || inCombat) && (
        <TutorialSwitch toggleTutorials={toggleTutorials}></TutorialSwitch>
      )}
    </>
  );
}

// Export Game component
export default Game;
