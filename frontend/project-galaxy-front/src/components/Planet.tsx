// Importing CSS styles from "../styles/Planet.css"
import "../styles/Planet.css";

// Importing SegmentButton component from "./Buttons"
import { SegmentButton } from "./Buttons";

import segment from "../assets/segment.png";

// Defining interface for Props
interface Props {
  imgUrl: string;
  event: () => void;
  secondSettlementUnlocked: boolean;
  thirdSettlementUnlocked: boolean;
  onSettlementNumberChange: (settlementNumber: number) => void;
  activeSettlements: boolean[];
  planetName : string;
}

// Defining Planet component
const Planet: React.FC<Props> = ({
  imgUrl,
  event,
  secondSettlementUnlocked,
  thirdSettlementUnlocked,
  onSettlementNumberChange,
  activeSettlements,
  planetName,
}) => {
  // Rendering JSX for the planet component
  return (
    <>
      {/* Display the planet name */}
      <div className="planet-name">{planetName}</div>
      {/* Rendering planet image */}
      <img src={imgUrl}></img>
      {/* Rendering first segment button */}
      <div className="segment1">
        <SegmentButton
          width={50}
          height={80}
          imgUrl={segment}
          event={event}
          onSettlementNumberChange={onSettlementNumberChange}
          settlementNumber={0}
        ></SegmentButton>
      </div>
      {/* Rendering second segment button if it has been unlocked*/}
      {(secondSettlementUnlocked || activeSettlements[1]) && (
        <div className="segment2">
          <SegmentButton
            width={50}
            height={80}
            imgUrl={segment}
            event={event}
            onSettlementNumberChange={onSettlementNumberChange}
            settlementNumber={1}
          ></SegmentButton>
        </div>
      )}
      {/* Rendering third segment button if it has been unlocked*/}
      {(thirdSettlementUnlocked || activeSettlements[2]) && (
        <div className="segment3">
          <SegmentButton
            width={50}
            height={80}
            imgUrl={segment}
            event={event}
            onSettlementNumberChange={onSettlementNumberChange}
            settlementNumber={2}
          ></SegmentButton>
        </div>
      )}
    </>
  );
};

// Exporting Planet component
export default Planet;
