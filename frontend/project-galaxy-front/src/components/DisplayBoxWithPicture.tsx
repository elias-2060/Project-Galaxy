// Importing CSS styles from "../styles/DisplayBoxWithPicture.css"
import "../styles/DisplayBoxWithPicture.css";

// Defining interface for Props
interface Props {
  value: string;
  width: number;
  height: number;
  imgUrl: string;
}

// Defining DisplayBoxWithPicture component
const DisplayBoxWithPicture: React.FC<Props> = ({ value, width, height, imgUrl }) => {
  // Setting style for the display box
  const style = {
    width: width,
    height: height,
  };

  // Returning JSX for the display box with picture
  return (
    <div className="box" style={style}>
      {/* Rendering image */}
      <img
        className="icon"
        src={imgUrl}
      ></img>
      {/* Rendering value */}
      <span>{value}</span>
    </div>
  );
};

// Exporting DisplayBoxWithPicture component
export default DisplayBoxWithPicture;