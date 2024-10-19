import React from 'react'
import { Routes, Route } from "react-router-dom";
import Register from './register';
import Login from './login';
import Game from './Game';

function App() {
  return (
      <Routes>
        <Route path="login" element={<Login />} />
        <Route path="/" element={<Register />} />
        <Route path="game" element={<Game />} />
      </Routes>
  );
}


export default App;
