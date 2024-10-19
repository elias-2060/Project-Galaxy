// Importing ButtonWithText component from "./Buttons"
import { useState, useEffect } from "react";
import { ButtonWithText } from "./Buttons";

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

// Defining SettingContent component
const SettingContent = () => {

  const logout = async () => {
      await axios.post(`${API_URL}/account/logout`, {}, {
          withCredentials: true
      }).then(response =>{
        localStorage.removeItem('USERNAME');
        localStorage.removeItem('planetNumber');
        window.location.href = "/login";
          
      });
    };
  
  // Rendering JSX for the SettingContent component
  return (
    <div className="settingBox">
      {/* Rendering ButtonWithText component for logging out */}
      <ButtonWithText width={200} height={50} value="Log out" event={logout}></ButtonWithText>
    </div>
  );
};

// Exporting SettingContent component
export default SettingContent;
