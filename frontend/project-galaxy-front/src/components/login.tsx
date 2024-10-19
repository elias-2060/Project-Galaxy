import React from 'react'
import '../styles/LoginRegister.css'
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

/**
 * Component for user login.
 * 
 * This component displays a form where users can log in by providing their username and password.
 * When the form is submitted, a POST request is sent to the server with the user's login information.
 */
function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [resp, setResp] = useState("")
    const [user, setUser] = useState("");

    useEffect(() => {
        const respStorage = localStorage.getItem('RESPONSE');
        if (respStorage) {
            setResp(respStorage)
            localStorage.removeItem('RESPONSE')
        }
    }, [])

    /**
     * Handles the submission of the login form.
     * Sends a POST request to the server with the provided username and password.
     */
    const submitHandler = async () => {
        await axios.post(`${API_URL}/account/login`, {
            user_name: username,
            password: password,
        }, {
            headers: {
                'Content-Type': 'application/json',
            },
            withCredentials: true
        }).then(response => {
            setResp(response.data)
            if (response.data === "Successfully logged in") {
                setUser(username)
                window.location.reload();
            }
            else {
                localStorage.setItem('RESPONSE', response.data)
                window.location.reload();
            }
        });
    };


    return (
        <>
            {user ? (
                <div>
                    {window.location.href = "/game"}
                </div>
            ) : (

                <div className="background">
                    <div className="container">
                        <div className="header">
                            <div className="text">Sign in</div>
                            <div className="underline"></div>
                        </div>
                        <div>
                            <div>
                                <input
                                    className="input"
                                    type="text"
                                    placeholder="Username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                            <div>
                                <input
                                    className="input"
                                    type="password"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="submits">
                            <button type="submit" className="submit" onClick={submitHandler}>
                                Sign In
                            </button>
                            <div className="submit">
                                <Link to="/">Sign Up</Link>
                            </div>
                        </div>
                        <div>
                            {resp}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}


export default Login;
