// Importing React library
import React, { useEffect, useState } from "react";

// Importing CSS styles for AchievementContent component
import "../styles/AchievementContent.css";

import Achievement from "./Achievement";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL

// AchievementContent component definition
const AchievementContent = () => {
  type Achievement = {
    achievement_id: string;
    achievement_name: string;
    achievement_description: string;
    reward: number;
    redeem_state: string;
  }
  const [achievements, setAchievements] = useState<Achievement[]>([]);

  const refreshAchievements = () => {
    axios.get(`${API_URL}/achievement/all`, { withCredentials: true }).then((response) => {
      setAchievements(response.data);
    })
  };

  useEffect(() => { refreshAchievements(); }, [])

  const [triggerAchievementRefresh, setTimeLeft] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => {
      console.log("rendered", triggerAchievementRefresh);
      setTimeLeft(!triggerAchievementRefresh); // Decrease time by 1 second
      refreshAchievements();
    }, 5000);
  }, [triggerAchievementRefresh]);

  return (
    // Container for achievement content
    <div className="achievementBox">
      {/* Container for scrollable content */}
      <div className="scrollable-content">
        {
          achievements.map((achievement) => (
            <Achievement
              id={achievement.achievement_id}
              title={achievement.achievement_description}
              reward={achievement.reward.toString()}
              redeemState={achievement.redeem_state}
            />)
          )
        }
      </div>
    </div>
  );
};

// Exporting AchievementContent component
export default AchievementContent;
