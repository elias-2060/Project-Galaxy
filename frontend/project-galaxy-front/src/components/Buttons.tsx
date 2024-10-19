// Importing CSS styles from "../styles/Buttons.css"
import "../styles/Buttons.css";

// Defining interface for buttonProps
interface buttonProps {
  imageUrl: string;
  width: number;
  height: number;
  event?: () => void;
  disabled?: boolean;
}

// Defining interface for buttonProps2
interface buttonProps2 {
  value: string;
  width: number;
  height: number;
  event?: () => void
  disabled: boolean;
}

// Defining interface for buttonProps3
interface buttonProps3 {
  imgUrl: string;
  event?: () => void;
  width: number;
  height: number;
  onSettlementNumberChange?: (number: number) => void;
  settlementNumber: number;
}

// Defining interface for buttonProps4
interface buttonProps4 {
  imgUrl: string;
  value: string;
  width: number;
  height: number;
  event?: () => void;
}

// Defining ButtonWithPicture component
export const ButtonWithPicture: React.FC<buttonProps> = ({
  imageUrl,
  width,
  height,
  event,
  disabled,
}) => {
  // Setting button style with background image
  const buttonStyle = {
    backgroundImage: `url(${imageUrl})`,
    width: width,
    height: height,
  };

  // Returning button JSX
  return (
    <button
      type="button"
      style={buttonStyle}
      className="ButtonWithPicture"
      onClick={event}
      disabled={disabled}
    ></button>
  );
};

// Defining ButtonWithText component
export const ButtonWithText: React.FC<buttonProps2> = ({
  value,
  width,
  height,
  event,
    disabled,
}) => {
  // Setting button style
  const buttonStyle = {
    width: width,
    height: height,
  };

  // Returning button JSX with text
  return (
    <button
      type="button"
      style={buttonStyle}
      className="ButtonWithText"
      onClick={event}
      disabled={disabled}
    >
      {value}
    </button>
  );
};
// Defining ButtonWithText component
export const ButtonWithTextAndImg: React.FC<buttonProps4> = ({
  value,
  width,
  height,
  event,
  imgUrl
}) => {
  // Setting button style
  const buttonStyle = {
    width: width,
    height: height,
  };

  // Returning button JSX with text
  return (
    <button
      type="button"
      style={buttonStyle}
      className="ButtonWithText"
      onClick={event}
    >
      {value}
      <img src={imgUrl} alt="img" />
    </button>
  );
};

// Defining SegmentButton component
export const SegmentButton: React.FC<buttonProps3> = ({
  imgUrl,
  width,
  height,
  event,
  onSettlementNumberChange,
  settlementNumber,
}) => {
  // Setting button style with background image
  const buttonStyle = {
    backgroundImage: `url(${imgUrl})`,
    width: width,
    height: height,
  };

  // Returning button JSX
  return (
    <button
      type="button"
      style={buttonStyle}
      className="SegmentButton"
      onClick={() => {
        if (event) {
          event();
        }
        if (onSettlementNumberChange) {
          onSettlementNumberChange(settlementNumber);
        }
      }}
    ></button>
  );
};