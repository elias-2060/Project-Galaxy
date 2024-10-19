import React, { useState, useEffect } from 'react';
import '../styles/ChatBox.css';
import '../styles/RaceBox.css';
import "../styles/Buttons.css";
import { ButtonWithPicture, ButtonWithText } from './Buttons';
import ChatBox from './ChatBox';
import RaceSettingsMenu from './RaceSettingsMenu';

import axios from 'axios';
import RaceContent from './RaceContent';

import returnButton from '../assets/returnIcon.png';

const API_URL = import.meta.env.VITE_API_URL


interface RaceBoxProps {
    show: boolean
}

const RaceBox = ({ show }: RaceBoxProps) => {
    const [isSettingVisible, setIsSettingVisible] = useState(false);
    const [race, setRace] = useState("");

    const toggleSettingVisibility = () => {
        setIsSettingVisible(!isSettingVisible);
    };

    useEffect(() => {
        (async () => {
            const response = await axios.get(`${API_URL}/race`, { withCredentials: true });
            setRace(response.data);
        }
        )()
    }, [])

    return (
        <div className='RaceBox'>
            <div>
                <div className='settings'>
                    {isSettingVisible ?
                        <ButtonWithPicture
                            width={50}
                            height={50}
                            imageUrl={returnButton}
                            event={toggleSettingVisibility}
                        ></ButtonWithPicture> :
                        <button className="clan-button" onClick={toggleSettingVisibility}>
                            {race}
                        </button>}
                </div>
                {isSettingVisible ? <RaceSettingsMenu /> : <ChatBox isRendered={!isSettingVisible}/>}
            </div>
        </div>
    );
};

export default RaceBox;;