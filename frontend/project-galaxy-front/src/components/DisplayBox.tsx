// Importing CSS styles from "../styles/DisplayBox.css"
import "../styles/DisplayBox.css";

// Defining interface for Props
interface Props {
  value: string;
  width: number;
  height: number;
}

// Defining DisplayBox component
const DisplayBox: React.FC<Props> = ({ value, width, height }) => {
  // Setting style for the display box
  const style = {
    width: width,
    height: height,
  };

  // Returning JSX for the display box
  return (
    <div className="displayBox" style={style}>
      {value}
    </div>
  );
};

// Exporting DisplayBox component
export default DisplayBox;