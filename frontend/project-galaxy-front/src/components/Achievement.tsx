import React, { useState } from 'react';
import '../styles/Achievement.css';
import imageSrc from "../assets/hammer.png";
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL

interface AchievementProps {
    id: string;
    title: string;
    reward: string;
    redeemState: string;
}

const Achievement: React.FC<AchievementProps> = ({ id, title, reward, redeemState }) => {
    const [redeemed, setRedeemed] = useState(false);

    const redeemAchievement = () => {
        setRedeemed(true);
        axios.post(`${API_URL}/achievement/redeem`, { achievement_id: id }, { withCredentials: true });
        // add here the reward to the player in the backend
    };

    if (redeemState === "redeemed") {
        console.log("achievement ", title, " already redeemed");
    }
    const state =
      redeemState === "redeemable"
        ? (
            redeemed
            ? "redeemed"
            : "redeemable"
        )
        : redeemState === "redeemed"
        ? "redeemed"
        : "not-redeemable";

    return (
        <button
            className={state}
            disabled={redeemState!=="redeemable" || redeemed}
            onClick={redeemAchievement}
        >
            <div>
                <span className="title">{title}</span>
                <div>
                    <span className="reward">{reward}</span>
                    <img src={imageSrc} alt="reward" className="image" />
                </div>
            </div>
        </button>
    );
};

export default Achievement;