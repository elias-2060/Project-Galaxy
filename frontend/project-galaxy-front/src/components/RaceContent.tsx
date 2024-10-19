// Importing CSS styles from "../styles/RaceContent.css"
import "../styles/RaceContent.css";
import React, { useState } from "react";
import RaceCreateMenu from "./RaceCreateMenu";
import RaceJoinMenu from "./RaceJoinMenu";


// Importing ButtonWithText component from "./Buttons"
import { ButtonWithText } from "./Buttons";

// Defining RaceContent component
const RaceContent = () => {
  const [isCreateVisible, setIsCreateVisible] = useState(false); // State to track the visibility of create alliance
  const [isJoinVisible, setIsJoinVisible] = useState(false); // State to track the visibility of join alliance

// Function to toggle the visibility of SettingContent and hide others
  const toggleCreateVisibility = () => {
    setIsCreateVisible(!isCreateVisible);
    setIsJoinVisible(false);
};

// Function to toggle the visibility of ClanContent and hide others
  const toggleJoinVisibility = () => {
    setIsCreateVisible(false);
    setIsJoinVisible(!isJoinVisible);
  };
  // Rendering JSX for the RaceContent component
  return (<>
    <div className="raceContent">
      {/* Rendering ButtonWithText component for creating alliance */}
      <ButtonWithText width={200} height={50} value="Create Alliance" event={toggleCreateVisibility} />
      {/* Rendering ButtonWithText component for joining alliance */}
      <ButtonWithText width={200} height={50} value="Join Alliance" event={toggleJoinVisibility}/>
    </div>
    <div>
      {isCreateVisible && <RaceCreateMenu />}
      {isJoinVisible && <RaceJoinMenu />}
    </div>
    </>
  );
};

// Exporting RaceContent component
export default RaceContent;