import { CircleMarker, Tooltip } from "react-leaflet";

// Same reasoning as BoroughLayer: literal colors, not CSS vars, since
// Leaflet's renderer won't resolve custom properties reliably.
const PIN_COLORS = {
  light: { FELONY: "#141414", MISDEMEANOR: "#7a7a7a", VIOLATION: "#a3a3a3" },
  dark: { FELONY: "#f2f2f2", MISDEMEANOR: "#8c8c8c", VIOLATION: "#5c5c5c" },
};

export default function CrimePin({ crime, theme, onClick }) {
  const palette = PIN_COLORS[theme] || PIN_COLORS.light;
  const color = palette[crime.law_cat_cd] || palette.MISDEMEANOR;

  return (
    <CircleMarker
      center={[crime.latitude, crime.longitude]}
      radius={6}
      pathOptions={{ color, fillColor: color, fillOpacity: 0.85, weight: 1 }}
      eventHandlers={{ click: () => onClick(crime.cmplnt_num) }}
    >
      <Tooltip direction="top" offset={[0, -6]}>
        {crime.ofns_desc}
      </Tooltip>
    </CircleMarker>
  );
}
