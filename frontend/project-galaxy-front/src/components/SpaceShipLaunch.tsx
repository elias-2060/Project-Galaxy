import React, {useState, ChangeEvent, FormEvent, useEffect} from 'react';
import "../styles/SpaceShipLaunch.css";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

interface Props {
    onLaunch: () => void;
    planetNr: number;
    settlementNr: number;
    posX: number;
    posY: number;
  }

const LaunchSpaceship: React.FC<Props> = (
    {
      onLaunch,
      planetNr,
      settlementNr,
      posX,
      posY
  }
  ) => {
  const [planet, setPlanet] = useState<string>('');
  const [transportType, setTransportType] = useState<string>('');
  const [amount, setAmount] = useState<number>(0);
  const [soldierType, setSoldierType] = useState<string>('');
  const [planetList, setPlanetList] = useState([]);
  const [rations, setRations] = useState(0);
  const [buildingMaterials, setBuildingMaterials] = useState(0);
  const [shipPresent, setShipPresent] = useState(true);
  const [unitCapacity, setUnitCapacity] = useState(0);
  const [resourceCapacity, setResourceCapacity] = useState(0);
  const [spaceCommandoAmount, setSpaceCommandoAmount] = useState(0);
  const [spaceMarineAmount, setSpaceMarineAmount] = useState(0);
  const [spaceDroneAmount, setSpaceDroneAmount] = useState(0);
    const [maxAmount, setMaxAmount] = useState(0);
  useEffect(() => {
  (async () => {
    const response = await axios.get(`${API_URL}/building/spaceport`, {
      params:
          {
            planet_number: planetNr,
            settlement_number: settlementNr,
            pos_x: posX,
            pos_y: posY,
          },
      withCredentials: true });
    setPlanetList(response.data.planet_names);
    setRations(response.data.rations);
    setBuildingMaterials(response.data.building_materials);
    setShipPresent(response.data.ship_present);
    setUnitCapacity(response.data.unit_capacity);
    setResourceCapacity(response.data.resource_capacity);
    setSpaceMarineAmount(response.data.space_marine_nr);
    setSpaceCommandoAmount(response.data.space_commando_nr);
    setSpaceDroneAmount(response.data.space_drone_nr);
  })();
  }, []);

  const handlePlanetChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setPlanet(e.target.value);
  }

  const handleLaunch = async () => {
    const response = await axios.post(`${API_URL}/building/spaceport`, {
      params: {
          planet_number: planetNr,
          settlement_number: settlementNr,
          pos_x: posX,
          pos_y: posY,
          planet_name: planet,
          unit_type: soldierType,
          amount: amount,
          transport_type: transportType,
      }
    }, {
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });
    if (response.data === "Spaceship successfully sent"){
        onLaunch();
    }
  }
  const handleTroopTypeChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setTransportType(e.target.value);
    // Reset soldierType when troop type changes
    if (e.target.value !== 'soldiers') {
      setSoldierType('');
    }
  };


  const handleCapacityChange = () => {
      let capacity = resourceCapacity;
      console.log("transport_type: ", transportType);
      // If it wants to send soldiers:
      if (transportType === "soldiers"){
          // Get the maximum number of soldiers you can send when a type is selected
          capacity = unitCapacity
          if (soldierType === "Space-Marine"){
              capacity = Math.floor(capacity / 3);
              capacity = Math.min(capacity, spaceMarineAmount);
          }
          else if (soldierType === "Space-Commando"){
              capacity = Math.floor(capacity / 6);
              capacity = Math.min(capacity, spaceCommandoAmount);
          }
          else if (soldierType === "Space-Drone"){
              capacity = Math.floor(capacity / 20);
              capacity = Math.min(capacity, spaceDroneAmount);
          }
      }
      else if (transportType === "rations"){
          setMaxAmount(Math.min(amount, rations))
      }
      else if (transportType === "materials"){
          setMaxAmount(Math.min(amount, buildingMaterials))
      }
      setMaxAmount(capacity);
  }

  const handleAmountChange = (e: ChangeEvent<HTMLInputElement>) => {
      // Calculate the new capacity:
      handleCapacityChange();

      // If the value is <= the max, return the value, else return the max
      if (parseInt(e.target.value) <= maxAmount){
        setAmount(parseInt(e.target.value));
      }
      else{
          setAmount(resourceCapacity);
      }
  };
  const isButtonDisabled = () => {
      if (planet === "" || transportType === "" || !shipPresent){
          return true
      }
      if (transportType === "soldiers" && soldierType === ""){
          return true;
      }
      return (amount <= 0);
  }

  const handleSoldierTypeChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setSoldierType(e.target.value);
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Here you can send the troop data to your backend or handle it however you like
    console.log('Sending troops:', { planet, troopType: transportType, amount, soldierType });
  };

  return (
    <form className="SendTroops" onSubmit={handleSubmit}>
      <div>
        <label htmlFor="planet">Select Planet:</label>
        <select id="planet" value={planet} onChange={handlePlanetChange}>
            <option value="">Select a planet</option>
            {planetList.map((planetItem, index) => (
                <option key={index} value={planetItem["planet_name"]}>
                    {planetItem["planet_name"]}
                </option>
                ))}
        </select>
      </div>
      <div>
        <label htmlFor="troopType">Select Type:</label>
        <select id="troopType" value={transportType} onChange={handleTroopTypeChange}>
          <option value="">Select Type</option>
          <option value="materials">Building Materials</option>
          <option value="rations">Rations</option>
          <option value="soldiers">Soldiers</option>
        </select>
      </div>
      {transportType === 'soldiers' && (
        <div>
          <label htmlFor="soldierType">Select Soldier Type:</label>
          <select id="soldierType" value={soldierType} onChange={handleSoldierTypeChange}>
            <option value="">Select Soldier Type</option>
              {spaceMarineAmount > 0 && <option value="Space-Marine">Space-Marine</option>}
              {spaceCommandoAmount > 0 && <option value="Space-Commando">Space-Commando</option>}
              {spaceDroneAmount > 0 && <option value="Space-Drone">Space-Drone</option>}
          </select>
        </div>
      )}
      <div>
        <label htmlFor="amount">Enter Amount:</label>
        <input
          type="number"
          id="amount"
          value={amount}
          onChange={handleAmountChange}
          placeholder="Enter amount"
          min="1"
          max={maxAmount.toString()}
          required
        />
      </div>
      <button type="submit"
              onClick={handleLaunch}
              disabled={isButtonDisabled()}
      >Send SpaceShip
      </button>
    </form>
  );
};

export default LaunchSpaceship;