import { useEffect, useState } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import BoroughLayer from "./BoroughLayer";
import CrimePin from "./CrimePin";
import { getCrimePins } from "../api/client";

const NYC_CENTER = [40.7128, -74.006];
const BOROUGH_CENTERS = {
  Manhattan: [40.776, -73.971],
  Brooklyn: [40.65, -73.95],
  Queens: [40.742, -73.79],
  "The Bronx": [40.85, -73.87],
  "Staten Island": [40.579, -74.15],
};

// Tile URLs matching each theme, so the base map itself goes dark, not
// just the UI chrome around it -- otherwise dark mode would have a
// bright map glowing in the middle of an otherwise dark interface.
const TILE_URLS = {
  light: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
  dark: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
};

function FlyToBorough({ borough }) {
  const map = useMap();
  useEffect(() => {
    if (borough && BOROUGH_CENTERS[borough]) {
      map.flyTo(BOROUGH_CENTERS[borough], 12, { duration: 0.8 });
    } else {
      map.flyTo(NYC_CENTER, 10, { duration: 0.8 });
    }
  }, [borough, map]);
  return null;
}

export default function MapView({ theme, selectedBorough, onSelectBorough, timeRange, selectedOffense, onSelectCrime }) {
  const [boroughShapes, setBoroughShapes] = useState(null);
  const [pins, setPins] = useState([]);

  useEffect(() => {
    fetch("/borough-boundaries.geojson")
      .then((r) => r.json())
      .then(setBoroughShapes);
  }, []);

  useEffect(() => {
    if (!selectedBorough) {
      setPins([]);
      return;
    }
    getCrimePins(selectedBorough.toUpperCase(), timeRange, selectedOffense)
      .then(setPins)
      .catch(() => setPins([]));
  }, [selectedBorough, timeRange, selectedOffense]);

  return (
    <MapContainer center={NYC_CENTER} zoom={10} style={{ height: "100%", width: "100%" }}>
      <TileLayer
        url={TILE_URLS[theme] || TILE_URLS.light}
        attribution='&copy; OpenStreetMap contributors &copy; CARTO'
      />
      <FlyToBorough borough={selectedBorough} />

      {boroughShapes && (
        <BoroughLayer
          data={boroughShapes}
          selectedBorough={selectedBorough}
          onSelect={onSelectBorough}
          theme={theme}
        />
      )}

      {pins.map((crime) => (
        <CrimePin key={crime.cmplnt_num} crime={crime} theme={theme} onClick={onSelectCrime} />
      ))}
    </MapContainer>
  );
}
