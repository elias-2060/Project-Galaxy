// Importing the CSS file for styling purposes
import "../styles/RaceCreateMenu.css";

import React, { useState } from "react";

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

// Functional component for creating a race menu
const RaceCreateMenu = () => {
  const [raceName, setRaceName] = useState("");

  const submitHandler = async (e: React.FormEvent) => {
    e.preventDefault();
    await axios.post(`${API_URL}/race`, {
      Race: raceName,
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true
    });
    window.location.reload();
  };

  return (
    // Container div with class name 'createContent'
    <div className="createContent">
      {/* Form for creating a new alliance */}
      <form onSubmit={submitHandler}>
        {/* Label for alliance name input field */}
        <label htmlFor="allianceName">Alliance Name:</label>
        {/* Input field for entering alliance name */}
        <input type="text" id="allianceName" name="allianceName" onChange={(e) => setRaceName(e.target.value)} />
        {/* Label for alliance description input field */}
        <label htmlFor="allianceDescription">Alliance Description:</label>
        {/* Input field for entering alliance description */}
        <input
          type="text"
          id="allianceDescription"
          name="allianceDescription"
        />
        {/* Submit button to create the alliance */}
        <input type="submit" value="Create" />
      </form>
    </div>
  );
};

// Exporting the RaceCreateMenu component for use in other modules
export default RaceCreateMenu;