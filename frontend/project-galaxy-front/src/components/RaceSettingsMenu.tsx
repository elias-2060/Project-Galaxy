import React, { useState, useEffect } from 'react';
import '../styles/RaceSettingsMenu.css';

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL

interface MemberProps {
    name: string;
    role: string;
    lvl: number;
}

const Member = ({ name, role, lvl }: MemberProps) => {
    return (
        <div className='member'>
            <span>name: {name}</span>
            <span>role: {role}</span>
            <span>lvl: {lvl}</span>
        </div>
    );
}

const RaceSettingsPage: React.FC = () => {
    const [raceName, setRaceName] = useState("");
    const [raceLeader, setRaceLeader] = useState("");
    const [raceMembers, setRaceMembers] = useState<[]>([]);

    useEffect(() => {
        (async () => {
            const response = await axios.get(`${API_URL}/race_members`, { withCredentials: true });
            setRaceName(response.data.race_name);
            setRaceLeader(response.data.leader);
            setRaceMembers(response.data.members);
        })();
    }, []);

    const handleLeaveGuild =async () => {
        await axios.post(`${API_URL}/leave_race`, {}, { withCredentials: true });
        window.location.reload();
    };

    return (
        <div className='RaceSettingsMenu'>
            <button className='leave-button' onClick={handleLeaveGuild}>Leave Guild</button>
            <div className='settings-content'>
                <span className=''>Race: {raceName}</span>
                <p>Members:</p>
                <ul className='members-list'>
                    {raceMembers.map((member) => {
                        return <li> <Member name={member} role={raceLeader === member ? "leader" : "member"} lvl={1} /> </li>
                    })}
                </ul>
            </div>
        </div>
    );
};

export default RaceSettingsPage;