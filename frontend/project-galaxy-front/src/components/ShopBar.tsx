// Importing CSS styles for shop components
import "../styles/Shop.css";
import hammer from "../assets/hammer.png";
import barrack from "../assets/barrack.png";
import farm from "../assets/farm.png";
import mine from "../assets/mine.png";
import spaceship from "../assets/spaceship.png";
import warper from "../assets/warper.png"

// defining the interface for the shop item button
interface shopButtonProps {
  buildMode: boolean;
  toggleBuild: () => void;
  structureType: number;
  setStructureType: (structureName: number) => void;
  name: string;
  lvl: number;
  imageSrc: string;
  cost: number;
  imageBuilding: string;
  buildingMaterials: number;
}

// defining ShopItemButton component
export const ShopItemButton = ({
  buildMode,
  toggleBuild,
  structureType,
  setStructureType,
  name,
  lvl,
  imageSrc,
  cost,
  imageBuilding,
  buildingMaterials
}: shopButtonProps) => {
  let playerBuildMaterialCount = buildingMaterials; // connect this to the player's build material count
  // function to set the state of buildMode and the currently selected structure type
  const update = () => {
    if (!buildMode) {
      toggleBuild();
      setStructureType(lvl);
    } else if (lvl === structureType) {
      toggleBuild();
      setStructureType(0);
    } else {
      setStructureType(lvl);
    }
  };
  // Disable the button if playerBuildMaterialCount is less than the cost
  const isDisabled = playerBuildMaterialCount < cost;

  // Returning JSX for the shop item button
  return (
    <button
      className={
        structureType === lvl ? "shopItemButton selected" : "shopItemButton"
      }
      onClick={update}
      disabled={isDisabled} // Disable the button based on player's build material count
    >
      <div>
        <span><img src={imageBuilding}/></span>
        <span>{cost}  <img src={imageSrc} alt={name} /></span>
      </div>
    </button>
  );
};

// defining the interface for the shop bar
interface shopBarProps {
  show: boolean;
  buildMode: boolean;
  toggleBuild: () => void;
  structureType: number;
  setStructureType: (structureName: number) => void;
  building_materials: number;
}

// defining ShopBar component
const ShopBar = ({
  show,
  buildMode,
  toggleBuild,
  structureType,
  setStructureType,
  building_materials,
}: shopBarProps) => {
  // Returning JSX for the shop bar
  return (
    <div className={show ? "sideshop active" : "sideshop"}>
      <ul>
        <li>
          <p>Farm</p>
          <ShopItemButton
              buildMode={buildMode}
              toggleBuild={toggleBuild}
              structureType={structureType}
              setStructureType={setStructureType}
              name={"Farm"}
              lvl={4}
              imageSrc={hammer}
              cost={150}
              imageBuilding={farm}
              buildingMaterials={building_materials}
          />
        </li>
        <li>
          <p>Mine</p>
          <ShopItemButton
              buildMode={buildMode}
              toggleBuild={toggleBuild}
              structureType={structureType}
              setStructureType={setStructureType}
              name={"Mine"}
              lvl={3}
              imageSrc={hammer}
              cost={150}
              imageBuilding={mine}
              buildingMaterials={building_materials}
          />
        </li>
        <li>
          <p>Barrack</p>
          <ShopItemButton
              buildMode={buildMode}
              toggleBuild={toggleBuild}
              structureType={structureType}
              setStructureType={setStructureType}
              name={"Barrack"}
              lvl={2}
              imageSrc={hammer}
              cost={100}
              imageBuilding={barrack}
              buildingMaterials={building_materials}
          />
        </li>
        <li>
          <p>Spaceport</p>
          <ShopItemButton
              buildMode={buildMode}
              toggleBuild={toggleBuild}
              structureType={structureType}
              setStructureType={setStructureType}
              name={"Spaceport"}
              lvl={5}
              imageSrc={hammer}
              cost={5000}
              imageBuilding={spaceship}
              buildingMaterials={building_materials}
          />
        </li>
        <li>
          <p>Warper</p>
          <ShopItemButton
              buildMode={buildMode}
              toggleBuild={toggleBuild}
              structureType={structureType}
              setStructureType={setStructureType}
              name={"Warper"}
              lvl={6}
              imageSrc={hammer}
              cost={1500}
              imageBuilding={warper}
              buildingMaterials={building_materials}
          />
        </li>
      </ul>
    </div>
  );
};

export default ShopBar;
