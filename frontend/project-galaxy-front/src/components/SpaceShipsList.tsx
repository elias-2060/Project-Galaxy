import React, {useEffect, useState} from 'react';
import { ButtonWithTextAndImg } from "./Buttons";
import "../styles/SpaceShipsLists.css";
import spaceshipImg from "../assets/spaceship.png";

interface Spaceship {
  id: number;
  name: string;
  type: string;
  direction: 'incoming' | 'outgoing';
  arrivalTime: number; // Timestamp of arrival in milliseconds
  departureTime: number; // Timestamp of departure in milliseconds
}

const SpaceshipList: React.FC = () => {
  const [showList, setShowList] = useState(false);


  // Add here the spaceships from the database, for now we will use a hardcoded list
  const spaceships: Spaceship[] = [
    { id: 1, name: 'Ship 1', type: 'Materials', direction: 'incoming', arrivalTime: Date.now() + 5000, departureTime: Date.now() + 10000 },
    { id: 2, name: 'Ship 2', type: 'Food', direction: 'outgoing', arrivalTime: Date.now() + 15000, departureTime: Date.now() + 20000 },
    { id: 3, name: 'Ship 3', type: 'Soldiers', direction: 'outgoing', arrivalTime: Date.now() + 15000, departureTime: Date.now() + 20000 },
  ];

  const formatTime = (time: number): string => {
    const seconds = Math.floor((time % (1000 * 60)) / 1000);
    const minutes = Math.floor((time % (1000 * 60 * 60)) / (1000 * 60));
    const hours = Math.floor((time % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleButtonClick = () => {
    setShowList(!showList);
  };

  return (
    <>
    <div className='spaceshipButton'>
      <ButtonWithTextAndImg  imgUrl={spaceshipImg} width={150} height={35} value='Spaceships' event={handleButtonClick}></ButtonWithTextAndImg>
    </div>
      {showList && (
        <div className='spaceshipsContent'>
          <h2>Ingoing Spaceships</h2>
          <ul>
            {spaceships
              .filter(spaceship => spaceship.direction === 'incoming')
              .map(spaceship => (
                <li key={spaceship.id}>
                  {spaceship.name} - {spaceship.type} (Arrival in: {formatTime(spaceship.arrivalTime - Date.now())})
                </li>
              ))}
          </ul>
          <h2>Outgoing Spaceships</h2>
          <ul>
            {spaceships
              .filter(spaceship => spaceship.direction === 'outgoing')
              .map(spaceship => (
                <li key={spaceship.id}>
                  {spaceship.name} - {spaceship.type} (Departure in: {formatTime(spaceship.departureTime - Date.now())})
                </li>
              ))}
          </ul>
        </div>
      )}
      </>
  );
};

export default SpaceshipList;