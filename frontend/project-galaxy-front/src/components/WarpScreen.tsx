import React, {useEffect, useState} from "react";
import "../styles/WarpSelectionMenu.css";
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

interface WarpSelectionProps {
  onClose: () => void;
  setWarpSetUp: (planetName: string) => void;
  planetNumber: number;
  updateStructRenderType: () => void;
  rerender: () => void;
  building_x: number;
  building_y: number;
  settlement_nr: number;
}

const WarpSelection: React.FC<WarpSelectionProps> = ({
    onClose,
    planetNumber,
    setWarpSetUp,
    updateStructRenderType,
    rerender,
    building_x,
    building_y,
    settlement_nr,
}) => {
    // List of linkable planets
    const [LinkablePlanets, setLinkablePlanets] =
        useState([])

    // Loads all the warp locations
    useEffect(() => {
    (async () => {
      const response = await axios.get(`${API_URL}/building/warper`, {
      params: {
        "planet_number": planetNumber,
        "settlement_number": settlement_nr,
        "pos_x": building_x,
        "pos_y": building_y
      },

      withCredentials: true });
      // Set the linkable planets
      setLinkablePlanets(response.data["linkable_planets"]);

      // Set up a planet link if it is linked
      if (response.data["warp_to"]){
          setWarpSetUp(response.data["warp_to"]);
          updateStructRenderType();
      }
    })();
  }, [rerender]);


const handleWarpSelectionClick = (
    planetName: string,
    planet_to_x: number,
    planet_to_y: number,

) => {
    /**
     * Handles when a warp location is selected
     */
    (async () => {
      const response = await axios.post(`${API_URL}/building/warper/change_warp_link`, {
      params: {
          "planet_number": planetNumber,
          "settlement_number": settlement_nr,
          "pos_x": building_x,
          "pos_y": building_y,
          "planet_to_x": planet_to_x,
          "planet_to_y": planet_to_y
      }},{withCredentials: true});
      if (response.data === "Link successfully created"){
          setWarpSetUp(planetName);
          updateStructRenderType();
      }
    })();
    onClose();
  };


  return (
    <div className="soldier-selection-window">
      <button className="close-button2" onClick={onClose}>x</button>
      <h2>Possible planets to link to</h2>
      {/* Replace the placeholder <ul> with the List component */}
      <div className="list-container">
      <ul className="warp_items_list">
        {LinkablePlanets.map((item, index) => (
            <button className="warp" key={index}
            onClick={() => handleWarpSelectionClick(
                item["planet_name"],
                item["coordinates"]["planet_x"],
                item["coordinates"]["planet_y"]
            )}
            >
                <h3 className={"warp"}>{item["planet_name"]}</h3>
                <h4 className={"warp"}>{item["user_name"]}</h4>
                <div>x: {item["coordinates"]["planet_x"]} y: {item["coordinates"]["planet_y"]}</div>
            </button>
        ))}
      </ul>
      </div>

    </div>
  );
};

export default WarpSelection;
