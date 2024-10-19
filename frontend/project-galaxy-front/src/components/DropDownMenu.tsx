import "../styles/DropDownMenu.css";
import { ButtonWithPicture } from "./Buttons";
import React, { useEffect, useState } from "react";
import SettingContent from "./SettingContent";
import AchievementContent from "./AchievementContent";
import RaceContent from "./RaceContent";

import clan from "../assets/clan.png";
import setting from "../assets/setting.png";
import trophy from "../assets/trophy.png";

import axios from "axios";
import RaceBox from "./RaceBox";
import ChatBox from "./ChatBox";

const API_URL = import.meta.env.VITE_API_URL

type ContentType = JSX.Element | null; // Define the type for content

const DropDownMenu = () => {
  const [isSettingVisible, setIsSettingVisible] = useState(true); // State to track the visibility of SettingContent
  const [isClanVisible, setIsClanVisible] = useState(false); // State to track the visibility of ClanContent
  const [isTrophyVisible, setIsTrophyVisible] = useState(false); // State to track the visibility of TrophyContent

  const [menuClass, setMenuClass] = useState("");

  const [race, setRace] = useState("");
  useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/race`, { withCredentials: true });
      setRace(response.data);
    })()
  }, [])

  useEffect(() => {
    if (isClanVisible && race !== "no race") {
      setMenuClass("menu-expanded");
    } else {
      setMenuClass("menu");
    }
  }, [isClanVisible, race]);

  // Function to toggle the visibility of SettingContent and hide others
  const toggleSettingVisibility = () => {
    setIsSettingVisible(!isSettingVisible);
    setIsClanVisible(false);
    setIsTrophyVisible(false);
  };

  // Function to toggle the visibility of ClanContent and hide others
  const toggleClanVisibility = () => {
    setIsSettingVisible(false);
    setIsClanVisible(!isClanVisible);
    setIsTrophyVisible(false);
  };

  // Function to toggle the visibility of TrophyContent and hide others
  const toggleTrophyVisibility = () => {
    setIsSettingVisible(false);
    setIsClanVisible(false);
    setIsTrophyVisible(!isTrophyVisible);
  };

  return (
    <div className="menu">
      <div className="button-container">
        <ButtonWithPicture
          width={50}
          height={50}
          imageUrl={clan}
          event={toggleClanVisibility} // Pass the toggleClanVisibility function as a prop
        ></ButtonWithPicture>
        <ButtonWithPicture
          width={50}
          height={50}
          imageUrl={trophy}
          event={toggleTrophyVisibility} // Pass the toggleTrophyVisibility function as a prop
        ></ButtonWithPicture>
        <ButtonWithPicture
          width={50}
          height={50}
          imageUrl={setting}
          event={toggleSettingVisibility} // Pass the toggleSettingVisibility function as a prop
        ></ButtonWithPicture>
      </div>


      {isSettingVisible && <SettingContent />}
      {/* Render SettingContent if isSettingVisible is true */}
      {isTrophyVisible && <AchievementContent />}
      {/* Render TrophyContent if isTrophyVisible is true */}
      {isClanVisible && (race == "no race" ? <RaceContent /> : <RaceBox show />)}
      {/* Render ClanContent if isClanVisible is true */}
    </div>
  );
};

export default DropDownMenu;
