import { useState } from "react";

import "../styles/Tutorial.css";

interface props {
  children: string;
  hideTutorial: (i: number) => void;
  index: number;
  className: string;
}

export const Tutorial = ({ children, hideTutorial, index, className }: props) => {
  const toggleVisibility = () => {
    hideTutorial(index);
  };
  return (
    <div className={"Tutorial " + className}>
      <button className="hideTutorialButton" onClick={toggleVisibility}>
        X
      </button>
      {children}
    </div>
  );
};

interface props2 {
  toggleTutorials: () => void;
}

export const TutorialSwitch = ({toggleTutorials}:props2) => {
  return (
    <>
      <label className="switch" >
        <input type="checkbox" onClick={toggleTutorials}></input>
        <span className="slider round"></span>
      </label>
    </>
  );
};

