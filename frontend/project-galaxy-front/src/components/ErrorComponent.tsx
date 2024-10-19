// ErrorComponent.tsx

import React from 'react';
import '../styles/ErrorComponent.css'; // Import CSS file for styling

interface ErrorProps {
  message: string;
}

const ErrorComponent: React.FC<ErrorProps> = ({ message }) => {
  return (
    <div className="error-overlay">
      <div className="error-box">
        <p className="error-message">{message}</p>
      </div>
    </div>
  );
};

export default ErrorComponent;
