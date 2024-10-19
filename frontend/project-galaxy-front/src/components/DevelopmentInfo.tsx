import React, { useEffect, useState } from "react";
import "../styles/DevelopmentInfo.css";

interface DevelopmentTimerProps {
  startTime: number; // Start time in milliseconds
  totalTime: number; // Total time in milliseconds
  type: string;
}

const DevelopmentTimer: React.FC<DevelopmentTimerProps> = ({ startTime, totalTime, type }) => {
  var info;
  if (type == "inDevelopment") {
    info = "Time left for development:";
  } else if (type == "SpaceshipGone") {
    info = "Time left for spaceship to land:";
  } else if (type == "sendingTroops") {
    info = "Time left before troops arrive at enemy planet:";
  }
  const [timeLeft, setTimeLeft] = useState<number>(
    startTime ? Math.max(0, totalTime - (Date.now() - startTime)) : 0
  );

  useEffect(() => {
    const timer = setTimeout(() => {
      setTimeLeft((prevTimeLeft) => Math.max(0, prevTimeLeft - 1000)); // Decrease time by 1 second
    }, 1000);

    return () => clearTimeout(timer); // Clear the timer on unmount
  }, [timeLeft]);

  // Function to format time in hours, minutes, and seconds
  const formatTime = (time: number): string => {
    const hours = Math.floor(time / (1000 * 60 * 60));
    const minutes = Math.floor((time % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((time % (1000 * 60)) / 1000);
    return `${hours}h ${minutes}m ${seconds}s`;
  };

  return (
    <div className="timer-container" style={{ top: 0, left: -320 }}>
      {timeLeft > 0 && (
        <p className="timer-text">
          <p className="timer-text">
        {info}{" "}
        <span className="time">{formatTime(timeLeft)}</span>
      </p>
        </p>
      )}
    </div>
  );
};

export default DevelopmentTimer;