import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../styles/LoginRegister.css';

const API_URL = import.meta.env.VITE_API_URL;

function Register() {
    const [username, setUsername] = useState('');
    //const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [planetName, setPlanetName] = useState('');
    const [errorResponse, setErrorResponse] = useState('');
    const [loginResponse, setLoginResponse] = useState('');

    useEffect(() => {
        const respStorage = localStorage.getItem('RESPONSE');
        if (respStorage) {
            setErrorResponse(respStorage);
            localStorage.removeItem('RESPONSE');
        }
    }, []);

    const submitHandler = async () => {
        await axios.post(`${API_URL}/account/register`, {
            user_name: username,
            password: password,
            planet_name: planetName,
        }, {
            headers: {
                'Content-Type': 'application/json',
            },
            withCredentials: true,
        }).then(response => {
            console.log(response.data);
            if (response.data === 'Successfully logged in') {
                setLoginResponse(response.data);
                window.location.reload();
            } else {
                setErrorResponse(response.data);
                localStorage.setItem('RESPONSE', response.data);
            }
        });
    };

    return (
        <>
            {loginResponse === 'Successfully logged in' ? (
                <div>
                    {window.location.href = '/game'}
                </div>
            ) : (
                <div className="background">
                    <div className="container">
                        <div className="header">
                            <div className="text">Sign up</div>
                        </div>
                        <div>
                            <div>
                                <input
                                    className="input"
                                    name="Username"
                                    type="text"
                                    placeholder="Username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                            <div>
                                <input
                                    className="input"
                                    name="Password"
                                    type="password"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                            <div>
                                <input
                                    className="input"
                                    name="ConfirmPassword"
                                    type="password"
                                    placeholder="Confirm Password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                />
                            </div>
                            <div> {/* Input field for planet name */}
                                <input
                                    className="input"
                                    name="PlanetName"
                                    type="text"
                                    placeholder="Planet Name"
                                    value={planetName}
                                    onChange={(e) => setPlanetName(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="submits">
                            <button type="submit" className="submit" onClick={submitHandler}>
                                Sign up
                            </button>
                            <div className="submit">
                                <Link to="/login">Sign in</Link>
                            </div>
                        </div>
                        <div>
                            {errorResponse}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

export default Register;