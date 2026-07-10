import { GeoJSON } from "react-leaflet";

// Leaflet's renderer sets these as raw SVG/canvas attributes, not CSS --
// CSS custom properties (var(--x)) don't reliably resolve there, so we
// resolve literal values here based on the active theme instead.
const PALETTE = {
  light: { border: "#c9c9c9", surface: "#ffffff", surfaceAlt: "#e4e4e4" },
  dark: { border: "#3d3d3d", surface: "#1f1f1f", surfaceAlt: "#2b2b2b" },
};

/**
 * Static geometry -- a different concern from CrimePin's dynamic,
 * filtered data. Clicking a shape reports the borough name up to
 * MapView, which is what triggers the pin fetch.
 */
export default function BoroughLayer({ data, selectedBorough, onSelect, theme }) {
  const colors = PALETTE[theme] || PALETTE.light;

  const styleFeature = (feature) => {
    const isSelected = feature.properties.boro_name === selectedBorough;
    return {
      color: colors.border,
      weight: isSelected ? 2 : 1,
      fillColor: isSelected ? colors.surfaceAlt : colors.surface,
      fillOpacity: isSelected ? 0.6 : 0.3,
    };
  };

  const onEachFeature = (feature, layer) => {
    layer.on({
      click: () => onSelect(feature.properties.boro_name),
      mouseover: (e) => e.target.setStyle({ fillOpacity: 0.5 }),
      mouseout: (e) => e.target.setStyle(styleFeature(feature)),
    });
  };

  return (
    <GeoJSON
      data={data}
      style={styleFeature}
      onEachFeature={onEachFeature}
      // Force re-render when selection or theme changes so styleFeature re-runs
      key={`${selectedBorough || "none"}-${theme}`}
    />
  );
}
