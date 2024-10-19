// Importing the CSS file for styling purposes
import "../styles/RaceJoinMenu.css";
// Importing useState hook from React for managing component state
import { useState, useEffect } from "react";

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

// Functional component for creating a race menu
const RaceCreateMenu: React.FC = () => {
  const [races, setRaces] = useState<any[]>([]);
  const [racename, setRacename] = useState("");

  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/join_race`);
      setRaces(response.data);
    })();
  }, []);

  const join_race = async () => {
    const response = await axios.post(`${API_URL}/join_race`, {
      RaceName: racename,
    }, {
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });
    window.location.reload();
  }

  // list of alliances
  const alliances: { name: string; description: string }[] = [];
  for (let i = 0; i < races.length; i++) {
    alliances.push({ name: races[i], description: "Description" });
  }

  // State to keep track of selected alliance index
  const [selectedAllianceIndex, setSelectedAllianceIndex] = useState<
    number | null
  >(null);

  // Function to handle alliance selection
  const handleAllianceClick = (index: number) => {
    setSelectedAllianceIndex(index);
    setRacename(alliances[index].name);
  };

  return (
    // Container div with class name 'joinMenu'
    <div className="joinMenu">
      {/* Container div for scrollable list */}
      <div className="scrollableList">
        {/* Unordered list for displaying alliances */}
        <ul>
          {/* Mapping through the list of alliances to render each one */}
          {alliances.map((alliance, index) => (
            // List item representing each alliance
            <li
              key={index} // Unique key for React to efficiently manage list items
              className={`listItem ${
                // Conditionally applying 'selected' class if the alliance is selected
                selectedAllianceIndex === index ? "selected" : ""
                }`}
              onClick={() => handleAllianceClick(index)} // Handling click event for alliance selection
            >
              {/* Div for displaying alliance name */}
              <div className="allianceName">{alliance.name} </div>
              {/* Div for displaying alliance description */}
              <div className="allianceDescription">{alliance.description}</div>
            </li>
          ))}
        </ul>
      </div>
      {/* Button for joining the selected alliance, disabled if no alliance is selected */}
      <button className="joinButton" disabled={selectedAllianceIndex === null} onClick={join_race}>
        Join
      </button>
    </div>
  );
};

// Exporting the RaceCreateMenu component for use in other modules
export default RaceCreateMenu;